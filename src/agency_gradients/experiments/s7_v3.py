"""S7-v3 - the combined confirmatory comparison (see PREREGISTRATION_S7.md).

World v3 = v2 + day/night, drifting resource field, wandering danger. All variants
share the same world, recombination, mutation rates and population settings.
Run:      python -m agency_gradients.experiments.s7_v3 --seed0 0 --seeds 5 --only "A:" --out out
Analyse:  python -m agency_gradients.experiments.s7_v3 --analyze DIR_WITH_CSVS --out out
"""
from __future__ import annotations

import glob
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from ..config import v3_config
from ..controls import oracle_policy
from ..runner import write_csv
from ..stats import bootstrap_diff_ci, bootstrap_mean_ci
from ..world import make_world
from .common import base_parser, emit, fmt

N_WIN = 10
SCALE, STEPS = 3, 200_000
VARIANTS = {
    "A: recurrent:48 (~5,300 genes)": dict(policy="recurrent:48"),
    "B: recurrent:48, random parents": dict(policy="recurrent:48", selection="drift"),
    "C: small policy (29 genes)": dict(policy="equivariant2", day_night=True),
    "D: hand-coded forager": dict(policy="equivariant2", day_night=True, _oracle=True),
}
METRICS = ["entropy_rate", "share_tier2", "share_tier1", "t2_reached", "signal_rate", "gen_mean", "pop_mean_late", "extinct"]


def _run(job):
    kw = dict(job["kw"])
    oracle = kw.pop("_oracle", False)
    w = make_world(v3_config(scale=job["scale"], steps=job["steps"], **kw), job["seed"])
    if oracle:
        w.policy = oracle_policy
    w.run()
    row = dict(variant=job["name"], seed=job["seed"])
    row.update(w.summary())
    lg = {k: np.asarray(v, float) for k, v in w.log.items()}
    T = len(lg["pop"])
    for i in range(N_WIN):
        s = slice(i * T // N_WIN, (i + 1) * T // N_WIN)
        g = lg["gain_c"][s] + lg["gain_1"][s] + lg["gain_2"][s]
        row[f"t2share_w{i}"] = float(lg["gain_2"][s].sum() / max(g.sum(), 1e-12))
    return row


def analyze(rows, out):
    names = list(VARIANTS)
    by = {n: [r for r in rows if r["variant"] == n] for n in names}
    L = ["# S7-v3 confirmatory results", "", "n per variant: " + ", ".join(f"{n.split(':')[0]}={len(by[n])}" for n in names), "",
         "| variant | " + " | ".join(METRICS) + " |", "|---|" + "---|" * len(METRICS)]
    for n in names:
        if by[n]:
            L.append(f"| {n} | " + " | ".join("{} [{}, {}]".format(*[fmt(v) for v in bootstrap_mean_ci([x[m] for x in by[n]])]) for m in METRICS) + " |")
    A, B, C = names[0], names[1], names[2]
    L += ["", "## Preregistered contrasts (difference of means, 95% bootstrap CI)", ""]
    for lab, a, b in (("H7a A - B (selection vs random parents)", A, B), ("H7b A - C (large genome vs small policy)", A, C)):
        if by[a] and by[b]:
            d, lo, hi = bootstrap_diff_ci([x["share_tier2"] for x in by[a]], [x["share_tier2"] for x in by[b]])
            L.append(f"- {lab}: share_tier2: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]  -> {'SUPPORTED' if lo > 0 else 'NOT supported'}")
    if by[A]:
        d, lo, hi = bootstrap_diff_ci([x[f"t2share_w{N_WIN-1}"] for x in by[A]], [x["t2share_w0"] for x in by[A]])
        L.append(f"- H7c A last window - first window: tier-2 share: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]  -> {'SUPPORTED' if lo > 0 else 'NOT supported'}")
    L += ["", "## Secondary (descriptive)", ""]
    for lab, a, b in (("A - B", A, B), ("A - C", A, C)):
        if by[a] and by[b]:
            for m in ("entropy_rate", "gen_mean", "signal_rate"):
                d, lo, hi = bootstrap_diff_ci([x[m] for x in by[a]], [x[m] for x in by[b]])
                L.append(f"- {lab} {m}: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]")
    emit(L, f"{out}/s7_v3_report.md")


def main(argv=None):
    ap = base_parser(__doc__.splitlines()[0])
    ap.add_argument("--only", type=str, default=None)
    ap.add_argument("--analyze", type=str, default=None)
    args = ap.parse_args(argv)
    if args.analyze:
        import csv
        rows = []
        for f in sorted(glob.glob(f"{args.analyze}/**/s7_v3_runs*.csv", recursive=True)):
            for r in csv.DictReader(open(f)):
                rows.append({k: (v if k == "variant" else (1.0 if v == "True" else 0.0 if v == "False" else float(v)))
                             for k, v in r.items()})
        write_csv(rows, f"{args.out}/s7_v3_runs_all.csv")
        return analyze(rows, args.out)
    steps, scale = (1500, 1) if args.smoke else (STEPS, SCALE)
    seeds = list(range(args.seed0, args.seed0 + (2 if args.smoke else args.seeds)))
    names = [n for n in VARIANTS if not args.only or any(o in n for o in args.only.split(","))]
    jobs = [dict(name=n, kw=VARIANTS[n], seed=sd, steps=steps, scale=scale) for n in names for sd in seeds]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        rows = []
        for i, r in enumerate(ex.map(_run, jobs, chunksize=1)):
            rows.append(r)
            print(f"  {i + 1}/{len(jobs)}", flush=True)
    tag = f"{names[0][0]}_{args.seed0}" if len(names) == 1 else f"all_{args.seed0}"
    write_csv(rows, f"{args.out}/s7_v3_runs_{tag}.csv")


if __name__ == "__main__":
    main()
