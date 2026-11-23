"""Locks world: a flow reactor with locked free-energy gradients, and structures that may open them.

Fuel F_i arrives in a flow reactor and either reacts to waste W_i or washes out unspent.
Each reaction F_i <-> W_i drops free energy by dmu0_i (units of kT) at standard
concentration. Its uncatalysed rate is k0 * exp(-B_i). B is the dial: how locked the
gradient is.

Catalysts carry a key: a bit string. Lock i has a target key. A catalyst offers its own
route through lock i with barrier b_cat + lam * d, where d is the Hamming distance between
its key and the lock's key. A catalyst speeds the forward and backward reaction by the same
factor, so it can never move the equilibrium.

Every reaction obeys local detailed balance: J+/J- = exp(A), with A the affinity in kT.
Entropy production is measured from the free-energy books. It is never rewarded and never
imposed. Nothing in the code refers to entropy when deciding who lives.

Arms (see SPEC.md):
    N  no catalysts. The passive counterfactual.
    M  fixed catalysts with random keys, fixed number, no growth. A natural mineral.
    D  catalysts that grow on the free energy their reaction releases. Keys copied without error.
    L  as D, but keys are inherited with mutation.
    U  fixed catalysts carrying the lock's own key, re-keyed if the lock drifts. A designer bound.

The books, closed and checked every step:
    fuel:   in - out = change in (F + W)                 for each lock
    energy: released = heat + change in stored          (released = free energy lost by reactions)
    heat  = released directly + upkeep paid + stored energy of the dead
Entropy produced, in k_B, has two parts:
    reaction: heat (kT), free energy degraded at the bath temperature
    mixing:   feed entering the reactor at a different composition (see mix_sigma)
The headline is their sum. Counting reactions alone penalises a good catalyst: it drives the
fuel toward equilibrium, so each reaction releases less, and the loss shows up as mixing.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, replace
import math
import numpy as np

ARMS = ("N", "M", "D", "L", "U")


@dataclass(frozen=True)
class Config:
    arm: str = "L"
    # locks (tuples, one entry per lock)
    dmu0: tuple = (6.0,)          # standard free-energy drop of F -> W, kT
    B: tuple = (8.0,)             # barrier of the uncatalysed route, kT
    f_in: tuple = (200.0,)        # feed level of fuel
    w_in: float = 1.0             # feed level of waste (keeps logarithms finite)
    k0: float = 100.0             # attempt rate, per residence time
    dil: float = 1.0              # dilution rate; time is in residence times
    # catalysis
    n_bits: int = 24              # key length
    b_cat: float = 0.0            # barrier of a perfect catalytic route, kT
    lam: float = 0.5              # extra barrier per mismatched bit, kT
    vol: float = 1000.0           # turns a count of catalysts into a concentration
    # growing catalysts (D and L)
    n0: int = 100                 # starting number
    e0: float = 10.0              # starting stored free energy each, kT
    eta: float = 0.5              # share of a catalyst's released free energy it can store
    e_div: float = 20.0           # stored free energy at which it splits in two
    c_up: float = 0.5             # upkeep, kT per residence time
    hazard: float = 0.01          # death rate from all other causes
    mu: float = 0.002             # per-bit mutation probability per division (L only)
    init: str = "random"          # "random" or "perfect" (positive control)
    # fixed catalysts (M and U)
    n_fixed: int = 0
    # lock drift
    drift: float = 0.0            # bit flips of each lock's key, per residence time
    # numerics
    dt: float = 0.01

    def with_(self, **kw) -> "Config":
        return replace(self, **kw)


def popcount(x: np.ndarray) -> np.ndarray:
    return np.bitwise_count(x).astype(np.int64)


def g_fn(F: np.ndarray, W: np.ndarray, dmu0: np.ndarray) -> np.ndarray:
    """Free-energy function of the reactor contents, per lock, in kT. Standard state count 1.

    G = F (dmu0 + ln F - 1) + W (ln W - 1). A closed reaction can only lower it.
    """
    return F * (dmu0 + np.log(F) - 1.0) + W * (np.log(W) - 1.0)


def flux_sigma(F, W, k, dmu0, dt, nsub=256):
    """Entropy produced by a closed reaction step, from the fluxes: integral of (J+ - J-) ln(J+/J-).

    Uses the exact trajectory and Simpson's rule. A check on the books, not used by the dynamics.
    """
    em = math.exp(-dmu0)
    T = F + W
    feq = T * em / (1.0 + em)
    kap = k * (1.0 + em)
    t = np.linspace(0.0, dt, nsub + 1)
    f = feq + (F - feq) * np.exp(-kap * t)
    w = T - f
    jp, jm = k * f, k * em * w
    y = (jp - jm) * np.log(jp / jm)
    h = dt / nsub
    return float(h / 3.0 * (y[0] + y[-1] + 4.0 * y[1:-1:2].sum() + 2.0 * y[2:-1:2].sum()))


def mix_sigma(c_start, c_in, dil, dt, nsub=8):
    """Entropy produced by mixing the feed into the reactor during a flow step, in k_B.

    Rate: dil * sum over species of [c_in ln(c_in / c) - c_in + c], a relative entropy, never
    negative. Integrated with Simpson's rule on the exact flow trajectory. In steady state,
    reaction plus mixing entropy equals dil * [g(c_in) - g(c)]: free energy carried in minus
    free energy carried out (gate G4b).
    """
    t = np.linspace(0.0, dt, nsub + 1)[:, None]
    c = c_in + (c_start - c_in) * np.exp(-dil * t)
    y = dil * (c_in * np.log(c_in / c) - c_in + c).sum(axis=1)
    h = dt / nsub
    return float(h / 3.0 * (y[0] + y[-1] + 4.0 * y[1:-1:2].sum() + 2.0 * y[2:-1:2].sum()))


class World:
    def __init__(self, cfg: Config, seed: int):
        assert cfg.arm in ARMS
        assert cfg.n_bits <= 62
        self.cfg = cfg
        K = len(cfg.B)
        assert len(cfg.dmu0) == K and len(cfg.f_in) == K
        self.K = K
        self.dmu0 = np.array(cfg.dmu0, float)
        self.Bv = np.array(cfg.B, float)
        self.fin = np.array(cfg.f_in, float)
        self.mask = (1 << cfg.n_bits) - 1
        # Two streams. The world stream fixes locks, the starting library and the markers'
        # target, so D and L of the same seed start identical. The dynamics stream does the rest.
        rw = np.random.default_rng([seed, 0])
        self.rng = np.random.default_rng([seed, 1])
        rnd = lambda r, n: r.integers(0, self.mask + 1, size=n, dtype=np.int64)
        self.lock = rnd(rw, K)
        self.marker_target = int(rnd(rw, 1)[0])
        lib = rnd(rw, cfg.n0)
        lib_m = rnd(rw, cfg.n0)
        fixed = rnd(np.random.default_rng([seed, 2]), cfg.n_fixed)
        self.t = 0.0
        self.F = self.fin.copy()
        self.W = np.full(K, cfg.w_in)
        self.extinct = False
        if cfg.arm in ("D", "L"):
            n = cfg.n0
            self.key = np.full(n, self.lock[0]) if cfg.init == "perfect" else lib.copy()
            self.mark = lib_m.copy()
            self.e = np.full(n, cfg.e0)
        elif cfg.arm == "M":
            self.key, self.mark = fixed, np.zeros(cfg.n_fixed, np.int64)
            self.e = np.zeros(cfg.n_fixed)
        elif cfg.arm == "U":
            self.key, self.mark = np.full(cfg.n_fixed, self.lock[0]), np.zeros(cfg.n_fixed, np.int64)
            self.e = np.zeros(cfg.n_fixed)
        else:
            self.key = self.mark = np.zeros(0, np.int64)
            self.e = np.zeros(0)
        self.mu = cfg.mu if cfg.arm == "L" else 0.0
        self.grows = cfg.arm in ("D", "L")
        self._fixed_k = None          # cached total catalytic rate of fixed catalysts (M, U)

    # ------------------------------------------------------------------ helpers
    @property
    def n(self) -> int:
        return len(self.key)

    def stored(self) -> float:
        return float(self.e.sum())

    def distances(self) -> np.ndarray:
        """Hamming distance of every catalyst to every lock, shape (n, K)."""
        if self.cfg.arm == "U":
            return np.zeros((self.n, self.K), np.int64)
        return popcount(self.key[:, None] ^ self.lock[None, :])

    def cat_rates(self) -> np.ndarray:
        """Per-catalyst rate constant through each lock, shape (n, K)."""
        c = self.cfg
        return c.k0 * np.exp(-(c.b_cat + c.lam * self.distances())) / c.vol

    def _mutate(self, x: np.ndarray, p: float) -> np.ndarray:
        if p <= 0.0 or len(x) == 0:
            return x
        flips = self.rng.random((len(x), self.cfg.n_bits)) < p
        if not flips.any():
            return x
        bits = (flips * (1 << np.arange(self.cfg.n_bits, dtype=np.int64))).sum(axis=1)
        return x ^ bits

    # ------------------------------------------------------------------ one step
    def step(self, check_flux: bool = False) -> dict:
        c, dt = self.cfg, self.cfg.dt
        K = self.K
        stored_before = self.stored()
        FW_before = self.F + self.W

        # 1. Flow, solved exactly. Inflow is constant; outflow is what balances the change.
        dec = math.exp(-c.dil * dt)
        inF = c.dil * self.fin * dt
        inW = np.full(K, c.dil * c.w_in * dt)
        F1 = self.fin + (self.F - self.fin) * dec
        W1 = c.w_in + (self.W - c.w_in) * dec
        outF = inF - (F1 - self.F)
        outW = inW - (W1 - self.W)
        sigma_mix = 0.0
        if c.dil > 0.0:
            sigma_mix = mix_sigma(np.concatenate([self.F, self.W]),
                                  np.concatenate([self.fin, np.full(K, c.w_in)]), c.dil, dt)
        self.F, self.W = F1, W1

        # 2. Reaction, closed, solved exactly with rates held over the step.
        # Fixed catalysts gain nothing, so only their total rate matters; it changes only on drift.
        k_unc = c.k0 * np.exp(-self.Bv)
        if self.grows:
            rc = self.cat_rates() if self.n else np.zeros((0, K))
            k = k_unc + rc.sum(axis=0)
        else:
            if self._fixed_k is None:
                self._fixed_k = self.cat_rates().sum(axis=0) if self.n else np.zeros(K)
            rc = None
            k = k_unc + self._fixed_k
        em = np.exp(-self.dmu0)
        T = self.F + self.W
        feq = T * em / (1.0 + em)
        F2 = feq + (self.F - feq) * np.exp(-k * (1.0 + em) * dt)
        W2 = T - F2
        g_before = g_fn(self.F, self.W, self.dmu0)
        released = g_before - g_fn(F2, W2, self.dmu0)          # per lock, kT
        reacted = self.F - F2                                  # net F -> W, per lock
        sigma_flux = 0.0
        if check_flux:
            sigma_flux = sum(flux_sigma(self.F[i], self.W[i], k[i], self.dmu0[i], dt) for i in range(K))
        self.F, self.W = F2, W2

        # Each route carries the same affinity at every instant, so free energy is shared by rate.
        if self.grows and self.n:
            gain = c.eta * ((rc / k[None, :]) @ released)          # per catalyst
        else:
            gain = np.zeros(self.n)
        heat_direct = float(released.sum() - gain.sum())

        # 3. Growing catalysts: store, pay upkeep, die, divide.
        upkeep_paid = 0.0
        dead_heat = 0.0
        if self.grows and self.n:
            self.e = self.e + gain
            pay = np.minimum(self.e, c.c_up * dt)
            upkeep_paid = float(pay.sum())
            self.e = self.e - pay
            dead = (self.e <= 0.0) | (self.rng.random(self.n) < c.hazard * dt)
            dead_heat = float(self.e[dead].sum())
            keep = ~dead
            self.key, self.mark, self.e = self.key[keep], self.mark[keep], self.e[keep]
            div = self.e >= c.e_div
            if div.any():
                self.e[div] *= 0.5
                ck = self._mutate(self.key[div], self.mu)
                cm = self._mutate(self.mark[div], self.mu)
                self.key = np.concatenate([self.key, ck])
                self.mark = np.concatenate([self.mark, cm])
                self.e = np.concatenate([self.e, self.e[div]])
            if self.n == 0:
                self.extinct = True
        heat = heat_direct + upkeep_paid + dead_heat

        # 4. Lock drift.
        if c.drift > 0.0:
            for i in range(K):
                for _ in range(self.rng.poisson(c.drift * dt)):
                    self.lock[i] ^= np.int64(1) << np.int64(self.rng.integers(c.n_bits))
            if c.arm == "U":
                self.key = np.full(self.n, self.lock[0])
            self._fixed_k = None

        self.t += dt
        return dict(
            released=float(released.sum()), heat=heat, stored_before=stored_before,
            stored_after=self.stored(), sigma_flux=sigma_flux, sigma_mix=sigma_mix,
            fuel_in=inF + inW, fuel_out=outF + outW, fw_before=FW_before, fw_after=self.F + self.W,
            reacted=reacted, fed=inF, n=self.n,
        )


def energy_error(led: dict) -> float:
    """released - heat - change in stored. Must be zero."""
    return led["released"] - led["heat"] - (led["stored_after"] - led["stored_before"])


def fuel_error(led: dict) -> np.ndarray:
    """(in - out) - change in (F + W), per lock. Must be zero."""
    return (led["fuel_in"] - led["fuel_out"]) - (led["fw_after"] - led["fw_before"])


def run(cfg: Config, seed: int, t_end: float, t_late: float | None = None, rec_every: float = 10.0,
        windows: list | None = None) -> dict:
    """Run one world.

    windows: list of (t0, t1) measurement windows. Default: one window [t_late, t_end].
    The top-level *_late values are from the last window. Every window is also reported.
    """
    if windows is None:
        windows = [(t_late, t_end)]
    w = World(cfg, seed)
    steps = int(round(t_end / cfg.dt))
    rec = max(1, int(round(rec_every / cfg.dt)))
    wins = [(int(round(a / cfg.dt)), int(round(b / cfg.dt))) for a, b in windows]
    blank = lambda: dict(heat=0.0, mix=0.0, released=0.0, reacted=np.zeros(w.K), fed=np.zeros(w.K), n=0.0, k=0)
    accs = [blank() for _ in wins]
    snaps = [None] * len(wins)
    cum_heat = cum_mix = 0.0
    n_min = w.n
    t_extinct = None
    series = []
    win = blank()

    def snapshot():
        dist = w.distances()[:, 0] if w.n else np.array([])
        mdist = popcount(w.mark ^ np.int64(w.marker_target)) if w.n and w.grows else np.array([])
        return dict(key_dist=float(dist.mean()) if len(dist) else None,
                    key_dist_min=int(dist.min()) if len(dist) else None,
                    marker_dist=float(mdist.mean()) if len(mdist) else None)

    for s in range(steps):
        led = w.step()
        cum_heat += led["heat"]; cum_mix += led["sigma_mix"]
        n_min = min(n_min, led["n"])
        if w.extinct and t_extinct is None:
            t_extinct = round(w.t, 6)
        live = [win] + [a for a, (s0, s1) in zip(accs, wins) if s0 <= s < s1]
        for d in live:
            d["heat"] += led["heat"]; d["mix"] += led["sigma_mix"]; d["released"] += led["released"]
            d["reacted"] += led["reacted"]; d["fed"] += led["fed"]; d["n"] += led["n"]; d["k"] += 1
        for j, (s0, s1) in enumerate(wins):
            if s + 1 == s1:
                snaps[j] = snapshot()
        if (s + 1) % rec == 0:
            span = win["k"] * cfg.dt
            series.append(dict(t=round(w.t, 6), sigma=(win["heat"] + win["mix"]) / span,
                               sigma_rxn=win["heat"] / span, released=win["released"] / span,
                               n=win["n"] / win["k"], stored=w.stored(), **snapshot()))
            win = blank()

    def summary(a, snap, ab):
        span = a["k"] * cfg.dt
        return dict(t0=ab[0], t1=ab[1], sigma=(a["heat"] + a["mix"]) / span, sigma_rxn=a["heat"] / span,
                    sigma_mix=a["mix"] / span, released=a["released"] / span,
                    spent=(a["reacted"] / a["fed"]).tolist(), n=a["n"] / a["k"], **(snap or {}))

    out_w = [summary(a, sn, ab) for a, sn, ab in zip(accs, snaps, windows)]
    last = out_w[-1]
    return dict(
        config=asdict(cfg), seed=seed, windows=out_w,
        sigma_late=last["sigma"], sigma_rxn_late=last["sigma_rxn"], sigma_mix_late=last["sigma_mix"],
        released_late=last["released"], spent_late=last["spent"], n_late=last["n"],
        cum_sigma=cum_heat + cum_mix, cum_heat=cum_heat, stored_end=w.stored(),
        extinct=w.extinct, t_extinct=t_extinct, n_min=n_min, series=series,
    )
