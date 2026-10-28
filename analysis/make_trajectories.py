"""Example trajectories and world snapshots (illustration, not a test).

Runs a handful of seeds per condition and plots rolling entropy production and the
share of energy from big deposits, plus three snapshots of one world. Seeds 0-4
only; the confirmatory statistics live in the experiment CSVs.
"""
from __future__ import annotations

import argparse
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from make_figures import AQUA, BLUE, GRID, INK, INK2, MUTED, SURF, VIOLET, save  # noqa: E402,F401
from agency_gradients import Config, World  # noqa: E402
from agency_gradients.controls import oracle_policy  # noqa: E402

CONDS = [("Survival only (evolving)", dict(selection="persistence"), None, BLUE),
         ("No selection (neutral)", dict(selection="drift"), None, MUTED),
         ("Hand-coded forager", dict(selection="persistence"), oracle_policy, VIOLET)]


def rolling(x, w):
    c = np.cumsum(np.insert(x, 0, 0.0))
    out = (c[w:] - c[:-w]) / w
    return np.concatenate([np.full(w - 1, np.nan), out])


def run(cfg, seed, policy):
    w = World(cfg, seed)
    w.policy = policy
    snaps = {0: snapshot(w)}
    w.run()
    snaps[cfg.steps] = snapshot(w)
    lg = {k: np.asarray(v, float) for k, v in w.log.items()}
    ent = lg["leak"] + cfg.kappa * lg["heat"]
    gain = lg["gain_c"] + lg["gain_1"] + lg["gain_2"]
    return rolling(ent, 2000), rolling(lg["gain_2"], 2000) / np.maximum(rolling(gain, 2000), 1e-9), snaps, w


def snapshot(w):
    return dict(commons=w.commons.copy(), ttype=w.ttype.copy(), open=np.where(w.ttype > 0, np.minimum(w.progress / np.where(w.ttype == 1, w.cfg.lock1, w.cfg.lock2), 1), 0),
                stock=w.stock.copy(), pos=w.pos[w.alive].copy(), energy=w.energy[w.alive].copy(), t=w.t)


def draw_snapshot(ax, s, cfg, title):
    L = cfg.size
    ax.imshow(s["commons"], cmap="Greens", vmin=0, vmax=1.3, interpolation="nearest")
    for (x, y) in np.argwhere(s["ttype"] == 1):
        live = s["stock"][x, y] > cfg.depletedAt
        ax.scatter([y], [x], marker="s", s=60, facecolors="none", edgecolors="#c98500" if live else MUTED, linewidths=1.6)
    for (x, y) in np.argwhere(s["ttype"] == 2):
        ax.scatter([y], [x], marker="D", s=150, facecolors=VIOLET if s["open"][x, y] > 0.5 else "none", edgecolors=VIOLET, linewidths=1.8, alpha=0.9)
    if len(s["pos"]):
        ax.scatter(s["pos"][:, 1], s["pos"][:, 0], s=9, c=INK, alpha=0.8, linewidths=0)
    ax.set_xlim(-0.5, L - 0.5); ax.set_ylim(L - 0.5, -0.5)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    ax.set_title(title, loc="left", fontsize=10, color=INK)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="figures")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--steps", type=int, default=20000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cfg = Config(steps=a.steps)
    series, worlds = {}, {}
    for name, kw, pol, _ in CONDS:
        series[name] = []
        for sd in range(a.seeds):
            ent, sh2, snaps, w = run(cfg.with_(**kw), sd, pol)
            series[name].append((ent, sh2))
            if sd == 0:
                worlds[name] = snaps
        print("done", name, flush=True)

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.0))
    for ax, idx, title, unit in [(axes[0], 0, "Entropy production rate (2,000-day rolling)", ""), (axes[1], 1, "Share of energy from big deposits (2,000-day rolling)", "")]:
        for name, _, _, color in CONDS:
            arr = np.array([s[idx] for s in series[name]])
            for row in arr:
                ax.plot(row, color=color, alpha=0.22, linewidth=1)
            ax.plot(np.nanmean(arr, axis=0), color=color, linewidth=2.4, label=name)
        ax.set_title(title, loc="left", fontsize=11, color=INK)
        ax.set_xlabel("day")
        ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.suptitle(f"Example runs: thin lines are individual worlds (seeds 0-{a.seeds - 1}), thick lines are their mean", x=0.01, ha="left", fontsize=12, y=1.02)
    save(fig, a.out, "trajectories.png")

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.4))
    draw_snapshot(axes[0], worlds["Survival only (evolving)"][0], cfg, "Day 0: random creatures (same for every condition)")
    draw_snapshot(axes[1], worlds["Survival only (evolving)"][a.steps], cfg, f"Day {a.steps:,}: survival only, seed 0")
    draw_snapshot(axes[2], worlds["Hand-coded forager"][a.steps], cfg, f"Day {a.steps:,}: hand-coded forager, seed 0")
    fig.suptitle("Green: grass. Squares: small deposits (dashed gray when used up). Diamonds: big deposits (filled when open). Dots: creatures.", x=0.01, ha="left", fontsize=10.5, y=1.0, color=INK2)
    save(fig, a.out, "world_snapshots.png")


if __name__ == "__main__":
    main()
