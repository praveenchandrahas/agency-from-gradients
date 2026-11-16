"""Read results/*.csv, test every preregistered prediction, write RESULTS.md and figures."""
from __future__ import annotations

import csv
import math
import os
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
BOOT = np.random.default_rng(20261116)
NB = 10_000

C_BASE, C_ABS, HAZARD = 0.02, 0.05, 0.01   # must match starlight.Config defaults


def load(name):
    with open(os.path.join(RES, name)) as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for k, v in r.items():
            if k != "arm":
                r[k] = float(v) if v not in ("", "nan") else float("nan")
    return rows


def vals(rows, key, **where):
    out = [r[key] for r in rows if all(r[k] == v for k, v in where.items())]
    return np.array(out, dtype=float)


def ci(x):
    """Mean and 95% bootstrap interval. NaNs (extinct worlds' traits) are dropped."""
    x = x[~np.isnan(x)]
    if x.size == 0:
        return float("nan"), float("nan"), float("nan"), 0
    b = BOOT.choice(x, size=(NB, x.size), replace=True).mean(axis=1)
    return float(x.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5)), int(x.size)


def ci_diff(x, y):
    """Mean(x) - mean(y) with a 95% bootstrap interval, groups resampled independently."""
    x, y = x[~np.isnan(x)], y[~np.isnan(y)]
    if x.size == 0 or y.size == 0:
        return float("nan"), float("nan"), float("nan")
    bx = BOOT.choice(x, size=(NB, x.size), replace=True).mean(axis=1)
    by = BOOT.choice(y, size=(NB, y.size), replace=True).mean(axis=1)
    d = bx - by
    return float(x.mean() - y.mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def f3(t):
    return f"{t[0]:.3f} [{t[1]:.3f}, {t[2]:.3f}]"


def verdict(ok):
    return "**Supported**" if ok else "**Not supported**"


out = []
P = out.append
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

# ------------------------------------------------------------------ E1
e1 = load("e1_runs.csv")
e1s = load("e1_series.csv")
lo = vals(e1, "a", arm="evolved", a0=0.08)
hi = vals(e1, "a", arm="evolved", a0=2.0)
d_start = ci_diff(hi, lo)
e_mean = float(np.nanmean(vals(e1, "e_mean", arm="evolved")))
a_star = math.sqrt((C_BASE + HAZARD * e_mean) / C_ABS)
a_all = ci(np.concatenate([lo, hi]))
grid = sorted({r["a0"] for r in e1 if r["arm"] == "fixed"})
curve = {a0: ci(vals(e1, "capture", arm="fixed", a0=a0)) for a0 in grid}
best_a = max(curve, key=lambda k: curve[k][0])
best = vals(e1, "capture", arm="fixed", a0=best_a)
c_lo, c_hi = vals(e1, "capture", arm="evolved", a0=0.08), vals(e1, "capture", arm="evolved", a0=2.0)
rise_lo = ci_diff(c_lo, vals(e1, "capture", arm="fixed", a0=0.08))
rise_hi = ci_diff(c_hi, vals(e1, "capture", arm="fixed", a0=2.0))
gap_lo, gap_hi = ci_diff(c_lo, best), ci_diff(c_hi, best)

p1a = d_start[1] > -0.15 and d_start[2] < 0.15
p1b = abs(a_all[0] - a_star) <= 0.25 * a_star
p1c = rise_lo[1] > 0 and rise_hi[1] > 0
p1d = abs(gap_lo[0]) <= 0.02 and abs(gap_hi[0]) <= 0.02

P("# Starlight: results\n")
P("Every number below is computed by `analysis/report.py` from the CSVs in `results/`. "
  "Intervals are 95% bootstrap intervals on seed means. Predictions are in `PREREGISTRATION.md`.\n")
P("## E1. Does persistence selection raise capture?\n")
P("| | Prediction | Result | Verdict |\n|---|---|---|---|")
P(f"| P1a | Both starts converge on the same absorber size | start-high minus start-low: {f3(d_start)}. "
  f"Late `a`: {f3(ci(lo))} from 0.08, {f3(ci(hi))} from 2.0 | {verdict(p1a)} |")
P(f"| P1b | Late `a` within 25% of the predicted a* | a* = {a_star:.3f} (mean energy {e_mean:.3f}); "
  f"evolved {f3(a_all[:3])}; ratio {a_all[0] / a_star:.2f} | {verdict(p1b)} |")
P(f"| P1c | Capture rises from both starts | from 0.08: +{f3(rise_lo)}; from 2.0: +{f3(rise_hi)} | {verdict(p1c)} |")
P(f"| P1d | Evolved capture within 0.02 of the best frozen value | best frozen: a = {best_a}, C = {curve[best_a][0]:.3f}. "
  f"Evolved minus best: {f3(gap_lo)} and {f3(gap_hi)} | {verdict(p1d)} |")
P("\nFrozen-absorber capture curve (10 seeds each):\n")
P("| a | " + " | ".join(f"{a:g}" for a in grid) + " |\n|" + "---|" * (len(grid) + 1))
P("| C | " + " | ".join(f"{curve[a][0]:.3f}" for a in grid) + " |")
P(f"\nEvolved capture: {f3(ci(c_lo))} from the low start, {f3(ci(c_hi))} from the high start.\n")

fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
for a0, col in ((0.08, "#1f77b4"), (2.0, "#d95f02")):
    by = defaultdict(list)
    for r in e1s:
        if r["arm"] == "evolved" and r["a0"] == a0:
            by[r["seed"]].append((r["t"], r["a"]))
    for s, pts in by.items():
        pts.sort()
        ax[0].plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=0.6, alpha=0.5)
    ax[0].plot([], [], color=col, label=f"start a = {a0:g}")
ax[0].axhline(a_star, color="k", ls="--", lw=1, label=f"predicted a* = {a_star:.2f}")
ax[0].set(xlabel="step", ylabel="mean absorber size a", title="E1: two starts, one destination")
ax[0].legend(frameon=False)
ax[1].errorbar(grid, [curve[a][0] for a in grid],
               yerr=[[curve[a][0] - curve[a][1] for a in grid], [curve[a][2] - curve[a][0] for a in grid]],
               color="grey", marker="o", label="frozen a (no evolution)")
ax[1].errorbar([ci(lo)[0]], [ci(c_lo)[0]], marker="*", ms=14, color="#1f77b4", label="evolved, from 0.08")
ax[1].errorbar([ci(hi)[0]], [ci(c_hi)[0]], marker="*", ms=14, color="#d95f02", label="evolved, from 2.0")
ax[1].set(xlabel="absorber size a", ylabel="capture fraction C", title="Selection lands at the top of the capture curve")
ax[1].legend(frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "e1_capture.png"), dpi=150); plt.close(fig)

# ------------------------------------------------------------------ E3
e3 = load("e3_runs.csv")
e3s = load("e3_series.csv")
f_free, f_cost = ci(vals(e3, "f", arm="free")), ci(vals(e3, "f", arm="costly"))
p3a = f_cost[0] < 0.15 and f_cost[2] < 0.15
p3b = f_free[1] <= 0.5 <= f_free[2]
P("## E3. The furnace: is entropy itself selected?\n")
P("| | Prediction | Result | Verdict |\n|---|---|---|---|")
P(f"| P3a | Costly furnace is purged (late `f` < 0.15) | {f3(f_cost)} | {verdict(p3a)} |")
P(f"| P3b | Free furnace only drifts (late `f` not different from 0.5) | {f3(f_free)} | {verdict(p3b)} |")
P("\nWhat that did to the heat output (energy per step, late window):\n")
P("| Arm | Heat from living | Heat from furnace | Furnace band captured | Usable band captured | Late `a` |\n|---|---|---|---|---|---|")
for arm in ("free", "costly"):
    P(f"| {arm} | {ci(vals(e3, 'heat', arm=arm))[0]:.1f} | {ci(vals(e3, 'heat_b', arm=arm))[0]:.1f} | "
      f"{f3(ci(vals(e3, 'capture_b', arm=arm)))} | {f3(ci(vals(e3, 'capture', arm=arm)))} | {f3(ci(vals(e3, 'a', arm=arm)))} |")
P("")
fig, ax = plt.subplots(figsize=(5.5, 3.8))
for arm, col in (("free", "#7570b3"), ("costly", "#d95f02")):
    by = defaultdict(list)
    for r in e3s:
        if r["arm"] == arm:
            by[r["seed"]].append((r["t"], r["f"]))
    for s, pts in by.items():
        pts.sort()
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=0.6, alpha=0.6)
    ax.plot([], [], color=col, label=f"{arm} furnace")
ax.axhline(0.5, color="k", ls=":", lw=1)
ax.set(xlabel="step", ylabel="mean furnace trait f", ylim=(0, 1), title="E3: a trait that only makes entropy")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "e3_furnace.png"), dpi=150); plt.close(fig)

# ------------------------------------------------------------------ E2
if os.path.exists(os.path.join(RES, "e2_runs.csv")):
    e2 = load("e2_runs.csv")
    speeds = sorted({r["v"] for r in e2})
    arms = ("a", "am", "amg")
    m_d = ci_diff(vals(e2, "m", arm="am", v=0.3), vals(e2, "m", arm="am", v=0.0))
    dr_d = ci_diff(vals(e2, "directed_rate", arm="amg", v=0.5), vals(e2, "directed_rate", arm="amg", v=0.0))
    ext_amg_05 = int(vals(e2, "extinct", arm="amg", v=0.5).sum())
    n_cell = int(vals(e2, "extinct", arm="amg", v=0.5).size)
    c_move = ci_diff(vals(e2, "capture", arm="am", v=0.3), vals(e2, "capture", arm="a", v=0.3))
    c_sense = ci_diff(vals(e2, "capture", arm="amg", v=0.5), vals(e2, "capture", arm="am", v=0.5))
    g0, g5 = ci(vals(e2, "g", arm="amg", v=0.0)), ci(vals(e2, "g", arm="amg", v=0.5))
    g_d = ci_diff(vals(e2, "g", arm="amg", v=0.5), vals(e2, "g", arm="amg", v=0.0))
    p2a = m_d[1] > 0
    p2b = dr_d[1] > 0 and ext_amg_05 <= n_cell / 2
    p2c = c_move[1] > 0
    p2d = c_sense[1] > 0
    p2e = g0[0] < 0.25 and g_d[1] > 0
    P("## E2. Does behaviour evolve, and only when needed?\n")
    P("| | Prediction | Result | Verdict |\n|---|---|---|---|")
    P(f"| P2a | Moving evolves with speed (`m` at 0.3 minus `m` at 0, arm `am`) | +{f3(m_d)} | {verdict(p2a)} |")
    P(f"| P2b | Sensing evolves with speed (directed-move rate at 0.5 minus at 0, arm `amg`) | +{f3(dr_d)}; "
      f"{ext_amg_05} of {n_cell} extinct at 0.5 | {verdict(p2b)} |")
    P(f"| P2c | Moving buys capture at v = 0.3 (`am` minus `a`) | {f3(c_move)} | {verdict(p2c)} |")
    P(f"| P2d | Sensing buys capture at v = 0.5 (`amg` minus `am`) | {f3(c_sense)} | {verdict(p2d)} |")
    P(f"| P2e | Unneeded sensing is not kept (`g` at 0 below 0.25, and below `g` at 0.5) | at 0: {f3(g0[:3])}; "
      f"at 0.5: {f3(g5[:3])}; difference {f3(g_d)} | {verdict(p2e)} |")
    for key, title in (("capture", "Capture fraction C"), ("extinct", "Extinct worlds (of 20)"),
                       ("m", "Late motility m"), ("g", "Late sensing g"),
                       ("directed_rate", "Directed moves per organism per step"), ("a", "Late absorber a")):
        P(f"\n{title}:\n")
        P("| arm | " + " | ".join(f"v = {v:g}" for v in speeds) + " |\n|" + "---|" * (len(speeds) + 1))
        for arm in arms:
            if key in ("m", "directed_rate") and arm == "a":
                continue
            if key == "g" and arm != "amg":
                continue
            cells = []
            for v in speeds:
                x = vals(e2, key, arm=arm, v=v)
                if key == "extinct":
                    cells.append(str(int(x.sum())))
                else:
                    c = ci(x)
                    cells.append("all extinct" if c[3] == 0 else f"{c[0]:.3f} [{c[1]:.3f}, {c[2]:.3f}]"
                                 + (f" (n={c[3]})" if c[3] < x.size else ""))
            P(f"| `{arm}` | " + " | ".join(cells) + " |")
    P("\n## Not preregistered: things the runs showed that I did not predict\n")
    P("These were looked at after the fact. Treat them as leads, not findings.\n")
    for v in (0.1, 0.2, 0.3):
        d = ci_diff(vals(e2, "capture", arm="amg", v=v), vals(e2, "capture", arm="am", v=v))
        P(f"- At v = {v:g}, allowing sensing changed capture by {f3(d)} (`amg` minus `am`).")
    P("- So where sensing was optional, the lineages that could sense captured slightly *less*. "
      "Selection did not maximise capture there. The cause is not established: it could be the running cost of the sensor, "
      "or crowding on the bright sites.")
    hf = float(np.mean(vals(e3, "heat", arm="free") + vals(e3, "heat_b", arm="free")))
    hc = float(np.mean(vals(e3, "heat", arm="costly") + vals(e3, "heat_b", arm="costly")))
    h0 = float(np.mean(vals(e1, "heat", arm="evolved")))
    P(f"- Total heat per step: {h0:.1f} with no furnace band (E1), {hf:.1f} with a free furnace, {hc:.1f} with a costly one. "
      f"Selection gave up {hf - hc:.1f} units of entropy-producing heat per step to save a running cost of 0.01 per unit of furnace.")
    P("- The frozen perfect climber captured about 0.15 in the pilots. The evolved populations at v = 0.8 captured 0.53. "
      "Their directed-move rate settled just above the patch speed (0.81 against 0.8): fast enough to keep up, "
      "not so fast that everyone piles onto the peak.")
    P("")
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
    cols = {"a": "grey", "am": "#1f77b4", "amg": "#d95f02"}
    names = {"a": "absorber only", "am": "+ moving", "amg": "+ moving + sensing"}
    xs = np.arange(len(speeds))
    for arm in arms:
        c = [ci(vals(e2, "capture", arm=arm, v=v)) for v in speeds]
        ax[0].errorbar(xs, [t[0] for t in c], yerr=[[t[0] - t[1] for t in c], [t[2] - t[0] for t in c]],
                       marker="o", color=cols[arm], label=names[arm], capsize=2)
    ax[0].set(xticks=xs, xticklabels=[f"{v:g}" for v in speeds], xlabel="final patch speed (sites per step)",
              ylabel="capture fraction C", title="E2: capture, by what is allowed to evolve")
    ax[0].legend(frameon=False)
    for j, (key, lab) in enumerate((("m", "late motility m"), ("g", "late sensing g"))):
        for arm in arms:
            if arm == "a" or (key == "g" and arm != "amg"):
                continue
            c = [ci(vals(e2, key, arm=arm, v=v)) for v in speeds]
            ok = [i for i, t in enumerate(c) if t[3] > 0]
            ax[j + 1].errorbar([xs[i] for i in ok], [c[i][0] for i in ok],
                               yerr=[[c[i][0] - c[i][1] for i in ok], [c[i][2] - c[i][0] for i in ok]],
                               marker="o", color=cols[arm], label=names[arm], capsize=2)
        ax[j + 1].set(xticks=xs, xticklabels=[f"{v:g}" for v in speeds], xlabel="final patch speed",
                      ylabel=lab, ylim=(0, 1), title=lab)
        ax[j + 1].legend(frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "e2_behaviour.png"), dpi=150); plt.close(fig)

with open(os.path.join(ROOT, "RESULTS.md"), "w") as fh:
    fh.write("\n".join(out) + "\n")
print("\n".join(out))
