"""S1 - selection criterion comparison.

Same world, four ways of deciding who reproduces:
  persistence : reproduce when energy surplus allows (the faithful condition)
  entropy     : reproduce by burning energy (entropy used AS a reward - the control
                that the thesis argues against; expected to breed furnaces)
  task        : reproduce by eating commons (a conventional task reward)
  drift       : random-parents births (fecundity selection removed; viability selection remains)

H1: persistence beats drift on entropy_rate without entropy ever being rewarded.
H4: entropy-as-reward does not beat persistence on tier-2 access.
"""
from __future__ import annotations

from ..config import SELECTIONS
from ..runner import run_jobs, write_csv
from ..stats import bootstrap_diff_ci, bootstrap_mean_ci
from .common import base_config, base_parser, emit, fmt, seeds_of

METRICS = ["entropy_rate", "capture_fraction", "capture_ratio", "t2_reached", "share_tier2",
           "share_tier1", "pop_mean_late", "extinct"]


def main(argv=None):
    args = base_parser(__doc__.splitlines()[0]).parse_args(argv)
    cfg0 = base_config(args)
    jobs = [dict(cfg=cfg0.with_(selection=s), seed=sd, labels=dict(selection=s))
            for s in SELECTIONS for sd in seeds_of(args)]
    rows = run_jobs(jobs, args.workers)
    write_csv(rows, f"{args.out}/s1_runs.csv")

    L = ["# S1 - selection criterion comparison", "",
         f"seeds: {len(seeds_of(args))}, steps: {cfg0.steps}", "",
         "| selection | " + " | ".join(METRICS) + " |", "|---|" + "---|" * len(METRICS)]
    for s in SELECTIONS:
        r = [x for x in rows if x["selection"] == s]
        cells = []
        for m in METRICS:
            mean, lo, hi = bootstrap_mean_ci([x[m] for x in r])
            cells.append(f"{fmt(mean)} [{fmt(lo)}, {fmt(hi)}]")
        L.append(f"| {s} | " + " | ".join(cells) + " |")

    def col(sel, m):
        return [x[m] for x in rows if x["selection"] == sel]

    L += ["", "## Pre-registered contrasts (difference of means, 95% bootstrap CI)", ""]
    for name, a, b, m in [
        ("H1  persistence - drift : entropy_rate", "persistence", "drift", "entropy_rate"),
        ("H1  persistence - drift : t2_reached", "persistence", "drift", "t2_reached"),
        ("H4  entropy - persistence : entropy_rate", "entropy", "persistence", "entropy_rate"),
        ("H4  entropy - persistence : t2_reached", "entropy", "persistence", "t2_reached"),
    ]:
        d, lo, hi = bootstrap_diff_ci(col(a, m), col(b, m))
        L.append(f"- {name}: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]")
    emit(L, f"{args.out}/s1_report.md")


if __name__ == "__main__":
    main()
