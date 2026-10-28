"""S6 - is the H2 failure a free-rider problem?

In S1-S5 the benefit of an opened deposit is split evenly among everyone standing
on it, so investing is a public good. Here, in `deposit_share="contributor"`, the
benefit is split in proportion to each agent's recent investment (a decaying
trace), so investors keep most of what they open. Everything else is the full
world (scarcity, mortality, succession on). Heredity is crossed with the sharing
rule, so we can ask whether heredity becomes load-bearing once investing pays
privately. See PREREGISTRATION_S6.md.
"""
from __future__ import annotations

from ..runner import run_jobs, write_csv
from ..stats import bootstrap_diff_ci, bootstrap_mean_ci
from .common import base_config, base_parser, emit, fmt, seeds_of

VARIANTS = {
    "equal, heredity": dict(deposit_share="equal", heredity=True),
    "equal, no heredity": dict(deposit_share="equal", heredity=False),
    "contributor, heredity": dict(deposit_share="contributor", heredity=True),
    "contributor, no heredity": dict(deposit_share="contributor", heredity=False),
}
METRICS = ["t2_reached", "share_tier1", "share_tier2", "entropy_rate", "capture_fraction", "pop_mean_late"]


def main(argv=None):
    args = base_parser(__doc__.splitlines()[0]).parse_args(argv)
    cfg0 = base_config(args)
    jobs = [dict(cfg=cfg0.with_(**kw), seed=sd, labels=dict(variant=name))
            for name, kw in VARIANTS.items() for sd in seeds_of(args)]
    rows = run_jobs(jobs, args.workers)
    write_csv(rows, f"{args.out}/s6_runs.csv")
    L = ["# S6 - private benefit of opening deposits", "",
         f"seeds: {len(seeds_of(args))}, steps: {cfg0.steps}", "",
         "| variant | " + " | ".join(METRICS) + " |", "|---|" + "---|" * len(METRICS)]
    by = {n: [x for x in rows if x["variant"] == n] for n in VARIANTS}
    for name in VARIANTS:
        L.append(f"| {name} | " + " | ".join(
            "{} [{}, {}]".format(*[fmt(v) for v in bootstrap_mean_ci([x[m] for x in by[name]])]) for m in METRICS) + " |")
    L += ["", "## Pre-registered contrasts (difference of means, 95% bootstrap CI)", ""]

    def c(label, a, b, m):
        d, lo, hi = bootstrap_diff_ci([x[m] for x in by[a]], [x[m] for x in by[b]])
        L.append(f"- {label} : {m}: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]")

    for m in ("t2_reached", "share_tier2"):
        c("H6a  contributor - equal (heredity on)", "contributor, heredity", "equal, heredity", m)
    for m in ("t2_reached", "share_tier2"):
        c("H6b  heredity - no heredity (contributor)", "contributor, heredity", "contributor, no heredity", m)
    emit(L, f"{args.out}/s6_report.md")


if __name__ == "__main__":
    main()
