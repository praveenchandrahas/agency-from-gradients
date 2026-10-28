"""S2 - factorial ablation of the candidate initial conditions (the core experiment).

Factors (each on/off): scarcity, heredity, mortality, succession  -> 16 conditions.
The gradient ladder itself is held fixed: it defines the tier-ascent metric, so
removing it would make the outcome true by construction (see S3 for the
no-ladder control).

H2: tier-2 access (t2_reached) requires scarcity, heredity and mortality; removing
    any one lowers it (CI excludes 0). Succession is two-sided, no directional claim.
"""
from __future__ import annotations

from ..config import FACTORS
from ..runner import run_jobs, write_csv
from ..stats import bootstrap_diff_ci, bootstrap_mean_ci, factor_effect
from .common import base_config, base_parser, emit, factorial, fmt, seeds_of

METRICS = ["t2_reached", "share_tier2", "entropy_rate", "capture_fraction", "pop_mean_late", "extinct"]


def main(argv=None):
    args = base_parser(__doc__.splitlines()[0]).parse_args(argv)
    cfg0 = base_config(args)
    jobs = []
    for cond in factorial(FACTORS):
        for sd in seeds_of(args):
            jobs.append(dict(cfg=cfg0.with_(**cond), seed=sd,
                             labels={k: int(v) for k, v in cond.items()}))
    rows = run_jobs(jobs, args.workers)
    write_csv(rows, f"{args.out}/s2_runs.csv")

    L = ["# S2 - factorial ablation", "",
         f"seeds per condition: {len(seeds_of(args))}, steps: {cfg0.steps}, conditions: 16", "",
         "## Main effects (on minus off, averaged over the other factors; 95% bootstrap CI)", "",
         "| factor | " + " | ".join(METRICS) + " |", "|---|" + "---|" * len(METRICS)]
    for f in FACTORS:
        cells = []
        for m in METRICS:
            e, lo, hi = factor_effect(rows, f, m, FACTORS, n_boot=1000)
            cells.append(f"{fmt(e)} [{fmt(lo)}, {fmt(hi)}]")
        L.append(f"| {f} | " + " | ".join(cells) + " |")

    def sel(**kw):
        return [r for r in rows if all(r[k] == int(v) for k, v in kw.items())]

    all_on = dict(scarcity=1, heredity=1, mortality=1, succession=1)
    L += ["", "## All-on vs leave-one-out (H2)", "",
          "Difference in t2_reached (all-on minus one factor off); positive = factor helped.", ""]
    base = [r["t2_reached"] for r in sel(**all_on)]
    for f in FACTORS:
        flipped = dict(all_on, **{f: 0})
        d, lo, hi = bootstrap_diff_ci(base, [r["t2_reached"] for r in sel(**flipped)])
        L.append(f"- {f} off: {fmt(d)} [{fmt(lo)}, {fmt(hi)}]")

    L += ["", "## Per-condition table", "",
          "| " + " | ".join(FACTORS) + " | t2_reached | entropy_rate | pop |", "|" + "---|" * (len(FACTORS) + 3)]
    for cond in factorial(FACTORS):
        r = sel(**cond)
        L.append("| " + " | ".join(str(int(v)) for v in cond.values()) + " | "
                 + " | ".join(fmt(bootstrap_mean_ci([x[m] for x in r])[0]) for m in
                              ("t2_reached", "entropy_rate", "pop_mean_late")) + " |")
    emit(L, f"{args.out}/s2_report.md")


if __name__ == "__main__":
    main()
