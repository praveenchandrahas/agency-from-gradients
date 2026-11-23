"""S15 analysis. Written and frozen with locks/PREREGISTRATION.md, before the confirmatory run.

Reads every run JSON under a directory and writes RESULTS.md and summary.json.
Intervals: 95% percentile bootstrap over seeds, 10,000 resamples, paired by seed.

    PYTHONPATH=. python analysis/report.py <results dir> <RESULTS.md>
"""
from __future__ import annotations

import glob
import json
import os
import sys

import numpy as np

B_GRID = (0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0)
N_BITS = (24, 32)
COLD = 16.0
NB = 10_000
H2C_TOL = 0.02
H2E_MAX = 0.10
RNG = np.random.default_rng(15)


def load(d):
    runs = {}
    for p in glob.glob(os.path.join(d, "**", "*.json"), recursive=True):
        base = os.path.basename(p)
        if base.startswith(("match_", "summary")):
            continue
        with open(p) as f:
            r = json.load(f)
        if "label" not in r:
            continue
        key = (r["label"], r["config"]["n_bits"], r["config"]["B"][0])
        runs.setdefault(key, {})[r["seed"]] = r
    return runs


def vec(runs, arm, nb, B, w=-1, field="sigma"):
    cell = runs.get((arm, nb, B), {})
    seeds = sorted(cell)
    return seeds, np.array([cell[s]["windows"][w][field] if field != "spent"
                            else cell[s]["windows"][w]["spent"][0] for s in seeds], float)


def boot_mean(x):
    x = np.asarray(x, float)
    if len(x) == 0:
        return (np.nan, np.nan, np.nan)
    idx = RNG.integers(0, len(x), size=(NB, len(x)))
    m = x[idx].mean(axis=1)
    return (float(x.mean()), float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975)))


def paired(runs, a, b, nb, B, w=-1, ratio=False):
    sa, xa = vec(runs, a, nb, B, w)
    sb, xb = vec(runs, b, nb, B, w)
    common = sorted(set(sa) & set(sb))
    xa = np.array([xa[sa.index(s)] for s in common])
    xb = np.array([xb[sb.index(s)] for s in common])
    if ratio:
        return boot_mean(xa / xb)
    return boot_mean(xa - xb)


def fmt(t, d=1):
    m, lo, hi = t
    if np.isnan(m):
        return "n/a"
    return f"{m:.{d}f} [{lo:.{d}f}, {hi:.{d}f}]"


def above(t):   # interval lies above zero
    return t[1] > 0


def slope_ci(runs, nb, w=-1):
    """OLS slope over B of the per-seed advantage L - max(M, D). Seeds resampled jointly."""
    seeds = None
    A = []
    for B in B_GRID:
        sl, xl = vec(runs, "L", nb, B, w)
        sm, xm = vec(runs, "M", nb, B, w)
        sd, xd = vec(runs, "D", nb, B, w)
        common = sorted(set(sl) & set(sm) & set(sd))
        seeds = common if seeds is None else sorted(set(seeds) & set(common))
        A.append({s: xl[sl.index(s)] - max(xm[sm.index(s)], xd[sd.index(s)]) for s in common})
    if not seeds:
        return (np.nan, np.nan, np.nan)
    M = np.array([[a[s] for a in A] for s in seeds])          # seeds x B
    Bv = np.array(B_GRID)
    Bc = Bv - Bv.mean()

    def slope(rows):
        y = rows.mean(axis=0)
        return float((Bc * (y - y.mean())).sum() / (Bc ** 2).sum())

    idx = RNG.integers(0, len(seeds), size=(NB, len(seeds)))
    bs = np.array([slope(M[i]) for i in idx])
    return (slope(M), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975)))


def verdict_hyp(runs, nb, w=-1):
    v = {}
    dn = paired(runs, "D", "N", nb, COLD, w)
    ln = paired(runs, "L", "N", nb, COLD, w)
    v["H1"] = dict(D_minus_N=dn, L_minus_N=ln, supported=above(dn) and above(ln))
    lm = paired(runs, "L", "M", nb, COLD, w)
    ld = paired(runs, "L", "D", nb, COLD, w)
    v["H2a"] = dict(L_minus_M=lm, L_minus_D=ld, supported=above(lm) and above(ld))
    sl = slope_ci(runs, nb, w)
    v["H2b"] = dict(slope=sl, supported=sl[1] > 0)
    h2c = {}
    ok = True
    for x in ("M", "D", "L"):
        t = paired(runs, x, "N", nb, 0.0, w, ratio=True)
        t = (t[0] - 1, t[1] - 1, t[2] - 1)
        h2c[x] = t
        ok = ok and (t[1] > -H2C_TOL and t[2] < H2C_TOL)
    v["H2c"] = dict(rel_diff=h2c, supported=ok)
    worst = None
    ok = True
    for B in B_GRID:
        t = paired(runs, "L", "U", nb, B, w)
        if t[1] > 0:
            ok = False
        if worst is None or t[0] > worst[1][0]:
            worst = (B, t)
    v["H2d"] = dict(max_L_minus_U=worst, supported=ok)
    h2e = {}
    status = []
    for x in ("D", "M"):
        t = paired(runs, x, "U", nb, COLD, w, ratio=True)
        h2e[x] = t
        status.append("supported" if t[2] < H2E_MAX else "not supported" if t[1] > H2E_MAX else "inconclusive")
    v["H2e"] = dict(ratio_to_U=h2e, status=dict(zip(("D", "M"), status)),
                    supported=all(s == "supported" for s in status))
    # overall, as preregistered
    if not v["H2c"]["supported"]:
        core = "model broken (H2c failed): nothing else here counts"
    elif not v["H2a"]["supported"] and not v["H2b"]["supported"]:
        core = "the narrow claim fails in this model"
    elif v["H2a"]["supported"] and v["H2b"]["supported"] and v["H2e"]["supported"]:
        core = "the narrow claim is supported in this model"
    elif v["H2a"]["supported"] and v["H2b"]["supported"]:
        core = "life does better, but something else also opens the lock: 'nothing else does' fails"
    else:
        core = "mixed"
    v["core"] = core
    return v


def main(d, out_md):
    runs = load(d)
    lines = ["# S15, Locks: results", "",
             "Computed by `analysis/report.py` from the run files. Predictions and decision rules: `PREREGISTRATION.md`.",
             "Intervals are 95% bootstrap intervals on seed means (10,000 resamples), paired by seed.",
             "Entropy production σ is in k_B per residence time: reactions plus mixing.",
             "Primary window: residence times 3,500 to 4,000. Secondary: 1,500 to 2,000.", ""]
    summary = {}
    for nb in N_BITS:
        if not any(k[1] == nb for k in runs):
            continue
        summary[nb] = {}
        lines += [f"## Key length {nb}", ""]
        for wi, wname in ((-1, "primary"), (0, "secondary")):
            v = verdict_hyp(runs, nb, wi)
            summary[nb][wname] = v
            lines += [f"### Verdicts, {wname} window", "",
                      f"**Overall: {v['core']}.**", "",
                      "| | Test | Result | Verdict |", "|---|---|---|---|",
                      f"| H1 | D − N and L − N at B = 16, above 0 | {fmt(v['H1']['D_minus_N'])}; {fmt(v['H1']['L_minus_N'])} | {'Supported' if v['H1']['supported'] else 'Not supported'} |",
                      f"| H2a | L − M and L − D at B = 16, above 0 | {fmt(v['H2a']['L_minus_M'])}; {fmt(v['H2a']['L_minus_D'])} | {'Supported' if v['H2a']['supported'] else 'Not supported'} |",
                      f"| H2b | Slope over B of L − max(M, D), above 0 | {fmt(v['H2b']['slope'], 2)} per kT | {'Supported' if v['H2b']['supported'] else 'Not supported'} |",
                      f"| H2c | At B = 0, M, D, L within ±{H2C_TOL:.0%} of N | " + "; ".join(f"{x} {fmt(t, 4)}" for x, t in v['H2c']['rel_diff'].items()) + f" | {'Supported' if v['H2c']['supported'] else 'Not supported'} |",
                      f"| H2d | L − U never above 0 | largest at B = {v['H2d']['max_L_minus_U'][0]:g}: {fmt(v['H2d']['max_L_minus_U'][1])} | {'Supported' if v['H2d']['supported'] else 'Not supported'} |",
                      f"| H2e | At B = 16, D/U and M/U below {H2E_MAX:.2f} | D {fmt(v['H2e']['ratio_to_U']['D'], 3)} ({v['H2e']['status']['D']}); M {fmt(v['H2e']['ratio_to_U']['M'], 3)} ({v['H2e']['status']['M']}) | {'Supported' if v['H2e']['supported'] else 'Not supported'} |",
                      ""]
        # sigma by arm and B, both windows
        for wi, wname in ((-1, "primary"), (0, "secondary")):
            lines += [f"### σ by arm and barrier, {wname} window", "",
                      "| arm | " + " | ".join(f"B = {B:g}" for B in B_GRID) + " |",
                      "|---|" + "---|" * len(B_GRID)]
            for arm in ("N", "M", "D", "L", "U"):
                lines.append(f"| {arm} | " + " | ".join(fmt(boot_mean(vec(runs, arm, nb, B, wi)[1]), 0) for B in B_GRID) + " |")
            lines.append("")
        lines += ["### Fuel spent, primary window", "",
                  "| arm | " + " | ".join(f"B = {B:g}" for B in B_GRID) + " |", "|---|" + "---|" * len(B_GRID)]
        for arm in ("N", "M", "D", "L", "U"):
            lines.append(f"| {arm} | " + " | ".join(f"{np.mean(vec(runs, arm, nb, B, -1, 'spent')[1]):.3f}"
                                                   if len(vec(runs, arm, nb, B)[1]) else "n/a" for B in B_GRID) + " |")
        lines += ["", "### Catalyst count, primary window", "",
                  "| arm | " + " | ".join(f"B = {B:g}" for B in B_GRID) + " |", "|---|" + "---|" * len(B_GRID)]
        for arm in ("D", "L", "M"):
            lines.append(f"| {arm} | " + " | ".join(f"{np.mean(vec(runs, arm, nb, B, -1, 'n')[1]):.0f}"
                                                   if len(vec(runs, arm, nb, B)[1]) else "n/a" for B in B_GRID) + " |")
        # R1 extinctions
        lines += ["", "### R1. Extinct worlds (of seeds run)", "",
                  "| arm | " + " | ".join(f"B = {B:g}" for B in B_GRID) + " |", "|---|" + "---|" * len(B_GRID)]
        for arm in ("D", "L"):
            row = []
            for B in B_GRID:
                cell = runs.get((arm, nb, B), {})
                row.append(f"{sum(r['extinct'] for r in cell.values())} of {len(cell)}")
            lines.append(f"| {arm} | " + " | ".join(row) + " |")
        # R2 sheltering: key distance against neutral marker distance, L
        lines += ["", "### R2. Key against neutral marker, arm L, end of run", "",
                  "Mean Hamming distance to the lock (key) and to a random fixed target (marker). Marker drift is the neutral baseline.", "",
                  "| B | key distance | marker distance | marker − key |", "|---|---|---|---|"]
        for B in B_GRID:
            cell = runs.get(("L", nb, B), {})
            pairs = [(r["windows"][-1].get("key_dist"), r["windows"][-1].get("marker_dist")) for r in cell.values()]
            pairs = [p for p in pairs if p[0] is not None and p[1] is not None]
            if not pairs:
                lines.append(f"| {B:g} | extinct | extinct | n/a |")
                continue
            k = np.array([p[0] for p in pairs]); m = np.array([p[1] for p in pairs])
            lines.append(f"| {B:g} | {k.mean():.2f} | {m.mean():.2f} | {fmt(boot_mean(m - k), 2)} |")
        # library sweep
        lines += ["", f"### Equivalent library at B = {COLD:g} (secondary)", "",
                  "Mineral arms with 1x, 10x and 100x the matched count, against L.", "",
                  "| arm | σ | σ − L |", "|---|---|---|"]
        for arm in ("M", "M10", "M100"):
            if runs.get((arm, nb, COLD)):
                lines.append(f"| {arm} | {fmt(boot_mean(vec(runs, arm, nb, COLD)[1]), 0)} | {fmt(paired(runs, arm, 'L', nb, COLD), 0)} |")
        lines.append("")
    with open(out_md, "w") as f:
        f.write("\n".join(lines) + "\n")

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(x) for k, x in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(x) for x in o]
        if isinstance(o, (np.floating, np.bool_)):
            return o.item()
        return o
    with open(os.path.join(os.path.dirname(out_md) or ".", "summary.json"), "w") as f:
        json.dump(clean(summary), f, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
