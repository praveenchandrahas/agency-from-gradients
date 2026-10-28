"""S8 - what happens when total entropy IS the objective?

Everything so far rewarded persistence. Here we do the opposite, on purpose: a
shared controller ("species genome") is optimised directly for the world's total
entropy production, with evolution strategies (random perturbations of the genome,
keep what scores higher). Life forms eat and scavenge leftover energy exactly as in
the main world; nothing else is rewarded. We then look at *what behaviour* that
objective produces.

Two cautions, stated up front (also in the README):
  * entropy = leaked energy + kappa x energy dissipated by agents. kappa > 1 is an
    ASSUMPTION, so "capture energy and burn it" scores higher by construction.
    kappa = 1 is the control: entropy is then almost fixed by the energy inflow.
  * a single shared controller removes the free-rider problem seen in S2/S6.
Controllers are evaluated with common random numbers inside a generation.
"""
from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from ..config import Config
from ..controls import oracle_policy
from ..runner import write_csv
from ..stats import bootstrap_mean_ci
from ..world import World, n_params, random_genomes
from .common import base_parser, emit, fmt

BURN = 400


def _cfg(kappa: float, policy: str) -> Config:
    # fixed population, no births, no extrinsic hazard: starvation is the only death
    return Config(kappa=kappa, policy=policy, hazard=0.0, init_pop=60)


def always_invest(obs, rng):
    return np.full(len(obs), 5)


def random_move(obs, rng):
    return rng.integers(0, 4, len(obs))


def run_episode(theta, cfg: Config, seed: int, steps: int, policy_fn=None, n_agents=None, kappa_eval=None):
    w = World(cfg, seed, n_agents=n_agents)
    w.reproduce = False
    if theta is not None:
        w.genome[:] = theta
    w.policy = policy_fn
    counts = np.zeros(6)
    inner = w._act

    def spy(idx, obs):
        a = inner(idx, obs)
        counts[:] += np.bincount(a, minlength=6)
        return a

    w._act = spy
    for _ in range(steps):
        w.step()
    lg = {k: np.asarray(v, float) for k, v in w.log.items()}
    sl = slice(min(BURN, steps // 5), None)
    k = cfg.kappa if kappa_eval is None else kappa_eval
    ent = lg["leak"][sl] + k * lg["heat"][sl]
    gain = lg["gain_c"][sl] + lg["gain_1"][sl] + lg["gain_2"][sl]
    g = max(gain.sum(), 1e-12)
    tot = max(counts.sum(), 1.0)
    return dict(
        fitness=float(ent.mean()),
        entropy_k3=float((lg["leak"][sl] + 3.0 * lg["heat"][sl]).mean()),
        entropy_k1=float((lg["leak"][sl] + lg["heat"][sl]).mean()),
        leak_share=float(lg["leak"][sl].sum() / max(lg["leak"][sl].sum() + lg["heat"][sl].sum(), 1e-12)),
        capture_fraction=float(gain.sum() / max(gain.sum() + lg["leak"][sl].sum(), 1e-12)),
        share_commons=float(lg["gain_c"][sl].sum() / g),
        share_tier1=float(lg["gain_1"][sl].sum() / g),
        share_tier2=float(lg["gain_2"][sl].sum() / g),
        pop_late=float(lg["pop"][sl].mean()),
        t2_reached=int(w.unlock_events[2] > 0),
        act_move=float(counts[:4].sum() / tot), act_stay=float(counts[4] / tot), act_invest=float(counts[5] / tot),
        stock_late=float((w.stock.sum())),
    )


def _eval_job(job):
    return run_episode(job["theta"], job["cfg"], job["seed"], job["steps"])["fitness"]


def centered_ranks(x):
    r = np.empty(len(x))
    r[np.argsort(x)] = np.arange(len(x))
    return r / (len(x) - 1) - 0.5


def evolve(cfg, es_seed, gens, pairs, sigma, lr, steps, ex):
    rng = np.random.default_rng(es_seed)
    P = n_params(cfg.policy)
    theta = random_genomes(rng, 1, cfg.policy)[0]
    curve = []
    for g in range(gens):
        eps = rng.standard_normal((pairs, P))
        env_seed = 10_000 + es_seed * 1000 + g          # common random numbers within a generation
        jobs = [dict(theta=theta + s * sigma * e, cfg=cfg, seed=env_seed, steps=steps)
                for e in eps for s in (1.0, -1.0)]
        F = np.array(list(ex.map(_eval_job, jobs, chunksize=1))).reshape(pairs, 2)
        r = centered_ranks(F.ravel()).reshape(pairs, 2)
        theta = theta + lr * ((r[:, 0] - r[:, 1])[:, None] * eps).sum(0) / pairs
        curve.append(float(F.mean()))
    return theta, curve


def main(argv=None):
    ap = base_parser(__doc__.splitlines()[0])
    ap.add_argument("--gens", type=int, default=40)
    ap.add_argument("--pairs", type=int, default=12)
    ap.add_argument("--sigma", type=float, default=0.4)
    ap.add_argument("--lr", type=float, default=0.3)
    ap.add_argument("--ep-steps", type=int, default=2000)
    ap.add_argument("--policy", type=str, default="equivariant")
    ap.add_argument("--kappas", type=str, default="3,1")
    args = ap.parse_args(argv)
    gens, pairs, ep = (2, 2, 300) if args.smoke else (args.gens, args.pairs, args.ep_steps)
    n_es = 2 if args.smoke else args.seeds
    eval_seeds = list(range(5000, 5000 + (2 if args.smoke else 8)))
    kappas = [float(k) for k in args.kappas.split(",")]
    rows, curves = [], {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for kappa in kappas:
            cfg = _cfg(kappa, args.policy)
            for i in range(n_es):
                es_seed = args.seed0 + i
                theta, curve = evolve(cfg, es_seed, gens, pairs, args.sigma, args.lr, ep, ex)
                curves[f"kappa{kappa:g}_s{es_seed}"] = curve
                print(f"  kappa={kappa:g} ES run {i + 1}/{n_es}: {curve[0]:.1f} -> {curve[-1]:.1f}", flush=True)
                res = [run_episode(theta, cfg, s, 2 * ep) for s in eval_seeds]
                row = dict(condition=f"optimised, kappa={kappa:g}", es_seed=es_seed)
                row.update({k: float(np.mean([r[k] for r in res])) for k in res[0]})
                rows.append(row)
                np.save(f"{args.out}/theta_kappa{kappa:g}_s{es_seed}.npy", theta) if _mk(args.out) else None
            # baselines (no optimisation), evaluated under the same kappa
            cfgb = _cfg(kappa, args.policy)
            base = {
                "random controller": lambda s: run_episode(random_genomes(np.random.default_rng(s), 1, args.policy)[0], cfgb, s, 2 * ep),
                "hand-coded forager": lambda s: run_episode(None, cfgb, s, 2 * ep, policy_fn=oracle_policy),
                "always invest": lambda s: run_episode(None, cfgb, s, 2 * ep, policy_fn=always_invest),
                "always move": lambda s: run_episode(None, cfgb, s, 2 * ep, policy_fn=random_move),
                "no life forms": lambda s: run_episode(None, cfgb, s, 2 * ep, n_agents=0),
            }
            for name, fn in base.items():
                res = [fn(s) for s in eval_seeds]
                row = dict(condition=f"{name}, kappa={kappa:g}", es_seed=-1)
                row.update({k: float(np.mean([r[k] for r in res])) for k in res[0]})
                rows.append(row)
    write_csv(rows, f"{args.out}/s8_runs.csv")
    with open(f"{args.out}/s8_curves.json", "w") as f:
        json.dump(curves, f)
    cols = ["fitness", "entropy_k3", "capture_fraction", "leak_share", "share_tier1", "share_tier2", "t2_reached",
            "act_move", "act_stay", "act_invest", "pop_late"]
    L = ["# S8 - total entropy as the objective", "", f"ES runs per kappa: {n_es}, generations: {gens}, "
         f"pairs: {pairs}, episode steps: {ep}, policy: {args.policy}", "",
         "| condition | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    conds = list(dict.fromkeys(r["condition"] for r in rows))
    for c in conds:
        rs = [r for r in rows if r["condition"] == c]
        cells = []
        for m in cols:
            v = [r[m] for r in rs]
            cells.append("{} [{}, {}]".format(*[fmt(x) for x in bootstrap_mean_ci(v)]) if len(v) > 2 else fmt(np.mean(v)))
        L.append(f"| {c} | " + " | ".join(cells) + " |")
    # pre-registered contrasts (PREREGISTRATION_S8.md): bootstrap over ES runs
    L += ["", "## Pre-registered contrasts (mean over ES runs, 95% bootstrap CI)", ""]

    def opt(k):
        return [r for r in rows if r["condition"] == f"optimised, kappa={k:g}"]

    def base(name, k):
        return [r for r in rows if r["condition"] == f"{name}, kappa={k:g}"][0]

    def line(label, vals):
        m, lo, hi = bootstrap_mean_ci(vals)
        L.append(f"- {label}: {fmt(m)} [{fmt(lo)}, {fmt(hi)}]")

    if 3.0 in kappas:
        line("H8a  optimised - hand-coded forager (kappa=3), entropy rate", [r["fitness"] - base("hand-coded forager", 3)["fitness"] for r in opt(3)])
        line("H8b  optimised - hand-coded forager (kappa=3), share of actions spent investing", [r["act_invest"] - base("hand-coded forager", 3)["act_invest"] for r in opt(3)])
    if 3.0 in kappas and 1.0 in kappas:
        g3 = [r["fitness"] - base("random controller", 3)["fitness"] for r in opt(3)]
        g1 = [r["fitness"] - base("random controller", 1)["fitness"] for r in opt(1)]
        rng = np.random.default_rng(0)
        diffs = [np.mean(rng.choice(g3, len(g3))) - np.mean(rng.choice(g1, len(g1))) for _ in range(4000)]
        L.append(f"- H8c  gain over random controller, kappa=3 minus kappa=1: {fmt(np.mean(g3) - np.mean(g1))} "
                 f"[{fmt(np.percentile(diffs, 2.5))}, {fmt(np.percentile(diffs, 97.5))}]")
    emit(L, f"{args.out}/s8_report.md")


def _mk(path):
    import os
    os.makedirs(path, exist_ok=True)
    return True


if __name__ == "__main__":
    main()
