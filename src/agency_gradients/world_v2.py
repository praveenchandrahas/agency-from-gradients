"""World v2: the v1 gradient ladder plus seasons, impassable terrain, danger zones,
a pheromone signalling channel, a recurrent policy with memory, and heritable body
traits (size, reproduction threshold). Opt-in via ``Config.world_v2``; v1 is untouched.

Energy ledger is unchanged in form: signalling costs energy that is dissipated as
heat; seasons change injection (counted as injected); body size changes who gets
how much of a shared meal, never the total. The pheromone is information, not energy.
"""
from __future__ import annotations

import numpy as np

from .config import Config
from .policies_v2 import N_ACT2, N_OBS2, H2, forward, random_genomes_v2, traits
from .world import DIRS, LOOK, World, random_genomes

DIRS7 = np.vstack([DIRS, [[0, 0]]]).astype(np.int64)   # action 6 = signal (no movement)


class WorldV2(World):
    def __init__(self, cfg: Config, seed: int, n_agents: int | None = None):
        assert cfg.world_v2, "WorldV2 requires cfg.world_v2=True"
        assert cfg.policy in ("recurrent", "mlp2", "equivariant2"), \
            "world v2 needs a v2 policy: recurrent | mlp2 | equivariant2"
        super().__init__(cfg, seed, n_agents)
        L = cfg.size
        m = cfg.max_pop
        self.h = np.zeros((m, H2))
        self.gen = np.zeros(m, dtype=np.int64)
        self.signal = np.zeros((L, L))
        self.wall = self._make_walls()
        self.danger = self._make_danger()
        f = self.field * (~self.wall)
        self._field0 = f / f.mean()
        self.commons[self.wall] = 0.0
        # move any founders off wall cells
        free = np.argwhere(~self.wall)
        for i in np.flatnonzero(self.alive):
            if self.wall[tuple(self.pos[i])]:
                self.pos[i] = free[self.rng.integers(len(free))]
        self.log["sig"] = []
        self._e0 = self.total_energy()

    # ----------------------------------------------------------------- setup
    def _make_walls(self) -> np.ndarray:
        cfg = self.cfg
        L = cfg.size
        wall = np.zeros((L, L), dtype=bool)
        for _ in range(cfg.n_walls):
            x, y = self.rng.integers(0, L, 2)
            horizontal = bool(self.rng.integers(2))
            for k in range(cfg.wall_len):
                cx, cy = ((x, (y + k) % L) if horizontal else ((x + k) % L, y))
                if self.ttype[cx, cy] == 0:
                    wall[cx, cy] = True
        return wall

    def _make_danger(self) -> np.ndarray:
        cfg = self.cfg
        L = cfg.size
        ax = np.arange(L)
        d = np.zeros((L, L))
        for _ in range(cfg.n_danger):
            x, y = self.rng.integers(0, L, 2)
            dx = np.minimum(np.abs(ax - x), L - np.abs(ax - x))[:, None]
            dy = np.minimum(np.abs(ax - y), L - np.abs(ax - y))[None, :]
            d = np.maximum(d, (np.sqrt(dx**2 + dy**2) <= cfg.danger_radius).astype(float))
        return d

    def spawn(self, genomes, positions, energies, lineages=None) -> int:
        free = np.flatnonzero(~self.alive)
        k = super().spawn(genomes, positions, energies, lineages)
        if k and hasattr(self, "h"):
            self.h[free[:k]] = 0.0
        return k

    # ------------------------------------------------------------ perception
    def _observe(self, idx: np.ndarray) -> np.ndarray:
        cfg = self.cfg
        L = cfg.size
        base = super()._observe(idx)
        p = self.pos[idx]
        xs = (p[:, 0:1] + LOOK[:, 0]) % L
        ys = (p[:, 1:2] + LOOK[:, 1]) % L
        ph = 2 * np.pi * self.t / cfg.season_period
        extra = np.concatenate([
            self.wall[xs, ys].astype(float),
            self.danger[xs, ys],
            self.signal[xs, ys],
            np.full((len(idx), 1), np.sin(ph)),
            np.full((len(idx), 1), np.cos(ph)),
        ], axis=1)
        return np.concatenate([base, extra], axis=1)

    def _act(self, idx: np.ndarray, obs: np.ndarray) -> np.ndarray:
        if self.policy is not None:
            return self.policy(obs, self.rng)
        logits, hn = forward(self.genome[idx], obs, self.h[idx], self.cfg.policy)
        self.h[idx] = hn
        return np.argmax(logits + self.rng.gumbel(size=logits.shape), axis=1)

    # ---------------------------------------------------------------- dynamics
    def _update_signal(self) -> None:
        cfg = self.cfg
        S = self.signal * (1.0 - cfg.signal_decay)
        nb = (np.roll(S, 1, 0) + np.roll(S, -1, 0) + np.roll(S, 1, 1) + np.roll(S, -1, 1)) / 4.0
        self.signal = (1.0 - cfg.signal_diffuse) * S + cfg.signal_diffuse * nb
        self.signal[self.wall] = 0.0

    def step(self) -> None:
        cfg = self.cfg
        L = cfg.size
        # seasons modulate commons regrowth (injection is counted from self.field)
        self.field = self._field0 * (1.0 + cfg.season_amp * np.sin(2 * np.pi * self.t / cfg.season_period))
        leak, _ = self._environment_update()
        self._update_signal()
        idx = np.flatnonzero(self.alive)
        n = len(idx)
        gain_c = gain_1 = gain_2 = heat = 0.0
        births = deaths = 0
        sig_n = 0

        if n:
            size, _rep = traits(self.genome[idx])
            obs = self._observe(idx)
            act = self._act(idx, obs)
            cost = (cfg.metabolism * size + cfg.move_cost * (act < 4)
                    + cfg.invest_cost * (act == 5) + cfg.signal_cost * (act == 6))
            old = self.pos[idx].copy()
            new = (old + DIRS7[act]) % L
            blocked = self.wall[new[:, 0], new[:, 1]] & (act < 4)
            self.pos[idx] = np.where(blocked[:, None], old, new)
            x, y = self.pos[idx, 0], self.pos[idx, 1]

            # signal emission
            sm = act == 6
            sig_n = int(sm.sum())
            if sig_n:
                np.add.at(self.signal, (x[sm], y[sm]), 1.0)
                np.minimum(self.signal, 1.0, out=self.signal)

            if cfg.deposit_share == "contributor":
                self.contrib[idx] *= cfg.contrib_decay

            m = (act == 5) & (self.ttype[x, y] > 0)
            if cfg.deposit_share == "contributor":
                self.contrib[idx[m]] += 1.0
            if m.any():
                np.add.at(self.progress, (x[m], y[m]), 1.0)
                lock = np.where(self.ttype == 1, cfg.lock1, cfg.lock2)
                np.minimum(self.progress, 2.0 * lock, out=self.progress)
                now = (self.ttype > 0) & (self.progress >= lock)
                newly = now & ~self.unlocked
                for tt in (1, 2):
                    k = int((newly & (self.ttype == tt)).sum())
                    if k:
                        self.unlock_events[tt] += k
                        if self.first_unlock[tt] is None:
                            self.first_unlock[tt] = self.t
                self.unlocked = now

            # eating: bigger bodies take a larger share and a larger bite
            cell = x * L + y
            cnt = np.bincount(cell, minlength=L * L).astype(float)
            wsz = np.bincount(cell, weights=size, minlength=L * L)
            tot_c = np.minimum(cfg.eat_rate * wsz, self.commons.ravel())
            self.commons.ravel()[:] -= tot_c
            g_c = tot_c[cell] * size / np.maximum(wsz[cell], 1e-12)

            hr = (np.where(self.ttype == 1, cfg.harvest1,
                           np.where(self.ttype == 2, cfg.harvest2, 0.0))
                  * self._openness()).ravel()
            tot_r = np.minimum(hr * cnt, self.stock.ravel())
            self.stock.ravel()[:] -= tot_r
            w = size * ((self.contrib[idx] + cfg.contrib_floor) if cfg.deposit_share == "contributor" else 1.0)
            W = np.bincount(cell, weights=w, minlength=L * L)
            g_r = tot_r[cell] * w / np.maximum(W[cell], 1e-12)
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

            dead = self.energy[idx] <= 0.0
            if cfg.mortality:
                p_die = cfg.hazard + cfg.danger_hazard * self.danger[x, y]
                dead = dead | (self.rng.random(n) < p_die)
            if dead.any():
                di = idx[dead]
                if cfg.mortality:
                    self.ledger["death_removed"] += float(self.energy[di].sum())
                    self.alive[di] = False
                    deaths = len(di)
                else:
                    self.ledger["bailout"] += float((1.0 - self.energy[di]).sum())
                    self.energy[di] = 1.0

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
        L_["sig"].append(sig_n)

    def _reproduce(self) -> int:
        cfg = self.cfg
        a = np.flatnonzero(self.alive)
        if len(a) == 0:
            return 0
        _size, rep = traits(self.genome[a])
        viable = self.energy[a] >= cfg.repro_cost + 1.0
        if cfg.selection == "persistence":
            ok = self.energy[a] >= cfg.repro_thresh * rep
        elif cfg.selection == "entropy":
            ok = (self.spent_acc[a] >= cfg.entropy_repro_spent) & viable
        elif cfg.selection == "task":
            ok = (self.commons_acc[a] >= cfg.repro_thresh) & viable
        elif cfg.selection == "drift":
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
            if cfg.mut_big_p > 0:
                big = self.rng.random((k, P)) < cfg.mut_big_p
                kids = kids + big * cfg.mut_big_sigma * self.rng.standard_normal((k, P))
        else:
            kids = random_genomes_v2(self.rng, k, cfg.policy)
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
        self.h[s] = 0.0
        self.gen[s] = self.gen[parents] + 1
        self.lineage[s] = self.lineage[parents]
        return k

    def summary(self, passive_rate: float | None = None) -> dict:
        out = super().summary(passive_rate)
        sg = np.asarray(self.log["sig"], dtype=float)
        pop = np.asarray(self.log["pop"], dtype=float)
        T = len(pop)
        w = slice(int(T * 0.75), T)
        out["signal_rate"] = float(sg[w].sum() / max(pop[w].sum(), 1.0))
        # early vs late, to show whether evolution is still moving
        lg = {k: np.asarray(v, dtype=float) for k, v in self.log.items()}
        e = slice(int(T * 0.10), int(T * 0.25))
        ge = lg["gain_c"][e] + lg["gain_1"][e] + lg["gain_2"][e]
        out["entropy_rate_early"] = float((lg["leak"][e] + self.cfg.kappa * lg["heat"][e]).mean())
        out["share_tier2_early"] = float(lg["gain_2"][e].sum() / max(ge.sum(), 1e-12))
        out["gen_mean"] = float(self.gen[self.alive].mean()) if self.alive.any() else float("nan")
        out["n_genes"] = int(self.genome.shape[1])
        if self.alive.any():
            size, rep = traits(self.genome[self.alive])
            out["size_mean"], out["repro_mult_mean"] = float(size.mean()), float(rep.mean())
        else:
            out["size_mean"] = out["repro_mult_mean"] = float("nan")
        return out
