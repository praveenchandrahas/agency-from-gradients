"""Starlight world: a minimal model of structures that live on a flux of free energy.

A ring of sites receives light. Light that nothing absorbs escapes, undegraded.
Light that an organism absorbs ends up as heat. That is the only route to heat.

Organisms have no objective. They gain energy by absorbing light, pay running
costs, split in two when they hold enough energy, and die when they run out or
by a constant hazard. Children inherit their parent's traits with small
mutations. Nothing in the code rewards capture, dissipation or entropy.

Traits (all heritable, all costly):
    a   absorber size       captures light, costs c_abs * a^2 per step
    m   motility            probability of moving one site per step
    g   sensing             probability that a move goes up the light gradient
    f   furnace             absorbs a second band of light and turns it straight
                            into heat. No benefit to the organism at all.

The energy ledger is closed and checked every step:
    emitted = escaped + captured
    captured = heat + change in stored energy
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import numpy as np

TRAITS = ("a", "m", "g", "f")


@dataclass(frozen=True)
class Config:
    # world
    n_sites: int = 256
    n_patches: int = 4
    patch_width: float = 6.0      # Gaussian sd, in sites
    patch_peak: float = 2.0       # light per site per step at the centre
    speed: float = 0.0            # final patch speed, sites per step
    ramp_steps: int = 0           # speed rises linearly from 0 over this many steps
    furnace_band: bool = False    # a second band of light only the furnace absorbs
    # physics of capture
    k_ext: float = 1.0            # Beer-Lambert extinction per unit absorber
    eta: float = 0.5              # fraction of absorbed light kept as usable energy
    # costs, energy per step
    c_base: float = 0.02
    c_abs: float = 0.05           # times a^2
    c_sense: float = 0.01         # times g
    c_move: float = 0.02          # per move actually made
    c_furnace: float = 0.0        # times f
    # life history
    hazard: float = 0.01          # death probability per step, independent of state
    e_rep: float = 2.0            # split in two at this energy
    # heredity
    mut_sd: float = 0.05
    mutable: tuple = ("a",)
    a0: float = 0.3
    m0: float = 0.0
    g0: float = 0.0
    f0: float = 0.0
    a_max: float = 4.0
    # sensing
    sense_eps: float = 0.01       # light differences below this are not sensed
    # bookkeeping
    n0: int = 400
    max_pop: int = 60000

    def as_dict(self):
        d = asdict(self)
        d["mutable"] = "".join(self.mutable)
        return d


class Extinct(Exception):
    pass


class World:
    def __init__(self, cfg: Config, seed: int):
        for t in cfg.mutable:
            if t not in TRAITS:
                raise ValueError(f"unknown trait {t!r}")
        self.cfg = cfg
        self.rng = np.random.default_rng(seed)
        self.t = 0
        n = cfg.n_sites
        self.x = np.arange(n, dtype=float)
        self.centres = (np.arange(cfg.n_patches) + 0.5) * n / cfg.n_patches
        self.light = self._field()
        # seed organisms on lit sites, in proportion to light
        p = self.light / self.light.sum()
        self.pos = self.rng.choice(n, size=cfg.n0, p=p)
        self.e = np.full(cfg.n0, cfg.e_rep / 2.0)
        self.a = np.full(cfg.n0, cfg.a0)
        self.m = np.full(cfg.n0, cfg.m0)
        self.g = np.full(cfg.n0, cfg.g0)
        self.f = np.full(cfg.n0, cfg.f0)
        self.extinct = False

    # ---------------------------------------------------------------- light
    def _field(self) -> np.ndarray:
        cfg = self.cfg
        n = cfg.n_sites
        L = np.zeros(n)
        for c in self.centres:
            d = np.abs(self.x - (c % n))
            d = np.minimum(d, n - d)
            L += np.where(d <= 3.0 * cfg.patch_width,
                          cfg.patch_peak * np.exp(-0.5 * (d / cfg.patch_width) ** 2), 0.0)
        return L

    def current_speed(self) -> float:
        cfg = self.cfg
        if cfg.ramp_steps <= 0:
            return cfg.speed
        return cfg.speed * min(1.0, self.t / cfg.ramp_steps)

    @property
    def n(self) -> int:
        return self.pos.size

    def stored(self) -> float:
        return float(self.e.sum())

    # ----------------------------------------------------------------- step
    def step(self) -> dict:
        """Advance one step. Returns the energy ledger for this step."""
        cfg, rng = self.cfg, self.rng
        N = cfg.n_sites
        v = self.current_speed()
        if v != 0.0:
            self.centres = self.centres + v
            self.light = self._field()
        L = self.light
        emitted = float(L.sum())
        emitted_b = emitted if cfg.furnace_band else 0.0
        stored_before = self.stored()
        n = self.n
        led = dict(emitted=emitted, emitted_b=emitted_b, captured=0.0, captured_b=0.0,
                   heat=0.0, stored_before=stored_before, stored_after=0.0,
                   pop=n, births=0, deaths=0, moves=0, directed=0, light_at_org=0.0)
        if n == 0:
            self.extinct = True
            self.t += 1
            return led

        # 1. movement
        moved = rng.random(n) < self.m
        directed = moved & (rng.random(n) < self.g)
        step_dir = np.where(rng.random(n) < 0.5, -1, 1)
        if directed.any():
            grad = L[(self.pos + 1) % N] - L[(self.pos - 1) % N]
            sensed = directed & (np.abs(grad) > cfg.sense_eps)
            step_dir = np.where(sensed, np.sign(grad).astype(int), step_dir)
        self.pos = np.where(moved, (self.pos + step_dir) % N, self.pos)

        # 2. absorption. Organisms on a site shade each other (Beer-Lambert).
        area = np.bincount(self.pos, weights=self.a, minlength=N)
        frac = -np.expm1(-cfg.k_ext * area)                       # fraction of site light captured
        with np.errstate(divide="ignore", invalid="ignore"):
            per_area = np.where(area > 0, L * frac / area, 0.0)
        intake = per_area[self.pos] * self.a
        captured = float(intake.sum())

        captured_b = 0.0
        if cfg.furnace_band:
            farea = np.bincount(self.pos, weights=self.f, minlength=N)
            ffrac = -np.expm1(-cfg.k_ext * farea)
            captured_b = float((L * ffrac).sum())                  # straight to heat

        # 3. energy balance
        cost = (cfg.c_base + cfg.c_abs * self.a ** 2 + cfg.c_sense * self.g
                + cfg.c_furnace * self.f + cfg.c_move * moved)
        e_tmp = self.e + cfg.eta * intake - cost
        deficit = np.clip(-e_tmp, 0.0, None)                       # cost that could not be paid
        heat = (1.0 - cfg.eta) * captured + float((cost - deficit).sum())
        e_new = np.maximum(e_tmp, 0.0)

        # 4. death: starvation, or a constant hazard blind to everything
        dead = (e_tmp <= 0.0) | (rng.random(n) < cfg.hazard)
        heat += float(e_new[dead].sum())                           # the body's energy becomes heat
        keep = ~dead
        pos, e = self.pos[keep], e_new[keep]
        a, m, g, f = self.a[keep], self.m[keep], self.g[keep], self.f[keep]

        # 5. reproduction: split the energy in two, copy the traits with mutation
        par = e >= cfg.e_rep
        nb = int(par.sum())
        if nb:
            e = np.where(par, e / 2.0, e)
            cpos = (pos[par] + rng.integers(-1, 2, size=nb)) % N
            kids = {}
            for name, arr, hi in (("a", a, cfg.a_max), ("m", m, 1.0), ("g", g, 1.0), ("f", f, 1.0)):
                c = arr[par]
                if name in cfg.mutable:
                    c = np.clip(c + rng.normal(0.0, cfg.mut_sd, size=nb), 0.0, hi)
                kids[name] = c
            pos = np.concatenate([pos, cpos])
            e = np.concatenate([e, e[par]])
            a = np.concatenate([a, kids["a"]])
            m = np.concatenate([m, kids["m"]])
            g = np.concatenate([g, kids["g"]])
            f = np.concatenate([f, kids["f"]])
        self.pos, self.e, self.a, self.m, self.g, self.f = pos, e, a, m, g, f
        if self.n > cfg.max_pop:
            raise RuntimeError(f"population {self.n} exceeded max_pop; parameters are off")

        led.update(captured=captured, captured_b=captured_b, heat=heat,
                   stored_after=self.stored(), births=nb, deaths=int(dead.sum()),
                   moves=int(moved.sum()), directed=int(directed.sum()),
                   light_at_org=float(L[self.pos].mean()) if self.n else 0.0)
        self.t += 1
        if self.n == 0:
            self.extinct = True
        return led


def ledger_error(led: dict) -> float:
    """captured - heat - change in stored energy. Should be zero."""
    return led["captured"] - led["heat"] - (led["stored_after"] - led["stored_before"])


def run(cfg: Config, seed: int, steps: int, rec_every: int = 200, check: bool = True) -> list[dict]:
    """Run one world. Returns one record per window of `rec_every` steps."""
    w = World(cfg, seed)
    rows, acc, worst = [], None, 0.0
    for t in range(steps):
        led = w.step()
        if check:
            err = abs(ledger_error(led))
            worst = max(worst, err)
            if err > 1e-6 * max(1.0, led["emitted"]):
                raise AssertionError(f"energy ledger broke at step {t}: {err}")
        if acc is None:
            acc = {k: 0.0 for k in led}
        for k, val in led.items():
            acc[k] += val
        if (t + 1) % rec_every == 0:
            k = rec_every
            n = w.n
            em = acc["emitted"]
            row = dict(
                t=t + 1, speed=w.current_speed(), pop=acc["pop"] / k,
                capture=acc["captured"] / em if em else 0.0,
                capture_b=acc["captured_b"] / acc["emitted_b"] if acc["emitted_b"] else 0.0,
                heat=acc["heat"] / k, heat_b=acc["captured_b"] / k, emitted=em / k,
                births=acc["births"] / k, deaths=acc["deaths"] / k,
                directed_rate=acc["directed"] / acc["pop"] if acc["pop"] else 0.0,
                move_rate=acc["moves"] / acc["pop"] if acc["pop"] else 0.0,
                light_at_org=acc["light_at_org"] / k,
                a=float(w.a.mean()) if n else np.nan, m=float(w.m.mean()) if n else np.nan,
                g=float(w.g.mean()) if n else np.nan, f=float(w.f.mean()) if n else np.nan,
                mg=float((w.m * w.g).mean()) if n else np.nan,
                e_mean=float(w.e.mean()) if n else np.nan,
                extinct=int(w.extinct), ledger_worst=worst)
            rows.append(row)
            acc = None
    return rows
