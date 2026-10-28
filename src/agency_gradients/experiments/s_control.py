"""Positive control: hand-coded forager vs evolved-from-random vs neutral drift.

Not an experiment about agency. It shows the headroom the world offers, so that a
null result from evolution can be read as "search did not get there" and not "the
world cannot reward it".
"""
from __future__ import annotations

from ..controls import oracle_policy
from ..runner import write_csv
from ..stats import bootstrap_mean_ci
from ..world import World
from .common import base_config, base_parser, emit, fmt, seeds_of

METRICS = ["entropy_rate", "capture_fraction", "share_tier1", "share_tier2", "t2_reached", "pop_mean_late"]


def main(argv=None):
    args = base_parser(__doc__.splitlines()[0]).parse_args(argv)
    cfg0 = base_config(args)
    rows = []
    for name, kw, pol in [("oracle (hand-coded)", {}, oracle_policy),
                          ("evolved from random", {}, None),
                          ("neutral drift", dict(selection="drift"), None)]:
        for sd in seeds_of(args):
            w = World(cfg0.with_(**kw), sd)
            w.policy = pol
            w.run()
            r = dict(variant=name, seed=sd)
            r.update(w.summary())
            rows.append(r)
    write_csv(rows, f"{args.out}/control_runs.csv")
    L = ["# Positive control", "", f"seeds: {len(seeds_of(args))}, steps: {cfg0.steps}", "",
         "| variant | " + " | ".join(METRICS) + " |", "|---|" + "---|" * len(METRICS)]
    for name in ("oracle (hand-coded)", "evolved from random", "neutral drift"):
        r = [x for x in rows if x["variant"] == name]
        L.append(f"| {name} | " + " | ".join(
            "{} [{}, {}]".format(*[fmt(v) for v in bootstrap_mean_ci([x[m] for x in r])]) for m in METRICS) + " |")
    emit(L, f"{args.out}/control_report.md")


if __name__ == "__main__":
    main()
