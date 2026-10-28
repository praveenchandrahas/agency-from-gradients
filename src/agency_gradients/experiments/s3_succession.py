"""S3 - passive baseline, no-ladder control and accounting sanity checks.

Runs each configuration with agents and compares against the SAME environment with
no agents (the denominator of the Capture Ratio).

IMPORTANT: Capture Ratio here is largely a bookkeeping identity. Agents are
*assumed* to dissipate energy at kappa entropy-units per energy against 1 for
passive leakage, so CR > 1 follows from capture_fraction and kappa. The row with
kappa = 1 is the sanity check: CR must collapse towards 1. The empirical content
of this experiment is capture_fraction and the tier shares, not CR itself.
"""
from __future__ import annotations

from ..runner import run_jobs, write_csv
from ..stats import bootstrap_mean_ci
from .common import base_config, base_parser, emit, fmt, seeds_of

VARIANTS = {
    "full ladder (kappa=3)": {},
    "full ladder (kappa=1, sanity)": dict(kappa=1.0),
    "no ladder (commons only)": dict(n_tier1=0, n_tier2=0),
    "ladder, no succession": dict(succession=False),
}
METRICS = ["capture_fraction", "entropy_rate", "capture_ratio", "share_tier1", "share_tier2", "pop_mean_late"]


def main(argv=None):
    args = base_parser(__doc__.splitlines()[0]).parse_args(argv)
    cfg0 = base_config(args)
    jobs = [dict(cfg=cfg0.with_(**kw), seed=sd, labels=dict(variant=name))
            for name, kw in VARIANTS.items() for sd in seeds_of(args)]
    rows = run_jobs(jobs, args.workers)
    write_csv(rows, f"{args.out}/s3_runs.csv")
    L = ["# S3 - passive baseline and ladder control", "",
         f"seeds: {len(seeds_of(args))}, steps: {cfg0.steps}", "",
         "| variant | " + " | ".join(METRICS) + " |", "|---|" + "---|" * len(METRICS)]
    for name in VARIANTS:
        r = [x for x in rows if x["variant"] == name]
        L.append(f"| {name} | " + " | ".join(
            "{} [{}, {}]".format(*[fmt(v) for v in bootstrap_mean_ci([x[m] for x in r])]) for m in METRICS) + " |")
    emit(L, f"{args.out}/s3_report.md")


if __name__ == "__main__":
    main()
