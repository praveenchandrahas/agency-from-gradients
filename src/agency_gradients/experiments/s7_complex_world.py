"""S7 - complex world (v2): ~2,000-gene recurrent policies evolved over many generations.

Question: does a large, prior-free genome (memory, signalling, heritable body traits)
evolve toward using the energy ladder when given enough generations, relative to
(a) random parents, (b) the small chemotaxis-shaped policy on the same world, and
(c) a hand-coded forager (headroom)? See PREREGISTRATION_S7.md.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor

import numpy as np

from ..config import v2_config
from ..controls import oracle_policy
from ..runner import write_csv
from ..stats import bootstrap_diff_ci, bootstrap_mean_ci
from ..world import make_world
from .common import base_parser, emit, fmt

N_WIN = 10
VARIANTS = {
    "recurrent (~2,000 genes)": dict(policy="recurrent"),
    "recurrent, random parents": dict(policy="recurrent", selection="drift"),
    "feed-forward (~1,400 genes)": dict(policy="mlp2"),
    "small chemotaxis policy (29 genes)": dict(policy="equivariant2"),
    "hand-coded forager": dict(policy="equivariant2", _oracle=True),
}
METRICS = ["entropy_rate", "share_tier2", "share_tier1", "t2_reached", "signal_rate", "gen_mean", "pop_mean_late", "extinct"]


def _run(job):
    kw = dict(job["kw"])
    oracle = kw.pop("_oracle", False)
    w = make_world(v2_config(steps=job["steps"], **kw), job["seed"])
    if oracle:
        w.policy = oracle_policy
    w.run()
    row = dict(variant=job["name"], seed=job["seed"])
    row.update(w.summary())
    lg = {k: np.asarray(v, float) for k, v in w.log.items()}
    T = len(lg["pop"])
    for i in range(N_WIN):
        s = slice(i * T // N_WIN, (i + 1) * T // N_WIN)
        row[f"ent_w{i}"] = float((lg["leak"][s] + w.cfg.kappa * lg["heat"][s]).mean())
        g = lg["gain_c"][s] + lg["gain_1"][s] + lg["gain_2"][s]
        row[f"t2share_w{i}"] = float(lg["gain_2"][s].sum() / max(g.sum(), 1e-12))
    return row


def main(argv=None):
    ap = base_parser(__doc__.splitlines()[0])
    ap.add_argument("--long-steps", type=int, default=100_000)
    ap.add_argument("--only", type=str, default=None, help="comma-separated variant name substrings")
    args = ap.parse_args(argv)
    steps = 1500 if args.smoke else args.long_steps
    seeds = list(range(args.seed0, args.seed0 + (2 if args.smoke else args.seeds)))
    names = [n for n in VARIANTS if not args.only or any(o in n for o in args.only.split(","))]
    jobs = [dict(name=n, kw=VARIANTS[n], seed=sd, steps=steps) for n in names for sd in seeds]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        rows = []
        for i, r in enumerate(ex.map(_run, jobs, chunksize=1)):
            rows.append(r)
            print(f"  {i + 1}/{len(jobs)}", flush=True)
    write_csv(rows, f"{args.out}/s7_runs.csv")
    by = {n: [x for x in rows if x["variant"] == n] for n in names}
    L = ["# S7 - complex world (v2)", "", f"seeds: {len(seeds)}, steps: {steps}", "",
         "| variant | " + " | ".join(METRICS) + " |", "|---|" + "---|" * len(METRICS)]
    for n in names:
        L.append(f"| {n} | " + " | ".join(
            "{} [{}, {}]".format(*[fmt(v) for v in bootstrap_mean_ci([x[m] for x in by[n]])]) for m in METRICS) + " |")
    L += ["", "## Contrasts (difference of means, 95% bootstrap CI)", ""]
    R, D, F = "recurrent (~2,000 genes)", "recurrent, random parents", "small chemotaxis policy (29 genes)"
    for a, b, lab in ((R, D, "S7a recurrent - random parents"), (R, F, "S7b recurrent - small policy")):
        if a in by and b in by:
            for m in ("share_tier2", "entropy_rate"):
                d, lo, hi = bootstrap_diff_ci([x[m] for x in by[a]], [x[m] for x in by[b]])
                L.append(f"- {lab} : {m}: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]")
    if R in by:
        d, lo, hi = bootstrap_diff_ci([x[f"t2share_w{N_WIN-1}"] for x in by[R]], [x["t2share_w0"] for x in by[R]])
        L.append(f"- S7c recurrent, last window - first window : tier-2 share: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]")
    emit(L, f"{args.out}/s7_report.md")


if __name__ == "__main__":
    main()
