"""Asynchronous gradient-ladder world.

Agents have no reward function. They live, eat, invest, reproduce and die in a
continuous population; what persists is what is left. Entropy production is
*measured* (see ``summary``) and is never an input to behaviour, except in the
explicitly labelled ``selection="entropy"`` control condition.

Energy ledger (checked by tests):
    delta(total energy) = injected - leaked - heat - repro_loss - death_removed
"""
from __future__ import annotations

import copy

import numpy as np

from .config import Config

# observation: channels x 5 cells ordered N, E, S, W, here (same order as DIRS) + own energy + bias
N_CH = 7   # commons, t1 locked/open, t2 locked/open, scent1, scent2
N_OBS = N_CH * 5 + 2
HID = 16
N_ACT = 6  # N, E, S, W, stay, invest

# Two policy classes (selected by Config.policy):
#   "equivariant": one shared weight vector over channels is applied to every
#       direction's cues (chemotaxis-style); ~27 parameters. Strong inductive prior.
#   "mlp": generic one-hidden-layer network; ~450 parameters. No prior, much slower
#       to evolve, and the only class with capacity for memory/prediction work.
P_MLP = N_OBS * HID + HID + HID * N_ACT + N_ACT
P_EQ = N_CH * 3 + 6


def n_params(policy: str) -> int:
    if policy == "equivariant":
        return P_EQ
    if policy == "mlp":
        return P_MLP
    raise ValueError(f"unknown policy {policy!r}")


DIRS = np.array([[-1, 0], [0, 1], [1, 0], [0, -1], [0, 0], [0, 0]], dtype=np.int64)
LOOK = DIRS[:5]


def random_genomes(rng: np.random.Generator, n: int, policy: str = "equivariant") -> np.ndarray:
    if policy == "equivariant":
        return rng.normal(0.0, 1.0, (n, P_EQ))
    g = np.empty((n, P_MLP))
    a = N_OBS * HID
    b = a + HID
    c = b + HID * N_ACT
    g[:, :a] = rng.normal(0, 1 / np.sqrt(N_OBS), (n, a))
    g[:, a:b] = 0.0
    g[:, b:c] = rng.normal(0, 1 / np.sqrt(HID), (n, c - b))
    g[:, c:] = 0.0
    return g


def policy_logits(genomes: np.ndarray, obs: np.ndarray, policy: str = "equivariant") -> np.ndarray:
    n = len(genomes)
    if policy == "equivariant":
        V = obs[:, : N_CH * 5].reshape(n, N_CH, 5)       # channel x (N,E,S,W,here)
        E = obs[:, N_CH * 5]
        wn = genomes[:, :N_CH]
        ws = genomes[:, N_CH:2 * N_CH]
        wi = genomes[:, 2 * N_CH:3 * N_CH]
        bm, bs, bi, em, es, ei = (genomes[:, 3 * N_CH + k] for k in range(6))
        move = np.einsum("nc,ncd->nd", wn, V[:, :, :4]) + (bm + em * E)[:, None]
        stay = np.einsum("nc,nc->n", ws, V[:, :, 4]) + bs + es * E
        inv = np.einsum("nc,nc->n", wi, V[:, :, 4]) + bi + ei * E
        return np.concatenate([move, stay[:, None], inv[:, None]], axis=1)
    a = N_OBS * HID
    b = a + HID
    c = b + HID * N_ACT
    w1 = genomes[:, :a].reshape(n, N_OBS, HID)
    b1 = genomes[:, a:b]
    w2 = genomes[:, b:c].reshape(n, HID, N_ACT)
    b2 = genomes[:, c:]
    h = np.tanh(np.einsum("ni,nih->nh", obs, w1) + b1)
    return np.einsum("nh,nha->na", h, w2) + b2


class World:
    def __init__(self, cfg: Config, seed: int, n_agents: int | None = None):
        self.cfg = cfg
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        L = cfg.size
        self.commons = np.full((L, L), cfg.commons_cap)
        self.ttype = np.zeros((L, L), dtype=np.int8)
        self.stock = np.zeros((L, L))
        self.progress = np.zeros((L, L))
        self.unlocked = np.zeros((L, L), dtype=bool)
        self.t2_budget = 0
        self.field = self._make_field()
        self._place_sites()
        self.scent = np.zeros((2, L, L))
        self._update_scent()

        m = cfg.max_pop
        self.alive = np.zeros(m, dtype=bool)
        self.pos = np.zeros((m, 2), dtype=np.int64)
        self.energy = np.zeros(m)
        self.age = np.zeros(m, dtype=np.int64)
        self.lineage = np.zeros(m, dtype=np.int64)
        self.genome = np.zeros((m, n_params(cfg.policy)))
        self.spent_acc = np.zeros(m)
        self.commons_acc = np.zeros(m)
        self.contrib = np.zeros(m)

        self.t = 0
        self.reproduce = True
        self.policy = None  # optional hand-coded policy(obs, rng) -> actions (positive controls)
        self.log = {k: [] for k in
                    ("pop", "leak", "heat", "gain_c", "gain_1", "gain_2", "births", "deaths")}
        self.ledger = dict(injected=0.0, leaked=0.0, heat=0.0, repro_loss=0.0,
                           death_removed=0.0, bailout=0.0)
        self.first_unlock = {1: None, 2: None}
        self.unlock_events = {1: 0, 2: 0}
        self.converted = 0

        n0 = cfg.init_pop if n_agents is None else n_agents
        if n0:
            self.spawn(random_genomes(self.rng, n0, cfg.policy),
                       self.rng.integers(0, L, (n0, 2)),
                       np.full(n0, cfg.init_energy),
                       lineages=np.arange(n0))
        self._e0 = self.total_energy()

    # ------------------------------------------------------------------ setup
    def _place_sites(self) -> None:
        cfg = self.cfg
        L = cfg.size
        n1, n2 = cfg.n_tier1, cfg.n_tier2
        cells = self.rng.choice(L * L, n1 + n2, replace=False)
        for c in cells[:n1]:
            x, y = divmod(int(c), L)
            self.ttype[x, y] = 1
            self.stock[x, y] = cfg.stock1
        if cfg.succession:
            self.t2_budget = n2           # tier-2 sites appear only by conversion
        else:
            for c in cells[n1:]:
                x, y = divmod(int(c), L)
                self.ttype[x, y] = 2
                self.stock[x, y] = cfg.stock2

    def _make_field(self) -> np.ndarray:
        """Spatial multiplier on commons regrowth (mean 1). Patchiness gives tier 0
        a weak gradient, so directed foraging can be selected for in small steps."""
        cfg = self.cfg
        L = cfg.size
        if cfg.patchiness <= 0:
            return np.ones((L, L))
        ax = np.arange(L)
        f = np.zeros((L, L))
        for _ in range(cfg.n_patches):
            x, y = self.rng.integers(0, L, 2)
            dx = np.minimum(np.abs(ax - x), L - np.abs(ax - x))[:, None]
            dy = np.minimum(np.abs(ax - y), L - np.abs(ax - y))[None, :]
            f += np.exp(-(dx**2 + dy**2) / (2 * cfg.patch_sigma**2))
        f = f / f.mean()                               # mean 1
        f = (1.0 - cfg.patchiness) + cfg.patchiness * f
        return f / f.mean()

    def _update_scent(self) -> None:
        """Smooth, static-between-conversions fields pointing toward each reservoir
        tier (a chemotaxis-style cue). Gaussian of toroidal distance to each site."""
        cfg = self.cfg
        L = cfg.size
        ax = np.arange(L)
        for k, tt in enumerate((1, 2)):
            f = np.zeros((L, L))
            for x, y in np.argwhere(self.ttype == tt):
                dx = np.minimum(np.abs(ax - x), L - np.abs(ax - x))[:, None]
                dy = np.minimum(np.abs(ax - y), L - np.abs(ax - y))[None, :]
                f += np.exp(-(dx**2 + dy**2) / (2 * cfg.scent_sigma**2))
            self.scent[k] = np.minimum(f, 1.0)

    def spawn(self, genomes, positions, energies, lineages=None) -> int:
        free = np.flatnonzero(~self.alive)
        k = min(len(free), len(genomes))
        if k == 0:
            return 0
        s = free[:k]
        self.alive[s] = True
        self.genome[s] = genomes[:k]
        self.pos[s] = positions[:k]
        self.energy[s] = energies[:k]
        self.age[s] = 0
        self.spent_acc[s] = 0.0
        self.commons_acc[s] = 0.0
        self.contrib[s] = 0.0
        self.lineage[s] = np.arange(k) if lineages is None else lineages[:k]
        return k

    # -------------------------------------------------------------- bookkeeping
    def total_energy(self) -> float:
        return float(self.commons.sum() + self.stock.sum() + self.energy[self.alive].sum())

    def ledger_residual(self) -> float:
        """Should be ~0 (floating-point noise) at every step."""
        L = self.ledger
        expected = (L["injected"] - L["leaked"] - L["heat"] - L["repro_loss"]
                    - L["death_removed"] + L["bailout"])
        return (self.total_energy() - self._e0) - expected

    # ------------------------------------------------------------- environment
    def _environment_update(self) -> tuple[float, float]:
        cfg = self.cfg
        leak = 0.0
        # commons: regrow; whatever would exceed the cap leaks (passive dissipation)
        self.commons += cfg.regrow * self.field
        self.ledger["injected"] += cfg.regrow * float(self.field.sum())
        excess = np.maximum(self.commons - cfg.commons_cap, 0.0)
        leak += float(excess.sum())
        self.commons -= excess
        # reservoirs: flat injection, proportional passive leak
        res = self.ttype > 0
        if res.any():
            reg = np.where(self.ttype == 1, cfg.regrow1, cfg.regrow2)
            self.stock[res] += reg[res]
            self.ledger["injected"] += float(reg[res].sum())
            lk = self.stock[res] * cfg.reservoir_leak
            self.stock[res] -= lk
            leak += float(lk.sum())
            # maintenance: progress decays everywhere; a site is open only while
            # progress stays at or above its lock level
            dec = np.where(self.ttype == 1, cfg.decay1, cfg.decay2)
            self.progress[res] *= (1.0 - dec[res])
            lock = np.where(self.ttype == 1, cfg.lock1, cfg.lock2)
            self.unlocked = res & (self.progress >= lock)
        # succession: drained tier-1 sites become tier-2 sites
        changed = False
        if cfg.succession and self.t2_budget > 0:
            drained = (self.ttype == 1) & (self.stock <= cfg.depleted_at)
            for x, y in np.argwhere(drained):
                if self.t2_budget <= 0:
                    break
                # the new tier-2 stock is created from nothing on purpose; count it as
                # injected so the ledger stays closed
                self.ledger["injected"] += cfg.stock2 - self.stock[x, y]
                self.ttype[x, y] = 2
                self.stock[x, y] = cfg.stock2
                self.progress[x, y] = 0.0
                self.unlocked[x, y] = False
                self.t2_budget -= 1
                self.converted += 1
                changed = True
        if changed:
            self._update_scent()
        self.ledger["leaked"] += leak
        return leak, 0.0

    def _openness(self) -> np.ndarray:
        """Graded openness in [0, 1]: progress / lock level on reservoir cells.
        Partial investment gives partial return (a smooth fitness landscape)."""
        cfg = self.cfg
        lock = np.where(self.ttype == 1, cfg.lock1, cfg.lock2)
        fr = np.minimum(self.progress / lock, 1.0)
        return np.where(self.ttype > 0, fr, 0.0)

    # --------------------------------------------------------------- perception
    def _observe(self, idx: np.ndarray) -> np.ndarray:
        cfg = self.cfg
        L = cfg.size
        live = self.stock > cfg.depleted_at           # drained sites are invisible
        fr = self._openness()
        ch = np.stack([
            self.commons / cfg.commons_cap,
            (self.ttype == 1) * live * (1.0 - fr),
            (self.ttype == 1) * live * fr,
            (self.ttype == 2) * live * (1.0 - fr),
            (self.ttype == 2) * live * fr,
            self.scent[0],
            self.scent[1],
        ])
        p = self.pos[idx]
        xs = (p[:, 0:1] + LOOK[:, 0]) % L          # (n, 5)
        ys = (p[:, 1:2] + LOOK[:, 1]) % L
        v = ch[:, xs, ys]                           # (5ch, n, 5pos)
        obs = np.concatenate([
            v.transpose(1, 0, 2).reshape(len(idx), -1),
            (self.energy[idx] / cfg.repro_thresh)[:, None],
            np.ones((len(idx), 1)),
        ], axis=1)
        return obs

    def _act(self, idx: np.ndarray, obs: np.ndarray) -> np.ndarray:
        if self.policy is not None:
            return self.policy(obs, self.rng)
        logits = policy_logits(self.genome[idx], obs, self.cfg.policy)
        g = self.rng.gumbel(size=logits.shape)
        return np.argmax(logits + g, axis=1)

    # ------------------------------------------------------------------- step
    def step(self) -> None:
        cfg = self.cfg
        L = cfg.size
        leak, _ = self._environment_update()
        idx = np.flatnonzero(self.alive)
        n = len(idx)
        gain_c = gain_1 = gain_2 = heat = 0.0
        births = deaths = 0

        if n:
            obs = self._observe(idx)
            act = self._act(idx, obs)
            cost = (cfg.metabolism + cfg.move_cost * (act < 4)
                    + cfg.invest_cost * (act == 5))
            self.pos[idx] = (self.pos[idx] + DIRS[act]) % L
            x, y = self.pos[idx, 0], self.pos[idx, 1]

            # invest -> progress -> unlock
            m = (act == 5) & (self.ttype[x, y] > 0)
            if cfg.deposit_share == "contributor":
                self.contrib[idx] *= cfg.contrib_decay
                self.contrib[idx[m]] += 1.0
            if m.any():
                np.add.at(self.progress, (x[m], y[m]), 1.0)
                lock = np.where(self.ttype == 1, cfg.lock1, cfg.lock2)
                np.minimum(self.progress, 2.0 * lock, out=self.progress)
                now = (self.ttype > 0) & (self.progress >= lock)
                newly = now & ~self.unlocked          # rising edges only
                for tt in (1, 2):
                    k = int((newly & (self.ttype == tt)).sum())
                    if k:
                        self.unlock_events[tt] += k
                        if self.first_unlock[tt] is None:
                            self.first_unlock[tt] = self.t
                self.unlocked = now

            # eating: cell-level sharing
            cell = x * L + y
            cnt = np.bincount(cell, minlength=L * L).astype(float)
            safe = np.maximum(cnt, 1.0)

            tot_c = np.minimum(cfg.eat_rate * cnt, self.commons.ravel())
            self.commons.ravel()[:] -= tot_c           # ravel() of C-contiguous is a view
            g_c = tot_c[cell] / safe[cell]

            hr = (np.where(self.ttype == 1, cfg.harvest1,
                           np.where(self.ttype == 2, cfg.harvest2, 0.0))
                  * self._openness()).ravel()
            tot_r = np.minimum(hr * cnt, self.stock.ravel())
            self.stock.ravel()[:] -= tot_r
            if cfg.deposit_share == "contributor":
                w = self.contrib[idx] + cfg.contrib_floor
                W = np.bincount(cell, weights=w, minlength=L * L)
                g_r = tot_r[cell] * w / W[cell]
            else:
                g_r = tot_r[cell] / safe[cell]
            t_at = self.ttype[x, y]
            g_1 = np.where(t_at == 1, g_r, 0.0)
            g_2 = np.where(t_at == 2, g_r, 0.0)

            self.energy[idx] += g_c + g_1 + g_2 - cost
            self.commons_acc[idx] += g_c
            self.spent_acc[idx] += cost
            self.age[idx] += 1
            gain_c, gain_1, gain_2 = float(g_c.sum()), float(g_1.sum()), float(g_2.sum())
            heat = float(cost.sum())
            self.ledger["heat"] += heat

            # death / bailout
            dead = self.energy[idx] <= 0.0
            if cfg.mortality and cfg.hazard > 0:
                dead = dead | (self.rng.random(n) < cfg.hazard)
            if dead.any():
                di = idx[dead]
                if cfg.mortality:
                    self.ledger["death_removed"] += float(self.energy[di].sum())
                    self.alive[di] = False
                    deaths = len(di)
                else:
                    self.ledger["bailout"] += float((1.0 - self.energy[di]).sum())
                    self.energy[di] = 1.0

            # reproduction
            if self.reproduce:
                births = self._reproduce()

        self.t += 1
        L_ = self.log
        L_["pop"].append(int(self.alive.sum()))
        L_["leak"].append(leak)
        L_["heat"].append(heat)
        L_["gain_c"].append(gain_c)
        L_["gain_1"].append(gain_1)
        L_["gain_2"].append(gain_2)
        L_["births"].append(births)
        L_["deaths"].append(deaths)

    def _reproduce(self) -> int:
        cfg = self.cfg
        a = np.flatnonzero(self.alive)
        if len(a) == 0:
            return 0
        viable = self.energy[a] >= cfg.repro_cost + 1.0
        if cfg.selection == "persistence":
            ok = self.energy[a] >= cfg.repro_thresh
        elif cfg.selection == "entropy":
            ok = (self.spent_acc[a] >= cfg.entropy_repro_spent) & viable
        elif cfg.selection == "task":
            ok = (self.commons_acc[a] >= cfg.repro_thresh) & viable
        elif cfg.selection == "drift":
            # random-parents model (not fully neutral: starvation still filters genomes): births restore the population towards init_pop, parents
            # chosen uniformly among the living, independent of energy or behaviour
            lam = cfg.drift_restore * max(cfg.init_pop - len(a), 0)
            nb = min(int(self.rng.poisson(lam)), len(a))
            ok = np.zeros(len(a), dtype=bool)
            ok[self.rng.choice(len(a), nb, replace=False)] = True
            ok &= viable
        else:
            raise ValueError(f"unknown selection {cfg.selection!r}")
        parents = a[ok]
        if len(parents) == 0:
            return 0
        self.rng.shuffle(parents)
        free = np.flatnonzero(~self.alive)
        parents = parents[: len(free)]
        k = len(parents)
        if k == 0:
            return 0
        if cfg.heredity:
            P = self.genome.shape[1]
            mask = self.rng.random((k, P)) < cfg.mut_rate
            kids = self.genome[parents] + mask * cfg.mut_sigma * self.rng.standard_normal((k, P))
        else:
            kids = random_genomes(self.rng, k, cfg.policy)
        self.energy[parents] -= cfg.repro_cost
        self.spent_acc[parents] = 0.0
        self.commons_acc[parents] = 0.0
        self.ledger["repro_loss"] += k * cfg.repro_cost * (1 - cfg.child_share)
        s = free[:k]
        self.alive[s] = True
        self.genome[s] = kids
        self.pos[s] = self.pos[parents]
        self.energy[s] = cfg.repro_cost * cfg.child_share
        self.age[s] = 0
        self.spent_acc[s] = 0.0
        self.commons_acc[s] = 0.0
        self.contrib[s] = 0.0
        self.lineage[s] = self.lineage[parents]
        return k

    def run(self, steps: int | None = None) -> "World":
        for _ in range(self.cfg.steps if steps is None else steps):
            self.step()
        return self

    # ------------------------------------------------------------------ probes
    def clone_environment(self) -> "World":
        """Copy of the world with the environment intact and no agents."""
        w = copy.deepcopy(self)
        w.alive[:] = False
        w.rng = np.random.default_rng(self.rng.integers(2**63))
        w.log = {k: [] for k in w.log}
        return w

    # ----------------------------------------------------------------- summary
    def summary(self, passive_rate: float | None = None) -> dict:
        cfg = self.cfg
        lg = {k: np.asarray(v, dtype=float) for k, v in self.log.items()}
        T = len(lg["pop"])
        w = slice(int(T * 0.75), T)                       # last quarter
        gain = lg["gain_c"][w] + lg["gain_1"][w] + lg["gain_2"][w]
        leak = lg["leak"][w]
        ent = leak + cfg.kappa * lg["heat"][w]
        # births also dissipate: repro_loss is small; kept out of ent for simplicity
        gsum = float(gain.sum())
        out = dict(
            pop_end=int(self.alive.sum()),
            pop_mean_late=float(lg["pop"][w].mean()),
            extinct=bool(self.alive.sum() == 0),
            capture_fraction=gsum / max(gsum + float(leak.sum()), 1e-12),
            share_commons=float(lg["gain_c"][w].sum()) / max(gsum, 1e-12),
            share_tier1=float(lg["gain_1"][w].sum()) / max(gsum, 1e-12),
            share_tier2=float(lg["gain_2"][w].sum()) / max(gsum, 1e-12),
            entropy_rate=float(ent.mean()),
            t1_unlocks=self.unlock_events[1],
            t2_unlocks=self.unlock_events[2],
            t1_reached=int(self.unlock_events[1] > 0),
            t2_reached=int(self.unlock_events[2] > 0),
            first_t1=np.nan if self.first_unlock[1] is None else self.first_unlock[1],
            first_t2=np.nan if self.first_unlock[2] is None else self.first_unlock[2],
            founders_alive=int(len(np.unique(self.lineage[self.alive]))) if self.alive.any() else 0,
            births=int(lg["births"].sum()),
            deaths=int(lg["deaths"].sum()),
            work_per_entropy=np.nan,  # reserved: needs an explicit work definition (see docs)
        )
        if passive_rate is not None and passive_rate > 0:
            out["capture_ratio"] = out["entropy_rate"] / passive_rate
        return out


def passive_entropy_rate(cfg: Config, seed: int = 0, steps: int = 400) -> float:
    """Entropy rate of the same environment with no agents (the denominator of
    the Capture Ratio)."""
    w = World(cfg, seed, n_agents=0)
    w.run(steps)
    lg = np.asarray(w.log["leak"])
    return float(lg[steps // 2:].mean())
