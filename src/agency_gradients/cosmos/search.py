"""Evaluation and evolution-strategy search for S11 (numpy only)."""
from __future__ import annotations

import numpy as np

from .model import Params, do_nothing, rollout
from .policies import (K_SEG, N_NN, N_PW, NA, NeuralPolicy, PiecewisePolicy, const_policy, mix_theta, pure_theta,
                       staged_theta)

_BASE = {}
NOISE_FLOOR = 1e90


def _key(p: Params, seed):
    return (p.horizon_yr, p.v_probe, p.eta, p.eps_gw, p.bh_mult, p.cost_mult, p.reach_limit, p.domain_mass, p.area_limit,
            p.hawking, p.capture_accretion, p.s_smbh0, p.tau_sf, p.col_mass_per_lsun, p.cost_c, p.cost_b, seed)


def baseline(p: Params, seed: int):
    """p must already be drawn for `seed`."""
    k = _key(p, seed)
    if k not in _BASE:
        r = rollout(p, do_nothing)
        _BASE[k] = r["entropy"]
    return _BASE[k]


def gain_of(p0: Params, policy, seed: int, check=False):
    p = p0.draw(seed)
    base = baseline(p, seed)
    r = rollout(p, policy, check_ledger=check)
    e = r["entropy"]
    g = {k: e[k] - base[k] for k in ("bh", "photon", "matter", "hawking")}
    g["total_raw"] = g["bh"] + g["photon"] + g["matter"] + g["hawking"]
    # float64 resolution of the ~3e104 BH total is ~1e89 kB: smaller differences are numerical noise
    g["total"] = g["total_raw"] if abs(g["total_raw"]) >= NOISE_FLOOR else 0.0
    g["W_final"] = r["W_final"]
    g["abs_total"] = e["total"]
    g["ledger_err"] = r["max_ledger_err"]
    g["cap_hit"] = r["cap_hit"]
    g["kappa"] = r["kappa"]
    g["spent"] = r["spent"]
    return g


def slog(g):
    return float(np.sign(g) * np.log10(1.0 + abs(g)))


def objective(p0: Params, make_policy, theta, seeds):
    vals = []
    for s in seeds:
        g = gain_of(p0, make_policy(theta), s)
        vals.append(slog(g["total"]))
    return float(np.mean(vals))


def centered_ranks(x):
    r = np.empty(len(x)); r[np.argsort(x)] = np.arange(len(x))
    return r / (len(x) - 1) - 0.5


def es(fobj, theta0, gens, pairs, sigma, lr, rng, verbose=False):
    """Antithetic OpenAI-style ES with centred ranks; returns the best candidate ever seen (elitist) and the curve."""
    theta = np.array(theta0, float)
    best, bestv = theta.copy(), fobj(theta)
    curve = [bestv]
    P = len(theta)
    for g in range(gens):
        eps = rng.standard_normal((pairs, P))
        cand = [theta + sg * sigma * e for e in eps for sg in (1.0, -1.0)]
        F = np.array([fobj(c) for c in cand])
        j = int(np.argmax(F))
        if F[j] > bestv:
            bestv, best = float(F[j]), cand[j].copy()
        r = centered_ranks(F).reshape(pairs, 2)
        theta = theta + lr * ((r[:, 0] - r[:, 1])[:, None] * eps).sum(0) / pairs
        curve.append(bestv)
        if verbose:
            print(f"  gen {g}: best {bestv:.2f}", flush=True)
    return best, curve


def grid_strategies():
    names = ["star_formation", "funnel_gas", "merge_holes", "collapse_remnants", "collectors"]
    nth = np.zeros((K_SEG, NA)); nth[:, 5] = 6.0
    out = {"nothing": nth.ravel()}
    for j, n in enumerate(names):
        out[f"only_{n}"] = pure_theta(j)
    for a in range(5):
        for b in range(a + 1, 5):
            w = np.zeros(5); w[a] = w[b] = 1.0
            out[f"mix_{names[a]}+{names[b]}"] = mix_theta(w)
    for a in (1, 2):
        out[f"staged_collectors_then_{names[a]}"] = staged_theta(4, a)
    w = np.array([0, 1, 1, 0, 1.0]); out["mix_funnel+merge+collectors"] = mix_theta(w)
    w = np.array([0, 1, 1, 1, 1.0]); out["mix_funnel+merge+collapse+collectors"] = mix_theta(w)
    out["equal_all"] = mix_theta(np.ones(5))
    return out


def phase_a(p0: Params, train_seeds, rng, gens=40, pairs=12, sigma=0.8, lr=0.5, mask=(1, 1, 1, 1, 1), verbose=False):
    """Grid over named strategies, then ES refinement from the best grid point. Returns (name, theta, grid_table)."""
    mk = lambda th: PiecewisePolicy(th, mask)
    table = {}
    for name, th in grid_strategies().items():
        if name.startswith(("only_", "mix_", "staged_")):
            # skip strategies using disabled levers entirely
            pass
        table[name] = objective(p0, mk, th, train_seeds)
    bestname = max(table, key=table.get)
    th0 = grid_strategies()[bestname]
    fobj = lambda th: objective(p0, mk, th, train_seeds)
    th, curve = es(fobj, th0, gens, pairs, sigma, lr, rng, verbose)
    return bestname, th, table, curve


def phase_b(p0: Params, train_seeds, rng, gens=60, pairs=24, sigma=0.3, lr=0.3, mask=(1, 1, 1, 1, 1), verbose=False):
    mk = lambda th: NeuralPolicy(th, mask)
    th0 = rng.standard_normal(N_NN) * 0.3
    fobj = lambda th: objective(p0, mk, th, train_seeds)
    return es(fobj, th0, gens, pairs, sigma, lr, rng, verbose)
