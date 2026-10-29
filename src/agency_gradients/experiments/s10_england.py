"""S10 - dissipative adaptation inside our world, with no selection at all.

No births, no deaths, no fitness. A dissipation-biased rearrangement rule is the only thing that
changes policies (see world_learn.EnglandWorld). Arms: absorbed, dissipated, neutral (drift
control), anti (opposite bias), plus the hand-coded forager as headroom. See PREREGISTRATION_S10.md.
Run:     python -m agency_gradients.experiments.s10_england --seed0 0 --seeds 10 --only absorbed --out out
Analyse: python -m agency_gradients.experiments.s10_england --analyze DIR --out out
"""
from __future__ import annotations

import glob
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from ..config import v2_config
from ..controls import oracle_policy
from ..runner import write_csv
from ..stats import bootstrap_diff_ci, bootstrap_mean_ci
from ..world import make_world
from .common import base_parser, emit, fmt

STEPS = 100_000
WORLD = dict(policy="equivariant2", mortality=False, day_night=True, field_drift_every=400)
ARMS = {"absorbed": dict(england="absorbed"), "dissipated": dict(england="dissipated"),
        "neutral": dict(england="neutral"), "anti": dict(england="anti"),
        "forager": dict(_oracle=True)}
METRICS = ["intake_late", "intake_early", "share_tier2_late", "share_tier1_late", "entropy_rate", "eng_accept"]


def _run(job):
    kw = dict(job["kw"])
    oracle = kw.pop("_oracle", False)
    w = make_world(v2_config(scale=job["scale"], steps=job["steps"], **WORLD, **kw), job["seed"])
    if oracle:
        w.policy = oracle_policy
    w.run()
    lg = {k: np.asarray(v, float) for k, v in w.log.items()}
    T = len(lg["pop"])
    late, early = slice(int(T * 0.75), T), slice(int(T * 0.10), int(T * 0.25))
    g = lg["gain_c"] + lg["gain_1"] + lg["gain_2"]
    row = dict(arm=job["name"], seed=job["seed"])
    row.update(w.summary())
    row["intake_late"] = float(g[late].sum() / max(lg["pop"][late].sum(), 1.0))
    row["intake_early"] = float(g[early].sum() / max(lg["pop"][early].sum(), 1.0))
    row["share_tier2_late"] = float(lg["gain_2"][late].sum() / max(g[late].sum(), 1e-12))
    row["share_tier1_late"] = float(lg["gain_1"][late].sum() / max(g[late].sum(), 1e-12))
    row.setdefault("eng_accept", float("nan"))
    return row


def analyze(rows, out):
    names = list(ARMS)
    by = {n: [r for r in rows if r["arm"] == n] for n in names}
    L = ["# S10 results", "", "runs: " + ", ".join(f"{n}={len(by[n])}" for n in names), "",
         "| arm | " + " | ".join(METRICS) + " |", "|---|" + "---|" * len(METRICS)]
    for n in names:
        if by[n]:
            cells = []
            for m in METRICS:
                v = [x[m] for x in by[n] if not np.isnan(x[m])]
                cells.append("{} [{}, {}]".format(*[fmt(q) for q in bootstrap_mean_ci(v)]) if v else "n/a")
            L.append(f"| {n} | " + " | ".join(cells) + " |")
    L += ["", "## Preregistered contrasts (difference of means, 95% bootstrap CI; supported = lower bound > 0)", ""]
    spec = (("H10a absorbed - neutral: intake_late", "absorbed", "neutral", "intake_late"),
            ("H10b dissipated - neutral: intake_late", "dissipated", "neutral", "intake_late"),
            ("H10c absorbed - anti: intake_late", "absorbed", "anti", "intake_late"),
            ("H10d absorbed - neutral: share_tier2_late", "absorbed", "neutral", "share_tier2_late"))
    for lab, a, b, m in spec:
        if len(by[a]) > 1 and len(by[b]) > 1:
            d, lo, hi = bootstrap_diff_ci([x[m] for x in by[a]], [x[m] for x in by[b]])
            L.append(f"- {lab}: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]  -> {'SUPPORTED' if lo > 0 else 'NOT supported'}")
    L += ["", "## Descriptive", ""]
    for a, b, m in (("dissipated", "neutral", "share_tier2_late"), ("forager", "absorbed", "intake_late"),
                    ("absorbed", "neutral", "share_tier1_late")):
        if len(by[a]) > 1 and len(by[b]) > 1:
            d, lo, hi = bootstrap_diff_ci([x[m] for x in by[a]], [x[m] for x in by[b]])
            L.append(f"- {a} - {b} {m}: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]")
    emit(L, f"{out}/s10_report.md")


def main(argv=None):
    ap = base_parser(__doc__.splitlines()[0])
    ap.add_argument("--only", type=str, default=None)
    ap.add_argument("--analyze", type=str, default=None)
    ap.add_argument("--scale", type=int, default=1)
    ap.add_argument("--long-steps", type=int, default=STEPS)
    args = ap.parse_args(argv)
    if args.analyze:
        import csv
        rows = []
        for f in sorted(glob.glob(f"{args.analyze}/**/s10_runs*.csv", recursive=True)):
            for r in csv.DictReader(open(f)):
                rows.append({k: (v if k == "arm" else (1.0 if v == "True" else 0.0 if v == "False" else float(v)))
                             for k, v in r.items()})
        write_csv(rows, f"{args.out}/s10_runs_all.csv")
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
    write_csv(rows, f"{args.out}/s10_runs_{tag}.csv")


if __name__ == "__main__":
    main()
