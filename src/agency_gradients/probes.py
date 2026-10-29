"""Agency probes.

``viability_probe`` is the operational form of "agency" used in this repo: can an
agent that has been displaced and depleted get itself back to a viable energy
state? The same test is run on (a) agents sampled from the evolved population and
(b) freshly initialised random-genome agents, in a copy of the same environment.
The difference between the two is the evidence; either number alone is not.

Limits (also in the README): this measures goal-less *viability restoration*. It
does not measure prediction or world-modelling. Predictive information is on the
roadmap, not implemented.
"""
from __future__ import annotations

import numpy as np

from .world import World, random_genomes


def viability_probe(world: World, n: int = 64, horizon: int = 150, seed: int = 0) -> dict:
    donors = np.flatnonzero(world.alive)
    if len(donors) == 0:
        return dict(evolved_recovered=np.nan, random_recovered=np.nan,
                    evolved_survived=np.nan, random_survived=np.nan, delta_recovered=np.nan)
    cfg = world.cfg
    rng = np.random.default_rng(seed)
    e0 = 0.5 * cfg.repro_thresh
    res = {}
    for label in ("evolved", "random"):
        w = world.clone_environment()
        w.reproduce = False
        w.rng = np.random.default_rng(rng.integers(2**63))
        if label == "evolved":
            g = world.genome[rng.choice(donors, n, replace=True)].copy()
        else:
            g = random_genomes(rng, n, cfg.policy)
        k = w.spawn(g, rng.integers(0, cfg.size, (n, 2)), np.full(n, e0))
        for _ in range(horizon):
            w.step()
        a = w.alive
        res[f"{label}_survived"] = float(a.sum()) / k
        res[f"{label}_recovered"] = float((a & (w.energy >= e0)).sum()) / k
    res["delta_recovered"] = res["evolved_recovered"] - res["random_recovered"]
    return res


def _record(w, steps: int):
    """Run w for `steps` steps recording, per step, (agent ids, observation, hidden state, energy change)."""
    rec = []
    orig_act, orig_post = w._act, w._post_step
    cur = {}

    def act(idx, obs):
        a = orig_act(idx, obs)
        cur["x"] = (idx.copy(), obs.copy(), w.h[idx].copy())
        return a

    def post(idx, gain, cost):
        orig_post(idx, gain, cost)
        i, o, h = cur["x"]
        rec.append((i, o, h, gain - cost))

    w._act, w._post_step = act, post
    for _ in range(steps):
        w.step()
    return rec


def _ridge_r2(Xtr, ytr, Xte, yte, lam=1.0) -> float:
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    A = (Xtr - mu) / sd
    B = (Xte - mu) / sd
    ym = ytr.mean()
    beta = np.linalg.solve(A.T @ A + lam * len(A) * np.eye(A.shape[1]), A.T @ (ytr - ym))
    pred = B @ beta + ym
    ss = ((yte - yte.mean()) ** 2).sum()
    if not np.isfinite(ss) or ss < 1e-9:
        return float("nan")
    return float(np.clip(1.0 - ((yte - pred) ** 2).sum() / ss, -1.0, 1.0))


def _predictive_dr2(rec, horizon: int, rng) -> float:
    """Does the agent's hidden state predict its own future energy gain (next `horizon` steps)
    better than its current observation alone? Returns R2(obs, h) - R2(obs) on held-out agents."""
    T = len(rec)
    if T <= horizon + 1:
        return float("nan")
    m = max(int(r[0].max()) for r in rec if len(r[0])) + 1
    R = np.full((T, m), np.nan)
    Hn = rec[0][2].shape[1]
    for t, (i, _o, _h, r) in enumerate(rec):
        R[t, i] = r
    X_o, X_h, y, who = [], [], [], []
    cs = np.nancumsum(np.nan_to_num(R, nan=0.0), axis=0)
    ok = (~np.isnan(R)).astype(int).cumsum(axis=0)
    for t in range(T - horizon):
        i, o, h, _r = rec[t]
        full = (ok[t + horizon - 1, i] - (ok[t - 1, i] if t else 0)) == horizon
        if not full.any():
            continue
        i2 = i[full]
        tot = cs[t + horizon - 1, i2] - (cs[t - 1, i2] if t else 0)
        X_o.append(o[full]); X_h.append(h[full]); y.append(tot); who.append(i2)
    if not y:
        return float("nan")
    X_o, X_h, y, who = map(np.concatenate, (X_o, X_h, y, who))
    agents = np.unique(who)
    if len(agents) < 8 or len(y) < 200:
        return float("nan")
    test_ag = rng.choice(agents, len(agents) // 2, replace=False)
    te = np.isin(who, test_ag)
    Xb = np.concatenate([X_o, X_h], axis=1)
    sub = rng.choice(np.flatnonzero(~te), min(20000, int((~te).sum())), replace=False)
    subt = rng.choice(np.flatnonzero(te), min(20000, int(te.sum())), replace=False)
    r_obs = _ridge_r2(X_o[sub], y[sub], X_o[subt], y[subt])
    r_both = _ridge_r2(Xb[sub], y[sub], Xb[subt], y[subt])
    return r_both - r_obs


def predictive_probe(world, steps: int = 300, horizon: int = 20, n_random: int = 64, seed: int = 0) -> dict:
    """Predictive-information probe (roadmap item, now implemented).

    Continue the evolved/trained population for `steps` steps without births, record each agent's
    observation, hidden state and energy change, and ask whether the hidden state predicts the
    agent's own energy gain over the next `horizon` steps beyond what the current observation
    already predicts (held-out agents, linear ridge). The same is done for freshly drawn random
    genomes in a copy of the same environment, because even a random recurrent net carries some
    memory. The difference is the evidence. Limits: linear read-out; a forward model of ITS OWN
    energy gain, not of the world; correlational, not a proof of internal modelling.
    """
    import copy
    if not world.alive.any() or world.h.shape[1] == 0:
        return dict(pred_dr2_evolved=np.nan, pred_dr2_random=np.nan, pred_delta=np.nan)
    rng = np.random.default_rng(seed)
    w = copy.deepcopy(world)
    w.reproduce = False
    w.rng = np.random.default_rng(rng.integers(2**63))
    ev = _predictive_dr2(_record(w, steps), horizon, rng)
    w2 = world.clone_environment()
    w2.reproduce = False
    w2.rng = np.random.default_rng(rng.integers(2**63))
    from .policies_v2 import random_genomes_v2
    k = w2.spawn(random_genomes_v2(rng, n_random, world.cfg.policy), rng.integers(0, world.cfg.size, (n_random, 2)),
                 np.full(n_random, 0.5 * world.cfg.repro_thresh))
    rd = _predictive_dr2(_record(w2, steps), horizon, rng)
    return dict(pred_dr2_evolved=ev, pred_dr2_random=rd, pred_delta=ev - rd)
