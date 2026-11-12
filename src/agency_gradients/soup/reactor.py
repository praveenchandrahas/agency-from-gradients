"""S14 soup: a well-mixed flow reactor, simulated molecule by molecule.

Thermodynamics. Every reaction is reversible and its rates obey local detailed balance: the
forward attempt factor is min(1, exp(-dG)) and the backward one min(1, exp(+dG)), so their
ratio is exp(-dG). A catalyst multiplies both directions by the same factor. Nothing else is
imposed. In particular there is no entropy term anywhere in the dynamics.

Bookkeeping. With these rates the closed system has the equilibrium distribution
P_eq(n) ~ prod_s (c0 exp(-g_s))**n_s / n_s!. Let Phi(n) = -ln P_eq(n) + const
= sum_s [n_s (g_s - ln c0) + ln n_s!]. For any single reaction event n -> n',
ln[a_forward(n) / a_backward(n')] = Phi(n) - Phi(n'). So the entropy produced by the reactions
in a step (in k_B) is Phi(before) - Phi(after), a state function of the counts. It is recorded,
never used.

Integrator. Tau-leaping with the Cao-Gillespie-Petzold step bound, Poisson reaction counts,
binomial washout, and rejection of any step that would make a count negative (the step is
halved and redrawn), so every ledger is exact in integers. `step_exact` is the exact direct
method, used to check the leaping.
"""
from __future__ import annotations

import math

import numpy as np

from .chemistry import Chemistry, SoupParams

_LOGFACT = np.concatenate(([0.0], np.cumsum(np.log(np.arange(1, 65536, dtype=float)))))


def logfact(n: np.ndarray) -> np.ndarray:
    global _LOGFACT
    m = int(n.max()) if n.size else 0
    if m >= len(_LOGFACT):
        new = np.arange(len(_LOGFACT), 2 * m + 2, dtype=float)
        _LOGFACT = np.concatenate((_LOGFACT, _LOGFACT[-1] + np.cumsum(np.log(new))))
    return _LOGFACT[n]


class Reactor:
    def __init__(self, chem: Chemistry, prm: SoupParams, dmu: float, seed, *, flow: bool = True,
                 n0: np.ndarray | None = None, t0: float = 0.0, t_end: float | None = None,
                 flux_ep: bool = False, day_night: int = 0):
        self.chem, self.prm, self.dmu, self.flow = chem, prm, float(dmu), flow
        self.rng = np.random.default_rng(seed)
        S, R = chem.n_species, chem.n_sites
        self.S, self.R, self.iF, self.iW = S, R, chem.iF, chem.iW
        self.x, self.y, self.z = chem.x, chem.y, chem.z
        self.same = (chem.x == chem.y)
        self.same_idx = np.flatnonzero(self.same)
        self.same_x = chem.x[self.same_idx]
        self.idx3 = np.concatenate((chem.x, chem.y, chem.z))
        eps = chem.eps_site
        self.fp, self.bp = np.minimum(1.0, np.exp(-eps)), np.minimum(1.0, np.exp(eps))
        dgc = eps - self.dmu
        self.fc, self.bc = np.minimum(1.0, np.exp(-dgc)), np.minimum(1.0, np.exp(dgc))
        self.fl, self.bl = min(1.0, math.exp(self.dmu)), min(1.0, math.exp(-self.dmu))
        self.eps, self.dgc = eps, dgc
        g = chem.g.copy()
        g[self.iF], g[self.iW] = self.dmu, 0.0
        self.glin = g - math.log(prm.c0)
        self.ext_p = chem.ext_p if chem.ext_p is not None else 0.0
        self.ext_c = chem.ext_c if chem.ext_c is not None else 0.0
        self.lens = chem.lens.astype(float)
        self.lens3 = np.where(chem.lens >= 3, chem.lens, 0).astype(float)
        # Feed. At zero drive F and W are fed in their equilibrium ratio (1:1), so the feed
        # itself carries no free energy. At positive drive the feed is pure fuel.
        self.n_in = np.zeros(S)
        self.n_in[chem.index("a")] = self.n_in[chem.index("b")] = prm.n_mono
        if self.dmu > 0:
            self.n_in[self.iF] = prm.n_fuel
        else:
            self.n_in[self.iF] = self.n_in[self.iW] = prm.n_fuel / 2
        self.n = (np.rint(self.n_in).astype(np.int64) if n0 is None else np.asarray(n0, np.int64).copy())
        self.t = float(t0)
        self.t0 = float(t0)
        # Exploratory only: a day/night feed. Fuel arrives at twice the rate for half of each
        # period and not at all for the other half, so the mean is unchanged. The period is a
        # whole number of residence times, so the feed is constant within every step.
        self.day_night = int(day_night)
        self.fuel_mean = float(self.n_in[self.iF])
        self._set_feed(0)
        self.t_end = prm.t_end if t_end is None else float(t_end)
        self.flux_ep = flux_ep
        nb = int(math.ceil(self.t_end - self.t0 - 1e-9))
        self.bin = 0
        z = lambda: np.zeros(nb)
        self.series = dict(fuel_in=z(), fuel_out=z(), coupled=z(), leak=z(), sigma=z(), sigma_flux=z(),
                           mass=z(), mass3=z(), dt=z(), phi_flow=z())
        self.late_from = max(0, int(round(prm.t_late - self.t0)))
        self.nsum = np.zeros(S)
        self.late_dt = 0.0
        self.kp_net = np.zeros(R, np.int64)
        self.kc_net = np.zeros(R, np.int64)
        self.snapshot = None            # counts at t_late
        self.steps = self.rejects = 0
        self.mass_in = self.mass_out = 0
        self.phi0 = self.phi(self.n)
        self.n_start = self.n.copy()

    def _set_feed(self, b: int):
        if self.day_night:
            day = ((int(round(self.t0)) + b) % self.day_night) < self.day_night / 2
            self.n_in[self.iF] = 2.0 * self.fuel_mean if day else 0.0

    # ---- thermodynamic state function -------------------------------------------------
    def phi(self, n: np.ndarray) -> float:
        return float((self.glin * n).sum() + logfact(n).sum())

    # ---- propensities -----------------------------------------------------------------
    def _prefactors(self, n):
        c, prm = self.chem, self.prm
        catp = np.bincount(c.cp_rxn, weights=n[c.cp_spec], minlength=self.R) + self.ext_p
        catc = np.bincount(c.cc_rxn, weights=n[c.cc_spec], minlength=self.R) + self.ext_c
        k = prm.kappa0
        return k * (1.0 + prm.speedup * catp / prm.c0), k * (prm.eta + prm.speedup * catc / prm.c0)

    def propensities(self, n):
        c0 = self.prm.c0
        pp, pc = self._prefactors(n)
        hf = n[self.x] * (n[self.y] - self.same).astype(float)
        nz = n[self.z].astype(float)
        nF, nW = float(n[self.iF]), float(n[self.iW])
        afp, abp = pp * self.fp * hf / c0, pp * self.bp * nz
        afc, abc = pc * self.fc * hf * nF / (c0 * c0), pc * self.bc * nz * nW / c0
        alf, alb = self.prm.kappa_leak * self.fl * nF, self.prm.kappa_leak * self.bl * nW
        return afp, abp, afc, abc, alf, alb

    def _expected_ep_rate(self, n, afp, abp, afc, abc, alf, alb) -> float:
        """Expected entropy production rate from the fluxes: sum over channels of the
        propensity times ln[a(n) / a_reverse(n after the event)]. Independent of `phi`."""
        lc0 = math.log(self.prm.c0)
        nx, ny, nz = n[self.x].astype(float), n[self.y].astype(float), n[self.z].astype(float)
        nF, nW = float(n[self.iF]), float(n[self.iW])
        with np.errstate(divide="ignore", invalid="ignore"):
            lhf = np.log(nx * (ny - self.same))
            lhf_up = np.where(self.same, np.log((nx + 2) * (nx + 1)), np.log((nx + 1) * (ny + 1)))
            Af_p = -self.eps - lc0 + lhf - np.log(nz + 1)
            Ab_p = self.eps + lc0 + np.log(nz) - lhf_up
            Af_c = -self.dgc - lc0 + lhf + math.log(nF) if nF > 0 else np.zeros(self.R)
            Af_c = Af_c - np.log(nz + 1) - math.log(nW + 1)
            Ab_c = self.dgc + lc0 + np.log(nz) + (math.log(nW) if nW > 0 else 0.0) - lhf_up - math.log(nF + 1)
            tot = 0.0
            for a, A in ((afp, Af_p), (abp, Ab_p), (afc, Af_c), (abc, Ab_c)):
                m = a > 0
                tot += float((a[m] * A[m]).sum())
        if alf > 0:
            tot += alf * (self.dmu + math.log(nF) - math.log(nW + 1))
        if alb > 0:
            tot += alb * (-self.dmu + math.log(nW) - math.log(nF + 1))
        return tot

    # ---- one tau-leap step ------------------------------------------------------------
    def step(self):
        prm, n, S, R = self.prm, self.n, self.S, self.R
        afp, abp, afc, abc, alf, alb = self.propensities(n)
        jn = (afp - abp) + (afc - abc)
        gg = afp + abp + afc + abc
        jc, gc = float((afc - abc).sum()), float((afc + abc).sum())
        mu = np.bincount(self.idx3, weights=np.concatenate((-jn, -jn, jn)), minlength=S)
        var = np.bincount(self.idx3, weights=np.concatenate((gg, gg, gg)), minlength=S)
        if len(self.same_idx):
            np.add.at(var, self.same_x, 2.0 * gg[self.same_idx])
        mu[self.iF] -= jc + (alf - alb); mu[self.iW] += jc + (alf - alb)
        var[self.iF] += gc + alf + alb; var[self.iW] += gc + alf + alb
        if self.flow:
            mu += prm.dil * (self.n_in - n)
            var += prm.dil * (self.n_in + n)
        bound = np.maximum(prm.eps_tau * n, 1.0)
        with np.errstate(divide="ignore", invalid="ignore"):
            t1 = np.where(mu != 0, bound / np.abs(mu), np.inf).min()
            t2 = np.where(var > 0, bound * bound / var, np.inf).min()
        edge = self.t0 + self.bin + 1.0
        tau = min(t1, t2, prm.tau_max, edge - self.t, self.t_end - self.t)
        hit_edge = tau >= edge - self.t
        avec = np.concatenate((afp, abp, afc, abc, (alf, alb)))
        while True:
            K = self.rng.poisson(avec * tau)
            dp, dc = K[:R] - K[R:2 * R], K[2 * R:3 * R] - K[3 * R:4 * R]
            dj = dp + dc
            drx = np.rint(np.bincount(self.idx3, weights=np.concatenate((-dj, -dj, dj)), minlength=S)).astype(np.int64)
            sdc, dl = int(dc.sum()), int(K[4 * R] - K[4 * R + 1])
            drx[self.iF] -= sdc + dl; drx[self.iW] += sdc + dl
            n1 = n + drx
            if self.flow:
                out = self.rng.binomial(n, -math.expm1(-prm.dil * tau))
                inn = self.rng.poisson(prm.dil * self.n_in * tau)
                n1o = n1 - out
            else:
                out = inn = np.zeros(S, np.int64)
                n1o = n1
            if n1.min() >= 0 and n1o.min() >= 0:
                break
            tau *= 0.5
            hit_edge = False
            self.rejects += 1
        n2 = n1o + inn
        # books
        b = self.bin
        s = self.series
        ph0, ph1, ph2 = self.phi(n), self.phi(n1), self.phi(n2)
        s["sigma"][b] += ph0 - ph1
        s["phi_flow"][b] += ph2 - ph1
        if self.flux_ep:
            s["sigma_flux"][b] += tau * self._expected_ep_rate(n, afp, abp, afc, abc, alf, alb)
        s["fuel_in"][b] += inn[self.iF]; s["fuel_out"][b] += out[self.iF]
        s["coupled"][b] += sdc; s["leak"][b] += dl
        s["mass"][b] += tau * float((self.lens * n).sum())
        s["mass3"][b] += tau * float((self.lens3 * n).sum())
        s["dt"][b] += tau
        self.mass_in += int((self.chem.lens * inn).sum()); self.mass_out += int((self.chem.lens * out).sum())
        if b >= self.late_from:
            self.nsum += tau * n
            self.late_dt += tau
            self.kp_net += dp; self.kc_net += dc
        self.n = n2
        self.steps += 1
        if hit_edge:
            self.t = edge
            self.bin += 1
            self._set_feed(self.bin)
            if self.bin == self.late_from and self.snapshot is None:
                self.snapshot = self.n.copy()
        else:
            self.t += tau

    def run(self, max_steps: int = 50_000_000):
        if self.late_from == 0 and self.snapshot is None:
            self.snapshot = self.n.copy()
        while self.t < self.t_end - 1e-12:
            self.step()
            if self.steps >= max_steps:
                raise RuntimeError("step budget exceeded")
        return self

    # ---- exact direct method (for checking) ---------------------------------------------
    def step_exact(self):
        prm, n, R, S = self.prm, self.n, self.R, self.S
        afp, abp, afc, abc, alf, alb = self.propensities(n)
        flow_in = prm.dil * self.n_in if self.flow else np.zeros(S)
        flow_out = prm.dil * n.astype(float) if self.flow else np.zeros(S)
        a = np.concatenate((afp, abp, afc, abc, (alf, alb), flow_in, flow_out))
        cs = np.cumsum(a)
        tot = cs[-1]
        if tot <= 0:
            self.t = self.t_end
            return
        tau = self.rng.exponential(1.0 / tot)
        if self.t + tau > self.t_end:
            self.t = self.t_end
            return
        j = int(np.searchsorted(cs, self.rng.random() * tot, side="right"))
        n1 = n.copy()
        rx = True
        if j < 4 * R:
            kind, r = divmod(j, R)
            sgn = 1 if kind in (0, 2) else -1
            n1[self.x[r]] -= sgn; n1[self.y[r]] -= sgn; n1[self.z[r]] += sgn
            if kind >= 2:
                n1[self.iF] -= sgn; n1[self.iW] += sgn
        elif j < 4 * R + 2:
            sgn = 1 if j == 4 * R else -1
            n1[self.iF] -= sgn; n1[self.iW] += sgn
        elif j < 4 * R + 2 + S:
            n1[j - 4 * R - 2] += 1; rx = False
        else:
            n1[j - 4 * R - 2 - S] -= 1; rx = False
        assert n1.min() >= 0
        b = min(int(self.t - self.t0), len(self.series["dt"]) - 1)
        if rx:
            self.series["sigma"][b] += self.phi(n) - self.phi(n1)
        else:
            self.series["phi_flow"][b] += self.phi(n1) - self.phi(n)
        self.series["mass"][b] += tau * float((self.lens * n).sum())
        self.series["mass3"][b] += tau * float((self.lens3 * n).sum())
        self.series["dt"][b] += tau
        if self.t >= prm.t_late:
            self.nsum += tau * n; self.late_dt += tau
        self.n = n1
        self.t += tau
        self.steps += 1

    def run_exact(self, max_steps: int = 50_000_000):
        while self.t < self.t_end and self.steps < max_steps:
            self.step_exact()
        return self

    # ---- summaries --------------------------------------------------------------------
    def window(self, lo: int, hi: int) -> dict:
        """Totals over bins [lo, hi) (bins are one residence time wide)."""
        s = {k: float(v[lo:hi].sum()) for k, v in self.series.items()}
        dt = max(s["dt"], 1e-12)
        return dict(capture=s["coupled"] / max(s["fuel_in"], 1.0), sigma_rate=s["sigma"] / dt,
                    sigma_flux_rate=s["sigma_flux"] / dt, poly_frac=s["mass3"] / max(s["mass"], 1e-12),
                    fuel_in=s["fuel_in"], coupled=s["coupled"], leak=s["leak"], fuel_out=s["fuel_out"], dt=dt)

    def late(self) -> dict:
        return self.window(self.late_from, len(self.series["dt"]))

    def poly_frac_series(self) -> np.ndarray:
        return self.series["mass3"] / np.maximum(self.series["mass"], 1e-12)

    def mean_late_counts(self) -> np.ndarray:
        return self.nsum / max(self.late_dt, 1e-12)

    def ledger_residuals(self) -> dict:
        """Every book must close. Mass and fuel are exact integers; Phi is a float identity."""
        s = self.series
        mass_now, mass_then = int((self.chem.lens * self.n).sum()), int((self.chem.lens * self.n_start).sum())
        fw_now = int(self.n[self.iF] + self.n[self.iW]); fw_then = int(self.n_start[self.iF] + self.n_start[self.iW])
        f_now, f_then = int(self.n[self.iF]), int(self.n_start[self.iF])
        fuel = f_then + s["fuel_in"].sum() - s["fuel_out"].sum() - s["coupled"].sum() - s["leak"].sum() - f_now
        phi = (self.phi(self.n) - self.phi0) - (s["phi_flow"].sum() - s["sigma"].sum())
        scale = max(abs(s["phi_flow"].sum()), abs(s["sigma"].sum()), abs(self.phi0), 1.0)
        return dict(mass=mass_then + self.mass_in - self.mass_out - mass_now, fuel=float(fuel),
                    phi_rel=float(abs(phi) / scale), fw_closed=(fw_now - fw_then) if not self.flow else 0)
