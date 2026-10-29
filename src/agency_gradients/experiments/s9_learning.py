"""S9 - engineered reward: does a private entropy/energy reward, learned within a lifetime, produce agency?

Arms (identical world, selection = persistence in all): off (no learning), energy (learn from own
energy change), heat (learn from own heat dissipation = an explicit private entropy reward).
Agency criteria (fixed in PREREGISTRATION_S9.md): predictive probe (does the hidden state predict
the agent's own future energy gain beyond its observation?) and the viability probe.
Run:     python -m agency_gradients.experiments.s9_learning --seed0 0 --seeds 5 --only energy --out out
Analyse: python -m agency_gradients.experiments.s9_learning --analyze DIR --out out
"""
from __future__ import annotations

import glob
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from ..config import v2_config
from ..probes import predictive_probe, viability_probe
from ..runner import write_csv
from ..stats import bootstrap_diff_ci, bootstrap_mean_ci
from ..world import make_world
from .common import base_parser, emit, fmt

SCALE, STEPS = 2, 100_000
ARMS = {"off": dict(plastic="off"), "energy": dict(plastic="energy"), "heat": dict(plastic="heat")}
WORLD = dict(policy="recurrent")      # plain v2 (seasons, walls, danger, signal): v3 extinguished every pilot run
METRICS = ["entropy_rate", "share_tier2", "t2_reached", "gen_mean", "pop_mean_late", "extinct",
           "delta_recovered", "pred_dr2_evolved", "pred_dr2_random", "pred_delta"]


def _run(job):
    cfg = v2_config(scale=job["scale"], steps=job["steps"], **WORLD, **job["kw"])
    w = make_world(cfg, job["seed"]).run()
    row = dict(arm=job["name"], seed=job["seed"])
    row.update(w.summary())
    row.update(viability_probe(w, seed=job["seed"]))
    row.update(predictive_probe(w, seed=job["seed"]))
    return row


def analyze(rows, out):
    names = list(ARMS)
    by = {n: [r for r in rows if r["arm"] == n] for n in names}
    ok = {n: [r for r in by[n] if not np.isnan(r["pred_delta"])] for n in names}
    L = ["# S9 results", "", "runs: " + ", ".join(f"{n}={len(by[n])} (valid probes {len(ok[n])})" for n in names), "",
         "| arm | " + " | ".join(METRICS) + " |", "|---|" + "---|" * len(METRICS)]
    for n in names:
        if by[n]:
            cells = []
            for m in METRICS:
                v = [x[m] for x in by[n] if not np.isnan(x[m])]
                cells.append("{} [{}, {}]".format(*[fmt(q) for q in bootstrap_mean_ci(v)]) if v else "n/a")
            L.append(f"| {n} | " + " | ".join(cells) + " |")
    L += ["", "## Preregistered contrasts (difference of means over runs with valid probes, 95% bootstrap CI)", ""]
    spec = (("H9a energy - off: pred_delta  (>0 supports)", "energy", "off", "pred_delta", +1),
            ("H9b heat - off: pred_delta  (>0 supports)", "heat", "off", "pred_delta", +1),
            ("H9c energy - off: delta_recovered  (>0 supports)", "energy", "off", "delta_recovered", +1),
            ("H9d heat - energy: delta_recovered  (<0 supports)", "heat", "energy", "delta_recovered", -1))
    for lab, a, b, m, sgn in spec:
        xa = [r[m] for r in ok[a] if not np.isnan(r[m])]
        xb = [r[m] for r in ok[b] if not np.isnan(r[m])]
        if len(xa) > 1 and len(xb) > 1:
            d, lo, hi = bootstrap_diff_ci(xa, xb)
            sup = (lo > 0) if sgn > 0 else (hi < 0)
            L.append(f"- {lab}: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]  -> {'SUPPORTED' if sup else 'NOT supported'}  (n={len(xa)} vs {len(xb)})")
        else:
            L.append(f"- {lab}: too few valid runs ({len(xa)} vs {len(xb)})")
    L += ["", "## Secondary (descriptive, all runs)", ""]
    for a, b in (("energy", "off"), ("heat", "off"), ("heat", "energy")):
        for m in ("entropy_rate", "share_tier2", "extinct"):
            if by[a] and by[b]:
                d, lo, hi = bootstrap_diff_ci([x[m] for x in by[a]], [x[m] for x in by[b]])
                L.append(f"- {a} - {b} {m}: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]")
    emit(L, f"{out}/s9_report.md")


def main(argv=None):
    ap = base_parser(__doc__.splitlines()[0])
    ap.add_argument("--only", type=str, default=None)
    ap.add_argument("--analyze", type=str, default=None)
    ap.add_argument("--scale", type=int, default=SCALE)
    ap.add_argument("--long-steps", type=int, default=STEPS)
    args = ap.parse_args(argv)
    if args.analyze:
        import csv
        rows = []
        for f in sorted(glob.glob(f"{args.analyze}/**/s9_runs*.csv", recursive=True)):
            for r in csv.DictReader(open(f)):
                rows.append({k: (v if k == "arm" else (1.0 if v == "True" else 0.0 if v == "False" else float(v)))
                             for k, v in r.items()})
        write_csv(rows, f"{args.out}/s9_runs_all.csv")
        return analyze(rows, args.out)
    steps, scale = (1500, 1) if args.smoke else (args.long_steps, args.scale)
    seeds = list(range(args.seed0, args.seed0 + (2 if args.smoke else args.seeds)))
    names = [n for n in ARMS if not args.only or n in args.only.split(",")]
    jobs = [dict(name=n, kw=ARMS[n], seed=sd, steps=steps, scale=scale) for n in names for sd in seeds]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        rows = []
        for i, r in enumerate(ex.map(_run, jobs, chunksize=1)):
            rows.append(r)
            print(f"  {i + 1}/{len(jobs)}", flush=True)
    tag = f"{names[0]}_{args.seed0}" if len(names) == 1 else f"all_{args.seed0}"
    write_csv(rows, f"{args.out}/s9_runs_{tag}.csv")


if __name__ == "__main__":
    main()
