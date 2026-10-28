"""Make the README figures from the CSVs written by the experiments.

    python analysis/make_figures.py --results results/confirmatory --out figures

Every figure is skipped, not faked, if its CSV is missing. Dots are individual runs
(one per seed); markers with bars are means with 95% bootstrap CIs.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from agency_gradients.stats import bootstrap_diff_ci, bootstrap_mean_ci, factor_effect  # noqa: E402

SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898780", "#e6e4de"
BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6"
SEL = {"persistence": BLUE, "entropy": ORANGE, "task": AQUA, "drift": MUTED,
       "oracle (hand-coded)": VIOLET, "evolved from random": BLUE, "neutral drift": MUTED}
NICE = {"persistence": "Survival only\n(persistence)", "entropy": "Rewarded for\nburning energy", "task": "Rewarded for\neating grass",
        "drift": "No selection\n(neutral)", "oracle (hand-coded)": "Hand-coded\nforager", "evolved from random": "Evolved\nfrom random",
        "neutral drift": "No selection\n(neutral)"}
FACTORS = ("scarcity", "heredity", "mortality", "succession")
FACTOR_NICE = {"scarcity": "Food is scarce", "heredity": "Children inherit instincts", "mortality": "Starvation is fatal", "succession": "Big deposits form where small run dry"}

plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "font.size": 10,
                     "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
                     "lines.linewidth": 2})


def load(path):
    if not os.path.exists(path):
        return None
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            for k, v in r.items():
                try:
                    r[k] = float(v)
                except ValueError:
                    pass
            rows.append(r)
    return rows


def col(rows, key, **filt):
    return [r[key] for r in rows if all(r[k] == v for k, v in filt.items()) and not (isinstance(r[key], float) and np.isnan(r[key]))]


def save(fig, out, name):
    fig.savefig(os.path.join(out, name), dpi=170, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def dotci(ax, x, vals, color, jitter=0.09, seed=0):
    rng = np.random.default_rng(seed + int(x * 10))
    ax.scatter(x + rng.uniform(-jitter, jitter, len(vals)), vals, s=14, color=color, alpha=0.35, linewidths=0, zorder=2)
    m, lo, hi = bootstrap_mean_ci(vals)
    ax.errorbar([x], [m], yerr=[[m - lo], [hi - m]], fmt="o", color=color, ecolor=color, capsize=4, markersize=7,
                markeredgecolor=SURF, markeredgewidth=1.5, zorder=4)


def fig_selection(rows, out, name, order, title, metrics):
    fig, axes = plt.subplots(1, len(metrics), figsize=(4.0 * len(metrics), 4.1), squeeze=False)
    for ax, (key, label) in zip(axes[0], metrics):
        for i, s in enumerate(order):
            dotci(ax, i, col(rows, key, **{"selection" if "selection" in rows[0] else "variant": s}), SEL[s])
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels([NICE[s] for s in order], fontsize=8.5)
        ax.set_title(label, loc="left", fontsize=11, color=INK)
        ax.grid(axis="x", visible=False)
        ax.set_xlim(-0.5, len(order) - 0.5)
    fig.suptitle(title, x=0.01, ha="left", fontsize=12.5, y=1.02)
    save(fig, out, name)


def forest(ax, items, xlabel, title):
    ys = np.arange(len(items))[::-1]
    for y, (lab, e, lo, hi) in zip(ys, items):
        sig = lo > 0 or hi < 0
        ax.errorbar([e], [y], xerr=[[e - lo], [hi - e]], fmt="o", color=BLUE if sig else MUTED, ecolor=BLUE if sig else MUTED,
                    capsize=4, markersize=7, markeredgecolor=SURF, markeredgewidth=1.5)
    ax.axvline(0, color=INK2, linewidth=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([i[0] for i in items], fontsize=9)
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.grid(axis="y", visible=False)


def fig_s2_effects(rows, out):
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 3.6), sharey=True)
    for ax, (m, xl, t) in zip(axes, [("t2_reached", "change in share of runs reaching big deposits", "Reaching big deposits"),
                                      ("entropy_rate", "change in entropy rate", "Entropy production"),
                                      ("pop_mean_late", "change in creatures alive", "Population")]):
        items = []
        for f in FACTORS:
            e, lo, hi = factor_effect(rows, f, m, FACTORS, n_boot=2000)
            items.append((FACTOR_NICE[f], e, lo, hi))
        forest(ax, items, xl, t)
    fig.suptitle("Effect of switching each condition on (vs off), averaged over the others. Blue = 95% interval excludes zero.", x=0.01, ha="left", fontsize=11.5, y=1.04)
    save(fig, out, "s2_main_effects.png")


def fig_s2_loo(rows, out):
    allon = dict(scarcity=1.0, heredity=1.0, mortality=1.0, succession=1.0)
    base = col(rows, "t2_reached", **allon)
    items = []
    for f in FACTORS:
        flip = dict(allon, **{f: 0.0})
        d, lo, hi = bootstrap_diff_ci(base, col(rows, "t2_reached", **flip))
        items.append((f"{FACTOR_NICE[f]}: remove it", d, lo, hi))
    fig, ax = plt.subplots(figsize=(7.4, 3.2))
    forest(ax, items, "share of runs reaching big deposits: all conditions on, minus one removed", "Is each condition needed? (H2)")
    save(fig, out, "s2_leave_one_out.png")


def fig_s2_heatmap(rows, out):
    rs = [(1, 1), (1, 0), (0, 1), (0, 0)]
    cs = [(1, 1), (1, 0), (0, 1), (0, 0)]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.1))
    for ax, (m, t, cmap) in zip(axes, [("t2_reached", "Share of runs reaching big deposits", "Blues"), ("entropy_rate", "Entropy production rate", "Blues")]):
        M = np.zeros((4, 4))
        for i, (sc, he) in enumerate(rs):
            for j, (mo, su) in enumerate(cs):
                v = col(rows, m, scarcity=float(sc), heredity=float(he), mortality=float(mo), succession=float(su))
                M[i, j] = np.mean(v) if v else np.nan
        im = ax.imshow(M, cmap=cmap, vmin=0 if m == "t2_reached" else None, vmax=1 if m == "t2_reached" else None, aspect="auto")
        for i in range(4):
            for j in range(4):
                v = M[i, j]
                dark = (v - np.nanmin(M)) / (np.nanmax(M) - np.nanmin(M) + 1e-9) > 0.55 if m != "t2_reached" else v > 0.55
                ax.text(j, i, f"{v:.2f}" if m == "t2_reached" else f"{v:.1f}", ha="center", va="center", color="white" if dark else INK, fontsize=10)
        ax.set_xticks(range(4))
        ax.set_xticklabels([f"{'fatal' if mo else 'safe'}\n{'succession' if su else 'no succ.'}" for mo, su in cs], fontsize=8.5)
        ax.set_yticks(range(4))
        ax.set_yticklabels([f"{'scarce' if sc else 'abundant'}, {'inherit' if he else 'no inherit'}" for sc, he in rs], fontsize=8.5)
        ax.set_title(t, loc="left", fontsize=11, color=INK)
        ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.suptitle("All 16 combinations of the four conditions", x=0.01, ha="left", fontsize=12.5, y=1.02)
    save(fig, out, "s2_heatmap.png")


def fig_s3(rows, out):
    order = ["full ladder (kappa=3)", "full ladder (kappa=1, sanity)", "no ladder (commons only)", "ladder, no succession"]
    labs = ["Full ladder\n(kappa 3)", "Full ladder\n(kappa 1, check)", "No ladder\n(grass only)", "Ladder,\nno succession"]
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.9))
    for ax, (m, t) in zip(axes, [("capture_fraction", "Share of energy used (not wasted)"), ("entropy_rate", "Entropy production rate"), ("capture_ratio", "Capture ratio (assumption-dependent)")]):
        for i, v in enumerate(order):
            dotci(ax, i, col(rows, m, variant=v), BLUE if i != 1 else MUTED)
        ax.set_xticks(range(4))
        ax.set_xticklabels(labs, fontsize=8.5)
        ax.set_title(t, loc="left", fontsize=11, color=INK)
        ax.grid(axis="x", visible=False)
    axes[2].axhline(1.0, color=INK2, linewidth=1, linestyle="--")
    fig.suptitle("Accounting checks and the no-ladder control", x=0.01, ha="left", fontsize=12.5, y=1.02)
    save(fig, out, "s3_accounting.png")


def fig_s4(rows, out):
    order = ["full", "no heredity", "no mortality", "abundant (no scarcity)", "drift selection"]
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    for i, v in enumerate(order[::-1]):
        vals = col(rows, "delta_recovered", variant=v)
        rng = np.random.default_rng(i)
        ax.scatter(vals, i + rng.uniform(-0.12, 0.12, len(vals)), s=14, color=BLUE, alpha=0.3, linewidths=0)
        m, lo, hi = bootstrap_mean_ci(vals)
        ax.errorbar([m], [i], xerr=[[m - lo], [hi - m]], fmt="o", color=BLUE, capsize=4, markersize=7, markeredgecolor=SURF, markeredgewidth=1.5)
    ax.axvline(0, color=INK2, linewidth=1)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order[::-1])
    ax.set_xlabel("evolved minus random-genome agents that recover after being displaced and starved")
    ax.set_title("Recovery after displacement (raw gap includes survivorship bias)", loc="left", fontsize=11, color=INK)
    ax.grid(axis="y", visible=False)
    d, lo, hi = bootstrap_diff_ci(col(rows, "delta_recovered", variant="full"), col(rows, "delta_recovered", variant="no heredity"))
    ax.text(0.99, 0.04, f"H3: full minus no-heredity = {d:.3f} [{lo:.3f}, {hi:.3f}]", transform=ax.transAxes, ha="right", fontsize=9, color=INK2)
    save(fig, out, "s4_recovery.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results/confirmatory")
    ap.add_argument("--out", default="figures")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    r = lambda n: load(os.path.join(a.results, n))
    s1, s2, s3, s4, ctl = r("s1_runs.csv"), r("s2_runs.csv"), r("s3_runs.csv"), r("s4_runs.csv"), r("control_runs.csv")
    if s1:
        fig_selection(s1, a.out, "s1_selection.png", ["persistence", "entropy", "task", "drift"],
                      "Four ways of deciding who has children, same world",
                      [("entropy_rate", "Entropy production rate"), ("t2_reached", "Reached big deposits (share of runs)"), ("share_tier2", "Energy from big deposits (share)")])
    if ctl:
        fig_selection(ctl, a.out, "control.png", ["oracle (hand-coded)", "evolved from random", "neutral drift"],
                      "Headroom check: what a hand-coded forager can do in this world",
                      [("entropy_rate", "Entropy production rate"), ("t2_reached", "Reached big deposits (share of runs)"), ("share_tier2", "Energy from big deposits (share)")])
    if s2:
        fig_s2_effects(s2, a.out); fig_s2_loo(s2, a.out); fig_s2_heatmap(s2, a.out)
    if s3:
        fig_s3(s3, a.out)
    if s4:
        fig_s4(s4, a.out)


if __name__ == "__main__":
    main()
