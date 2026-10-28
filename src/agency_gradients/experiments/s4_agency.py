"""S4 - agency probe: viability restoration, evolved vs random-genome agents.

For each condition, sample agents from the evolved population, displace and
deplete them in a copy of the world with reproduction switched off, and measure
how many get back to a viable energy level within the horizon. The same test is
run on freshly randomised genomes. delta_recovered = evolved - random.

H3: delta_recovered(full) - delta_recovered(no heredity) > 0.

CAUTION - survivorship bias. Agents sampled from a living population have already
passed hazard and starvation filters that fresh random genomes have not, so
delta_recovered is positive even with no inheritance at all (the "no heredity" and
"drift" rows show this). The raw delta is therefore NOT evidence of evolved agency;
only the difference between the full world and the no-heredity world isolates what
accumulated through heredity.

Not measured: prediction / world-modelling. See README roadmap.
"""
from __future__ import annotations

from ..runner import run_jobs, write_csv
from ..stats import bootstrap_diff_ci, bootstrap_mean_ci
from .common import base_config, base_parser, emit, fmt, seeds_of

VARIANTS = {
    "full": {},
    "no heredity": dict(heredity=False),
    "no mortality": dict(mortality=False),
    "abundant (no scarcity)": dict(scarcity=False),
    "drift selection": dict(selection="drift"),
}


def main(argv=None):
    args = base_parser(__doc__.splitlines()[0]).parse_args(argv)
    cfg0 = base_config(args)
    jobs = [dict(cfg=cfg0.with_(**kw), seed=sd, labels=dict(variant=name), probe=True)
            for name, kw in VARIANTS.items() for sd in seeds_of(args)]
    rows = run_jobs(jobs, args.workers)
    write_csv(rows, f"{args.out}/s4_runs.csv")
    ms = ["evolved_recovered", "random_recovered", "delta_recovered", "evolved_survived", "random_survived"]
    L = ["# S4 - agency probe (viability restoration)", "",
         f"seeds: {len(seeds_of(args))}, steps: {cfg0.steps}", "",
         "| variant | " + " | ".join(ms) + " |", "|---|" + "---|" * len(ms)]
    for name in VARIANTS:
        r = [x for x in rows if x["variant"] == name]
        L.append(f"| {name} | " + " | ".join(
            "{} [{}, {}]".format(*[fmt(v) for v in bootstrap_mean_ci([x[m] for x in r])]) for m in ms) + " |")
    d, lo, hi = bootstrap_diff_ci(
        [x["delta_recovered"] for x in rows if x["variant"] == "full"],
        [x["delta_recovered"] for x in rows if x["variant"] == "no heredity"])
    L += ["", "## Pre-registered contrast (H3)", "",
          f"- delta_recovered(full) - delta_recovered(no heredity): {fmt(d)} [{fmt(lo)}, {fmt(hi)}]"]
    emit(L, f"{args.out}/s4_report.md")


if __name__ == "__main__":
    main()
