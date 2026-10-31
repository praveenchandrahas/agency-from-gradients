"""The S11 ledger world. Units: mass in Msun, energy in Msun c^2, time in yr, entropy in k_B.

Two compartments (index 0 = unreached U, 1 = reached R). Baseline physics acts in both;
levers act in R only. R grows as the agent's probe cone expands (see cosmology.reach_fractions).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np

from . import cosmology as cs
from .constants import (EJ, HAWKING_K, HAWKING_RATIO, K1, KB, MSUN, NB_PER_MSUN, S_BH_COEF, S_CEH, S_OBS_EL,
                        SIGMA_SB, T_CMB0, THAWK_MSUN, YR, LSUN, C, OB, H0, G)

import math

B = 80                                   # black hole mass bins, M_j = 2 * 2^j Msun (up to ~1e24)
BIN_LOG2 = np.arange(B)
LEVERS = ["star_formation", "funnel_gas", "merge_holes", "collapse_remnants", "collectors"]

# stellar classes: mass fraction of formed mass, lifetime (yr), fuel fraction burned, T_eff (K)
ST_FRAC = np.array([0.20, 0.30, 0.20, 0.15, 0.15])
ST_TAU = np.array([3e12, 6e10, 6e9, 4.4e8, 5e6])
ST_FBURN = np.array([0.9, 0.3, 0.1, 0.1, 0.1])
ST_TEFF = np.array([3500., 4500., 6000., 12000., 30000.])
NU_FRAC = 0.0068                         # neutrino energy per unit mass of a core-collapse progenitor
ST_RAD = ST_FBURN * 0.007 + np.array([0, 0, 0, 0, NU_FRAC])      # radiated fraction of dying mass
WD_FRAC = np.array([0.99, 0.90, 0.50, 0.17, 0.0])
NS_FRAC = np.array([0, 0, 0, 0, 0.044])
BH_FRAC = np.array([0, 0, 0, 0, 0.064])
BH_MEAN_MASS = 8.0
MATTER_S = dict(igm=20.0, gas=10.0, star=20.0, wd=0.5, ns=0.2, col=0.1)   # k_B per baryon (negligible, reported)


@dataclass
class Params:
    horizon_yr: float = 1e14
    per_decade: int = 30
    v_probe: float = 0.5
    chi0_gly: float = 0.1
    eta: float = 0.1                    # radiative efficiency of accretion
    eps_gw: float = 0.05                # mass fraction radiated as GW in a merger
    eps_col: float = 0.05               # energy released collapsing a remnant to a hole
    bh_mult: float = 1.0                # multiplies the BH entropy coefficient
    cost_mult: float = 1.0
    reach_limit: bool = True            # False: all matter reachable from the start
    domain_mass: float = 1.5e14         # baryon mass of a bound domain (Msun); 0 or inf = no domain limit
    area_limit: bool = True             # radiators limited by collector area
    levers_on: tuple = (1, 1, 1, 1, 1)
    hawking: bool = False
    capture_accretion: bool = True      # collectors can harvest accretion light
    enforce_cap: bool = True
    s_smbh0: float = S_OBS_EL
    tau_sf: float = 2.5e9
    tau_acc0: float = 40e9
    tau_b: float = 1e8
    tau_m: float = 1e9                  # pair merge delay per generation
    tau_d: float = 1e9
    tau_build: float = 1e8
    sf_boost: float = 10.0
    cost_a: float = 1e-6
    cost_b: float = 1e-4
    cost_c: float = 1e-4
    cost_d: float = 1e-3
    cost_e: float = 1e-6
    col_mass_per_lsun: float = 2e-7     # Msun of collector per Lsun intercepted (Mercury-scale swarm)
    rho_area: float = 1.0               # kg/m^2 of radiator
    xi_max: float = 0.3                 # work extraction efficiency ceiling
    w0: float = 1e-3                    # seed work reservoir (Msun c^2): one stellar lifetime of energy
    f_dust: float = 0.3
    t_dust: float = 20.0
    t_acc: float = 1e5
    t_waste0: float = 100.0

    def draw(self, seed: int) -> "Params":
        """Parameter-uncertainty draw for seed >= 0 (seed -1: nominal)."""
        if seed < 0:
            return self
        r = np.random.default_rng(10_000_019 + seed)
        return replace(self,
                       s_smbh0=self.s_smbh0 * float(np.exp(r.normal(0, 0.5))),
                       tau_sf=self.tau_sf * float(np.exp(r.normal(0, 0.3))),
                       eta=float(np.exp(r.uniform(np.log(0.06), np.log(0.3)))) if self.eta == 0.1 else self.eta,
                       eps_gw=float(r.uniform(0.02, 0.10)) if self.eps_gw == 0.05 else self.eps_gw,
                       domain_mass=(float(np.exp(r.uniform(np.log(3e13), np.log(5e14)))) if self.domain_mass == 1.5e14
                                    else self.domain_mass))


def bin_index(mean_mass):
    return np.clip(np.rint(np.log2(np.maximum(mean_mass, 1e-30) / 2.0)), 0, B - 1).astype(int)


BIN_MASS = 2.0 * 2.0 ** BIN_LOG2


def smbh_initial(s_target, m_total, mc=3e9):
    """Schechter-like SMBH number function, solved so sum(M^2)*coef = s_target and sum(M) = m_total."""
    lo, hi = 17, 40                      # bins from ~2.6e5 Msun upward
    M = BIN_MASS[lo:hi]
    target_ratio = s_target / S_BH_COEF / m_total   # sum M^2 / sum M
    best = None
    for gam in np.linspace(-1.0, 1.8, 281):
        n = M ** (-gam) * np.exp(-M / mc)
        ratio = (n * M ** 2).sum() / (n * M).sum()
        if best is None or abs(np.log(ratio / target_ratio)) < best[0]:
            best = (abs(np.log(ratio / target_ratio)), gam, n)
    n = best[2]
    n = n * m_total / (n * M).sum()
    hn = np.zeros(B)
    hm = np.zeros(B)
    hs = np.zeros(B)
    hn[lo:hi], hm[lo:hi], hs[lo:hi] = n, n * M, n * M ** 2
    return hn, hm, hs


class Cosmos:
    """One universe. step(u) advances one log-time step with lever shares u (len 5)."""

    def __init__(self, p: Params):
        self.p = p
        self.grid = cs.time_grid(p.horizon_yr, p.per_decade)
        self.F = cs.reach_fractions(self.grid, p.v_probe, p.chi0_gly) if p.reach_limit else np.ones(len(self.grid))
        self.Tenv = cs.t_env(self.grid)
        self.logt = np.log(self.grid)
        self.i = 0
        n_b = OB * 3 * H0 ** 2 / (8 * math.pi * G) * (4 / 3) * math.pi * (cs.CHI_OBS_GLY * 9.4607e24) ** 3 / MSUN
        self.N = n_b                                          # baryon mass of the observable universe, Msun
        N = self.N
        C0 = 0.09 * N                                         # cumulative stellar mass formed by now
        G0 = 0.012 * N
        sfr0 = G0 / p.tau_sf
        st = np.zeros(5)
        st[0] = ST_FRAC[0] * C0
        st[1] = ST_FRAC[1] * C0
        st[2] = ST_FRAC[2] * C0 * 0.5
        st[3] = ST_FRAC[3] * sfr0 * ST_TAU[3]
        st[4] = ST_FRAC[4] * sfr0 * ST_TAU[4]
        dead = np.array([0, 0, ST_FRAC[2] * C0 * 0.5, ST_FRAC[3] * (C0 - sfr0 * ST_TAU[3]), ST_FRAC[4] * (C0 - sfr0 * ST_TAU[4])])
        wd0 = float((dead * WD_FRAC).sum())
        ns0 = float((dead * NS_FRAC).sum())
        bh_m0 = float((dead * BH_FRAC).sum())
        hn1 = np.zeros(B); hm1 = np.zeros(B); hs1 = np.zeros(B)
        j = int(bin_index(BH_MEAN_MASS))
        hn1[j] = bh_m0 / BH_MEAN_MASS; hm1[j] = bh_m0; hs1[j] = hn1[j] * BH_MEAN_MASS ** 2
        smbh_m = 4.8e18 * N / 7.5e22 * 0 + 4.8e18               # SMBH mass density ~4e5 Msun/Mpc^3 over the volume
        hn2, hm2, hs2 = smbh_initial(p.s_smbh0, smbh_m)
        hn_t, hm_t, hs_t = hn1 + hn2, hm1 + hm2, hs1 + hs2
        rad_so_far = float((ST_RAD * dead).sum())
        # baryon closure: IGM takes the remainder
        igm = N - G0 - st.sum() - wd0 - ns0 - hm_t.sum() - rad_so_far
        self.fusion_defect = rad_so_far
        f = 1e-12
        self.G = np.array([G0 * (1 - f), G0 * f]) if False else np.array([G0, 0.0])
        # build as total then split by tiny initial R fraction
        self.R0 = float(self.F[0])
        sp = np.array([1 - self.R0, self.R0])
        self.G = G0 * sp
        self.I = igm * sp
        self.st = np.outer(sp, st)
        self.wd = wd0 * sp
        self.ns = ns0 * sp
        self.col = np.zeros(2)
        self.hn = np.outer(sp, hn_t); self.hm = np.outer(sp, hm_t); self.hs = np.outer(sp, hs_t)
        self.kappa = 0.0
        self.W = p.w0
        self.Eout = 0.0
        self.bar_in_bh = float(hm_t.sum())
        self.bar_evap = 0.0
        self.S_ph = 0.0
        self.S_hawk = 0.0
        self.G0 = G0
        self.spent = np.zeros(5)
        self.hist = []
        # initial ledgers
        self.E0 = self.energy_total()
        self.B0 = self.baryon_total()
        self.cap_hit = False
        self.S_ph = self._initial_photon_entropy(dead)

    # ---- ledgers -------------------------------------------------------------------------
    def nonbh(self):
        return float(self.G.sum() + self.I.sum() + self.st.sum() + self.wd.sum() + self.ns.sum() + self.col.sum())

    def energy_total(self):
        return self.nonbh() + float(self.hm.sum()) + self.W + self.Eout

    def baryon_total(self):
        return self.nonbh() + self.fusion_defect + self.bar_in_bh + self.bar_evap

    def ledger_errors(self):
        e = abs(self.energy_total() - self.E0) / self.E0
        b = abs(self.baryon_total() - self.B0) / self.B0
        return e, b

    # ---- entropy -------------------------------------------------------------------------
    def _initial_photon_entropy(self, dead):
        """Starlight already emitted before 'now' (same baseline for every strategy: cancels in gains)."""
        e = dead * ST_RAD
        s = (4 / 3) * K1 * (e / ST_TEFF).sum()
        self.Eout = float(e.sum())
        self.E0 = self.energy_total()   # include the radiation already emitted so the ledger starts closed
        return float(s)

    def s_bh(self):
        return S_BH_COEF * self.p.bh_mult * float(self.hs.sum())

    def s_matter(self):
        nb = NB_PER_MSUN
        return nb * (MATTER_S["igm"] * self.I.sum() + MATTER_S["gas"] * self.G.sum() + MATTER_S["star"] * self.st.sum()
                     + MATTER_S["wd"] * self.wd.sum() + MATTER_S["ns"] * self.ns.sum() + MATTER_S["col"] * self.col.sum())

    def s_cmb(self):
        return 1480.0 * 4 / 3 * math.pi * (cs.CHI_OBS_GLY * 9.4607e26) ** 3     # k_B/cm^3 x cm^3

    def entropy(self):
        sb, sm, sp, sh, sc = self.s_bh(), self.s_matter(), self.S_ph, self.S_hawk, self.s_cmb()
        return dict(bh=sb, matter=sm, photon=sp, hawking=sh, cmb=sc, total=sb + sm + sp + sh + sc)

    # ---- helpers -------------------------------------------------------------------------
    def _rebin(self):
        n, m, s = self.hn, self.hm, self.hs
        nn = np.zeros_like(n); mm = np.zeros_like(m); ss = np.zeros_like(s)
        for c in (0, 1):
            ok = n[c] > 1e-300
            idx = np.zeros(B, int)
            idx[ok] = bin_index(m[c][ok] / n[c][ok])
            np.add.at(nn[c], idx[ok], n[c][ok]); np.add.at(mm[c], idx[ok], m[c][ok]); np.add.at(ss[c], idx[ok], s[c][ok])
        self.hn, self.hm, self.hs = nn, mm, ss

    def _add_holes(self, c, count, mass, meanmass):
        j = int(bin_index(meanmass))
        self.hn[c, j] += count; self.hm[c, j] += mass; self.hs[c, j] += count * meanmass ** 2

    def power_R(self):
        """Stellar power in R in Msun c^2 / yr."""
        return float((ST_FBURN * 0.007 / ST_TAU * self.st[1]).sum())

    # ---- one step --------------------------------------------------------------------------
    def features(self):
        N = self.N
        return np.array([
            (self.logt[self.i] - self.logt[0]) / (self.logt[-1] - self.logt[0]),
            self.F[self.i],
            self.G.sum() / N * 30, self.st.sum() / N * 10, (self.wd.sum() + self.ns.sum()) / N * 10,
            np.log10(max(self.hs.sum() * S_BH_COEF, 1.0)) / 120.0,
            self.kappa, np.log10(max(self.W, 1e-30)) / 30.0 + 1.0,
            self.hm[1].sum() / max(self.hm.sum(), 1e-30),
            1.0 - min(1.0, self.hn[1].sum() / max(self.hn.sum(), 1e-30) * 0 + 0.0),
        ])

    def step(self, u):
        p = self.p
        i = self.i
        t0, t1 = self.grid[i], self.grid[i + 1]
        dt = t1 - t0
        u = np.asarray(u, float) * np.asarray(p.levers_on, float)
        # 1. reach growth: move a fraction of U into R
        Fo, Fn = self.F[i], self.F[i + 1]
        tf = 0.0 if Fo >= 1.0 else (Fn - Fo) / (1.0 - Fo)
        if tf > 0:
            # mix collectors (diluted by luminosity)
            pR = max(self.power_R(), 1e-300)
            pU_moved = float((ST_FBURN * 0.007 / ST_TAU * self.st[0]).sum()) * tf
            self.kappa *= pR / (pR + pU_moved)
            for arr in (self.G, self.I, self.wd, self.ns, self.hn, self.hm, self.hs):
                mv = arr[0] * tf
                arr[0] -= mv; arr[1] += mv
            self.st[1] += self.st[0] * tf; self.st[0] *= (1 - tf)
        # 2. requests from lever shares (R only)
        cm = p.cost_mult
        free = self.G[1]
        # (a) star formation boost
        rate_mult = 1.0 + (p.sf_boost - 1.0) * u[0]
        pa = 1 - math.exp(-dt * rate_mult / p.tau_sf)
        p0 = 1 - math.exp(-dt / p.tau_sf)
        dm_a_req = free * max(pa - p0, 0.0)
        # (b) funnel
        dm_b_req = free * u[1] * (1 - math.exp(-dt / p.tau_b))
        # (c) mergers
        n_holes_R = float(self.hn[1].sum())
        floor = (float(self.hm[1].sum() + self.G[1] + self.I[1] + self.st[1].sum() + self.wd[1] + self.ns[1])
                 / p.domain_mass) if (p.domain_mass and np.isfinite(p.domain_mass)) else 0.0
        avail = max(0.0, 1.0 - floor / max(n_holes_R, 1e-300))
        phi = u[2] * avail * (1 - math.exp(-dt / p.tau_m))
        capm = p.domain_mass if (p.domain_mass and np.isfinite(p.domain_mass)) else self.N
        nzh = self.hn[1] > 1e-300
        mu_R = np.zeros(B); mu_R[nzh] = self.hm[1][nzh] / self.hn[1][nzh]
        mmask = (nzh & (2 * (1 - p.eps_gw) * mu_R <= capm)).astype(float)   # a merged pair must still fit in one domain
        merged_mass_req = phi * float((mmask * self.hm[1]).sum())
        # (d) collapse
        qd = u[3] * (1 - math.exp(-dt / p.tau_d))
        dm_d_req = qd * float(self.wd[1] + self.ns[1])
        # (e) collectors
        P_R = self.power_R()
        dk_req = u[4] * (1 - self.kappa) * (1 - math.exp(-dt / p.tau_build))
        col_req = p.col_mass_per_lsun * (P_R * EJ / YR / LSUN) * dk_req
        cost = cm * (p.cost_a * dm_a_req + p.cost_b * dm_b_req + p.cost_c * merged_mass_req + p.cost_d * dm_d_req
                     + p.cost_e * col_req)
        s = 1.0 if cost <= 0 else min(1.0, self.W / cost)
        s = max(s, 0.0)
        spent = cost * s
        self.W -= spent
        waste_heat = spent
        # ---- baseline + levers ----------------------------------------------------------------
        dEout = 0.0                       # energy radiated this step (Msun c^2)
        S_new = 0.0
        # star formation (both compartments)
        mult = np.array([1.0, 1.0 + (p.sf_boost - 1.0) * u[0] * s])
        pf = 1 - np.exp(-dt * mult / p.tau_sf)
        form = self.G * pf
        extra_a = float(form[1] - self.G[1] * p0)
        self.G -= form
        self.st += np.outer(form, ST_FRAC)
        # gas cooling from the IGM
        tau_acc = p.tau_acc0 * (t0 / cs.T0_YR)
        cool = self.I * (1 - math.exp(-dt / tau_acc))
        self.I -= cool; self.G += cool
        # lever (b): funnel R gas into holes
        dm_b = min(dm_b_req * s, self.G[1])
        acc_light = 0.0
        if dm_b > 0:
            w = self.hs[1] / max(self.hs[1].sum(), 1e-300)
            dm_j = dm_b * w
            eddcap = self.hm[1] * np.expm1(min(dt * (1 - p.eta) / (p.eta * 0.45e9), 600.0)) / (1 - p.eta)
            dm_j = np.minimum(dm_j, eddcap)
            capm = p.domain_mass if (p.domain_mass and np.isfinite(p.domain_mass)) else self.N
            nzb = self.hn[1] > 1e-300
            room = np.zeros(B)
            room[nzb] = self.hn[1][nzb] * np.maximum(capm - self.hm[1][nzb] / self.hn[1][nzb], 0.0) / (1 - p.eta)
            dm_j = np.minimum(dm_j, room)
            dm_b = float(dm_j.sum())
            nz = self.hn[1] > 1e-300
            delta = np.zeros(B)
            delta[nz] = (1 - p.eta) * dm_j[nz] / self.hn[1][nz]
            self.hs[1] += 2 * self.hm[1] * delta + self.hn[1] * delta ** 2
            self.hm[1] += (1 - p.eta) * dm_j
            self.G[1] -= dm_b
            self.bar_in_bh += dm_b
            acc_light = p.eta * dm_b
            dEout += acc_light
        # star death
        dead = self.st * (1 - np.exp(-dt / ST_TAU))
        self.st -= dead
        rad = dead * ST_RAD
        star_E = (dead * ST_FBURN * 0.007)
        self.fusion_defect += float(rad.sum())
        self.wd += (dead * WD_FRAC).sum(axis=1)
        self.ns += (dead * NS_FRAC).sum(axis=1)
        bhm = (dead * BH_FRAC).sum(axis=1)
        gas_ret = (dead * (1 - WD_FRAC - NS_FRAC - BH_FRAC - ST_RAD)).sum(axis=1)
        self.G += gas_ret
        for c in (0, 1):
            if bhm[c] > 0:
                self._add_holes(c, bhm[c] / BH_MEAN_MASS, bhm[c], BH_MEAN_MASS)
        self.bar_in_bh += float(bhm.sum())
        dEout += float(rad.sum())
        # starlight entropy at emission, dust reprocessing, collector capture (R)
        s_emit = (4 / 3) * K1 * (rad / ST_TEFF)                       # per compartment x class
        S_new += float(s_emit.sum())
        gfrac = min(1.0, float(self.G.sum()) / self.G0)
        fd = p.f_dust * gfrac
        k = self.kappa
        # uncaptured energy per compartment: R uncaptured = (1-k)
        star_tot = rad.sum(axis=1)
        unc = np.array([star_tot[0], star_tot[1] * (1 - k)])
        S_new += (4 / 3) * K1 * fd * float(unc.sum()) * (1 / p.t_dust - 1 / 8000.0)
        cap_E = star_tot[1] * k
        cap_S_removed = float(s_emit[1].sum()) * k
        if p.capture_accretion:
            cap_E += acc_light * k
            cap_S_removed += (4 / 3) * K1 * acc_light * k / p.t_acc
        if acc_light > 0:
            S_new += (4 / 3) * K1 * acc_light / p.t_acc
            S_new += (4 / 3) * K1 * fd * acc_light * (1 - k if p.capture_accretion else 1.0) * (1 / p.t_dust - 1 / p.t_acc)
        # radiator temperature
        Tenv = self.Tenv[i + 1]
        col_mass_kg = self.col[1] * MSUN
        xi_c = 0.0
        # lever (e): build collectors (before capture this step uses old kappa; build adds for next)
        col_new = min(col_req * s, self.G[1])
        dk = dk_req * s * (col_new / col_req if col_req > 0 and col_new < col_req * s else 1.0)
        if col_new > 0:
            self.G[1] -= col_new; self.col[1] += col_new
        # work extraction from captured energy
        if cap_E > 0 and col_mass_kg > 0:
            P_heat = (cap_E + waste_heat) * EJ / (dt * YR)
            A = col_mass_kg / p.rho_area
            T_area = (P_heat / (SIGMA_SB * A)) ** 0.25 if p.area_limit else 0.0
            Tc = max(Tenv, T_area)
            xi_c = p.xi_max * (1 - min(1.0, Tc / 8000.0))
        else:
            Tc = max(Tenv, p.t_waste0 if (col_mass_kg <= 0) else Tenv)
            if col_mass_kg > 0 and waste_heat > 0:
                A = col_mass_kg / p.rho_area
                P_heat = waste_heat * EJ / (dt * YR)
                Tc = max(Tenv, (P_heat / (SIGMA_SB * A)) ** 0.25 if p.area_limit else 0.0)
        if cap_E > 0:
            stored = xi_c * cap_E
            self.W += stored
            dEout -= stored
            S_new += (4 / 3) * K1 * (cap_E - stored) / Tc - cap_S_removed
        if waste_heat > 0:
            S_new += (4 / 3) * K1 * waste_heat / Tc
        dEout += waste_heat
        self.kappa = min(1.0, self.kappa + dk)
        # lever (a) energy already counted in waste; mass flows handled via star formation above
        # lever (d): collapse remnants to holes
        dm_d = dm_d_req * s
        if dm_d > 0:
            tot = self.wd[1] + self.ns[1]
            fw, fn_ = self.wd[1] / tot, self.ns[1] / tot
            mw, mn = dm_d * fw, dm_d * fn_
            self.wd[1] -= mw; self.ns[1] -= mn
            for mass, obj in ((mw, 0.6), (mn, 1.4)):
                if mass > 0:
                    hm_ = mass * (1 - p.eps_col)
                    self._add_holes(1, mass / obj, hm_, obj * (1 - p.eps_col))
            self.bar_in_bh += dm_d
            erel = p.eps_col * dm_d
            dEout += erel
            S_new += (4 / 3) * K1 * erel / 1e10
        # lever (c): mergers within bound domains
        ph = phi * s * mmask
        if ph.any():
            n, m, ss_ = self.hn[1].copy(), self.hm[1].copy(), self.hs[1].copy()
            ok = (n > 1e-300) & (ph > 0)
            nout = np.zeros(B); mout = np.zeros(B); sout = np.zeros(B)
            nout[ok] = ph[ok] * n[ok] / 2
            mout[ok] = (1 - p.eps_gw) * ph[ok] * m[ok]
            sout[ok] = (1 - p.eps_gw) ** 2 * (ph[ok] * ss_[ok] + ph[ok] * m[ok] ** 2 / n[ok])
            self.hn[1] = n * (1 - ph); self.hm[1] = m * (1 - ph); self.hs[1] = ss_ * (1 - ph)
            dEout += p.eps_gw * float((ph * m).sum())
            tmpn, tmpm, tmps = self.hn[1].copy(), self.hm[1].copy(), self.hs[1].copy()
            idx = np.zeros(B, int)
            idx[ok] = bin_index(mout[ok] / np.maximum(nout[ok], 1e-300))
            np.add.at(tmpn, idx[ok], nout[ok]); np.add.at(tmpm, idx[ok], mout[ok]); np.add.at(tmps, idx[ok], sout[ok])
            self.hn[1], self.hm[1], self.hs[1] = tmpn, tmpm, tmps
        # Hawking evaporation (far horizon)
        if p.hawking:
            for c in (0, 1):
                n, m, ss_ = self.hn[c], self.hm[c], self.hs[c]
                ok = n > 1e-300
                if not ok.any():
                    continue
                mu = np.zeros(B); mu[ok] = m[ok] / n[ok]
                hot = ok & (THAWK_MSUN / np.maximum(mu, 1e-300) > Tenv)
                if not hot.any():
                    continue
                m3 = mu[hot] ** 3 - 3 * HAWKING_K * dt
                newmu = np.where(m3 > 0, np.maximum(m3, 0.0) ** (1 / 3), 0.0)
                dM = n[hot] * (mu[hot] - newmu)
                ratio = np.where(mu[hot] > 0, newmu / mu[hot], 0.0)
                ds = ss_[hot] * (1 - ratio ** 2)
                self.S_hawk += HAWKING_RATIO * S_BH_COEF * p.bh_mult * float(ds.sum())
                evb = float(dM.sum()) * self.bar_in_bh / max(float(self.hm.sum()), 1e-300)
                self.bar_in_bh -= evb; self.bar_evap += evb
                dEout += float(dM.sum())
                gone = newmu == 0
                nn_ = np.where(gone, 0.0, n[hot])
                n[hot] = nn_; m[hot] = nn_ * newmu; ss_[hot] = ss_[hot] * ratio ** 2
        self._rebin()
        self.Eout += dEout
        self.S_ph += S_new
        self.spent += np.array([p.cost_a * dm_a_req, p.cost_b * dm_b_req, p.cost_c * merged_mass_req, p.cost_d * dm_d_req,
                                p.cost_e * col_req]) * cm * s
        if p.enforce_cap and self.s_bh() > S_CEH:
            self.cap_hit = True
        self.i += 1
        return s

    def done(self):
        return self.i >= len(self.grid) - 1


def rollout(p: Params, policy, check_ledger=False, tol=1e-9, record=False):
    """Run to the horizon. policy(features, step_index, n_steps) -> 5 shares (sum <= 1)."""
    w = Cosmos(p)
    maxe = 0.0
    n = len(w.grid) - 1
    trace = []
    while not w.done():
        u = policy(w.features(), w.i, n)
        w.step(u)
        if check_ledger or record:
            e, b = w.ledger_errors()
            maxe = max(maxe, e, b)
        if record:
            trace.append((w.grid[w.i], np.asarray(u).copy(), w.s_bh(), w.kappa, w.W, w.F[w.i]))
    ent = w.entropy()
    out = dict(entropy=ent, max_ledger_err=maxe, cap_hit=w.cap_hit, kappa=w.kappa, spent=w.spent.copy(),
               hole_mass_R=float(w.hm[1].sum()), W_final=float(w.W), n_holes=float(w.hn.sum()))
    if record:
        out["trace"] = trace
    return out


def do_nothing(f, i, n):
    return np.zeros(5)
