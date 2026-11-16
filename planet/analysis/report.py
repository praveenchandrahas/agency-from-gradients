"""Every number in RESULTS.md and every figure comes from here.

    python analysis/report.py

Reads the CSVs in results/. Verdicts apply the "fails if" column of PREREGISTRATION.md, nothing else.
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
RNG = np.random.default_rng(20261116)
BOOT = 10_000

COG = {"weak": "weakly_variable", "seasonal": "predictable_seasonal", "volatile": "volatile_shifting",
       "strong": "strong_predictable_hotspots"}
CTL = {"volatile": "volatile_no_cognition", "strong": "strong_predictable_no_cognition"}
NAME = {"weakly_variable": "weak", "predictable_seasonal": "seasonal", "volatile_shifting": "volatile",
        "strong_predictable_hotspots": "strong", "volatile_no_cognition": "volatile, no agency",
        "strong_predictable_no_cognition": "strong, no agency"}
ENDS = {"w220": "201 to 220", "w660": "641 to 660"}

# Chart colours: a validated categorical order (blue, orange, aqua, yellow, magenta), light surface.
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


# ---------------------------------------------------------------- statistics
def boot(x):
    """Mean and 95% bootstrap interval of replicate values."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return np.nan, np.nan, np.nan
    means = x[RNG.integers(0, len(x), size=(BOOT, len(x)))].mean(axis=1)
    return float(x.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def boot_ratio(num, den):
    """Ratio of replicate means, replicates resampled together."""
    num, den = np.asarray(num, float), np.asarray(den, float)
    idx = RNG.integers(0, len(num), size=(BOOT, len(num)))
    r = num[idx].mean(axis=1) / den[idx].mean(axis=1)
    return float(num.mean() / den.mean()), float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))


def f(stat, d=3):
    m, lo, hi = stat
    return f"{m:.{d}f} [{lo:.{d}f}, {hi:.{d}f}]"


def verdict(ok):
    return "**Supported**" if ok else "**Not supported**"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


# ---------------------------------------------------------------- data
pure = pd.read_csv(os.path.join(RES, "pure_windows.csv"))
pure_s = pd.read_csv(os.path.join(RES, "pure_series.csv"))
pure_h = pd.read_csv(os.path.join(RES, "pure_hist.csv"))
pure_p = pd.read_csv(os.path.join(RES, "pure_patches.csv"))
mixed = pd.read_csv(os.path.join(RES, "mixed_windows.csv"))
mixed_s = pd.read_csv(os.path.join(RES, "mixed_series.csv"))


def pv(key, window, col):
    """Replicate values, ordered by replicate, for one pure scenario."""
    d = pure[(pure.scenario_key == key) & (pure.window == window)].sort_values("replicate")
    return d[col].to_numpy()


def mv(env, arm, start, window, col):
    d = mixed[(mixed.env == env) & (mixed.arm == arm) & np.isclose(mixed.start, start) & (mixed.window == window)]
    return d.sort_values("replicate")[col].to_numpy()


md: list[str] = []
add = md.append
add("# Planet: results\n")
add("Every number below is computed by `analysis/report.py` from the CSVs in `results/`. "
    "Intervals are 95% bootstrap intervals on replicate means, 20 replicates per cell. "
    "Predictions are in `PREREGISTRATION.md`. The endpoint is the mean over generations 201 to 220, "
    "the paper's endpoint. A second endpoint, 641 to 660, is shown beside it.\n")

n_ext = int(pure[pure.window == "g0"].extinct.sum()) + int(mixed[mixed.window == "g0"].extinct.sum())
n_runs = len(pure[pure.window == "g0"]) + len(mixed[mixed.window == "g0"])
add(f"{n_runs} runs, {n_ext} extinct.\n")

# ---------------------------------------------------------------- the paper's table
add("## First, the paper's own table\n")
add("Replicates 0 to 5 at generation 220 use the paper's seeds. Mean ± between-replicate SD. "
    "These equal Table 2 of the paper.\n")
rows = []
for key in ["weakly_variable", "predictable_seasonal", "volatile_shifting", "strong_predictable_hotspots",
            "volatile_no_cognition", "strong_predictable_no_cognition"]:
    d = pure[(pure.scenario_key == key) & (pure.window == "g220") & (pure.replicate < 6)]
    cell = lambda c, k: f"{d[c].mean():.{k}f} ± {d[c].std():.{k}f}"  # noqa: E731
    rows.append([NAME[key], cell("population", 0), cell("mean_collector", 3), cell("mean_agency_composite", 3),
                 cell("biotic_power_harnessed_TW", 2), cell("biotic_power_per_entity_GW", 2),
                 cell("occupied_patch_fraction", 3)])
add(table(["Scenario", "Population", "Collector", "Agency", "Throughput (TW)", "Per entity (GW)", "Occupancy"], rows))
add("")

# ================================================================= E1
add("## E1. Competition: carriers and non-carriers on one planet\n")
F = {(e, a, s, w): boot(mv(e, a, s, w, "carrier_fraction"))
     for e in COG for (a, s) in (("full", 0.1), ("full", 0.5), ("full", 0.9), ("bonus", 0.5), ("movement", 0.5))
     for w in ENDS}

p1a = all(F[(e, "full", 0.5, "w220")][1] > 0.5 for e in ("volatile", "strong"))
traj = (mixed_s[(mixed_s.arm == "full") & np.isclose(mixed_s.start, 0.5)]
        .groupby(["env", "generation"]).carrier_fraction.mean())
early = traj["strong"].loc[:40]
p1b_early = bool((early > 0.5).any())
p1b_late = F[("strong", "full", 0.5, "w220")][2] < 0.5
diff_bm = {e: boot(mv(e, "bonus", 0.5, "w220", "carrier_fraction") - mv(e, "movement", 0.5, "w220", "carrier_fraction"))
           for e in COG}
p1c = all(diff_bm[e][1] > 0 for e in COG)
p1d = F[("strong", "movement", 0.5, "w220")][2] < 0.5

add(table(["", "Source", "Prediction", "Result", "Verdict"], [
    ["P1a", "paper", "From 50/50, carriers gain share in volatile and strong (F > 0.5)",
     f"volatile: {f(F[('volatile', 'full', 0.5, 'w220')])}; strong: {f(F[('strong', 'full', 0.5, 'w220')])}",
     verdict(p1a)],
    ["P1b", "guess", "In strong, carriers gain early and lose later",
     f"highest mean F up to generation 40: {early.max():.3f} (generation {int(early.idxmax())}); "
     f"endpoint {f(F[('strong', 'full', 0.5, 'w220')])}", verdict(p1b_early and p1b_late)],
    ["P1c", "guess", "F(bonus) > F(movement) in all four environments",
     "; ".join(f"{e}: {f(diff_bm[e])}" for e in COG), verdict(p1c)],
    ["P1d", "guess", "Movement alone loses in strong (F < 0.5)", f(F[("strong", "movement", 0.5, "w220")]),
     verdict(p1d)],
]))
add("")
for w, label in ENDS.items():
    add(f"Carrier fraction F, generations {label}:\n")
    add(table(["Environment", "full, from 10%", "full, from 50%", "full, from 90%", "bonus only, from 50%",
               "movement only, from 50%"],
              [[e] + [f(F[(e, a, s, w)]) for (a, s) in (("full", 0.1), ("full", 0.5), ("full", 0.9), ("bonus", 0.5),
                                                        ("movement", 0.5))] for e in COG]))
    add("")
add("Mean carrier fraction on the way there, full arm from 50%:\n")
gens = [10, 20, 30, 40, 80, 120, 160, 220, 330, 440, 550, 660]
add(table(["Environment"] + [str(g) for g in gens], [[e] + [f"{traj[e].loc[g]:.3f}" for g in gens] for e in COG]))
add("")
add("The two types side by side, full arm from 50%, generations 201 to 220. "
    "Crowding is the number of entities sharing a patch, averaged over the entities of that type. "
    "A peak patch is one that is brighter than all eight neighbours.\n")
rows = []
for e in COG:
    for tag, who in (("c", "carriers"), ("n", "non-carriers")):
        g = lambda c: boot(mv(e, "full", 0.5, "w220", f"{c}_{tag}"))  # noqa: E731
        rows.append([e, who, f(g("net_mean")), f(g("survival_mean")), f(g("crowding"), 1), f(g("frac_on_peak")),
                     f(g("occupied_fraction"))])
add(table(["Environment", "Type", "Mean net energy", "Mean survival", "Crowding", "Share on peak patches",
           "Patches occupied"], rows))
add("")
add("Aggregate throughput (TW). The pool allows about 136.\n")
rows = []
for e in COG:
    row = [e]
    for w in ENDS:
        row.append(f(boot(mv(e, "full", 0.5, w, "biotic_power_harnessed_TW")), 1))
        row.append(f(boot(pv(COG[e], w, "biotic_power_harnessed_TW")), 1))
        row.append(f(boot(pv(CTL[e], w, "biotic_power_harnessed_TW")), 1) if e in CTL else "not run")
    rows.append(row)
add(table(["Environment", "mixed, 201-220", "all carriers, 201-220", "no carriers, 201-220", "mixed, 641-660",
           "all carriers, 641-660", "no carriers, 641-660"], rows))
add("")

# ================================================================= E2
add("## E2. Neutral markers: how far does a trait rise if it does nothing?\n")
rise_m = {k: boot(pv(k, "w220", "marker_composite") - pv(k, "g0", "marker_composite")) for k in NAME}
p2a = all(rise_m[k][0] >= 0.05 for k in NAME)
AM = {(e, w): boot(pv(COG[e], w, "mean_agency_composite") - pv(COG[e], w, "marker_composite"))
      for e in COG for w in ENDS}
RATIO = {(e, w): boot_ratio(pv(COG[e], w, "marker_composite") - pv(COG[e], "g0", "marker_composite"),
                            pv(COG[e], w, "mean_agency_composite") - pv(COG[e], "g0", "mean_agency_composite"))
         for e in COG for w in ENDS}
p2b = AM[("strong", "w220")][1] > 0
p2c = not (RATIO[("weak", "w220")][2] < 0.5)
add(table(["", "Source", "Prediction", "Result", "Verdict"], [
    ["P2a", "review", "Markers rise by at least 0.05 in each of the six scenarios",
     "; ".join(f"{NAME[k]}: +{rise_m[k][0]:.3f}" for k in NAME), verdict(p2a)],
    ["P2b", "paper", "Agency is selected in strong: A − M > 0", f(AM[("strong", "w220")]), verdict(p2b)],
    ["P2c", "review", "In weak, markers match at least half of the rise in agency",
     f"rise in M / rise in A = {f(RATIO[('weak', 'w220')], 2)}", verdict(p2c)],
]))
add("")
for w, label in ENDS.items():
    add(f"Agency composite A and marker composite M, generations {label}. Both start at 0.068.\n")
    add(table(["Environment", "A", "M", "A − M", "rise in M / rise in A"],
              [[e, f(boot(pv(COG[e], w, "mean_agency_composite"))), f(boot(pv(COG[e], w, "marker_composite"))),
                f(AM[(e, w)]), f(RATIO[(e, w)], 2)] for e in COG]))
    add("")
TRAITS = [("sensing", 1), ("processing", 2), ("prediction", 3), ("planning", 4), ("action", 5)]
for w, label in ENDS.items():
    add(f"Each agency trait minus its own marker, generations {label}. "
        "Above zero: pushed up by selection. Below zero: pushed down.\n")
    add(table(["Environment"] + [t for t, _ in TRAITS],
              [[e] + [f(boot(pv(COG[e], w, f"mean_{t}") - pv(COG[e], w, f"marker_{k}"))) for t, k in TRAITS]
               for e in COG]))
    add("")
add("The action trait itself:\n")
add(table(["Environment", "start", "201 to 220", "641 to 660"],
          [[e, f"{pv(COG[e], 'g0', 'mean_action').mean():.3f}", f(boot(pv(COG[e], "w220", "mean_action"))),
            f(boot(pv(COG[e], "w660", "mean_action")))] for e in COG]))
add("")

# ================================================================= E3
add("## E3. Demography: why do populations stay small when each entity has plenty?\n")
mf = {k: boot(pv(k, "w220", "growth_meanfield")) for k in NAME}
geo = {k: boot(pv(k, "g220", "growth_geo")) for k in NAME}
p3a = all(mf[COG[e]][0] > 1.10 for e in ("volatile", "strong")) and all(mf[CTL[e]][0] < 1.06 for e in CTL)
band = all(0.99 <= geo[COG[e]][0] <= 1.01 for e in ("volatile", "strong"))
d_below = boot(pv(COG["strong"], "w220", "frac_net_below_threshold") - pv(CTL["strong"], "w220", "frac_net_below_threshold"))
p3b = band and d_below[1] > 0
d_crowd = {w: boot(pv(COG["strong"], w, "crowding_entity_weighted") - pv(CTL["strong"], w, "crowding_entity_weighted"))
           for w in ENDS}
p3c = d_crowd["w220"][2] < 0
d660 = {(e, c): boot(pv(COG[e], "w660", c) - pv(CTL[e], "w660", c))
        for e in CTL for c in ("biotic_power_harnessed_TW", "biotic_power_per_entity_GW")}
p3d = all(d660[(e, "biotic_power_harnessed_TW")][2] < 0 and d660[(e, "biotic_power_per_entity_GW")][1] > 0 for e in CTL)
best = {e: boot(pv(COG[e], "early", "choice_true_best")) for e in COG}
p3e = all(best[e][0] >= 0.80 for e in COG)
add(table(["", "Source", "Prediction", "Result", "Verdict"], [
    ["P3a", "review", "Mean-field growth above 1.10 with agency, below 1.06 without",
     "; ".join(f"{NAME[k]}: {mf[k][0]:.3f}" for k in (COG["volatile"], COG["strong"], CTL["volatile"], CTL["strong"])),
     verdict(p3a)],
    ["P3b", "guess", "The gap is inequality, not a transient: realised growth within 0.99 to 1.01, "
     "and more entities below the survival threshold with agency (strong)",
     f"realised growth: volatile {geo[COG['volatile']][0]:.4f}, strong {geo[COG['strong']][0]:.4f}; "
     f"difference in share below threshold: {f(d_below)}", verdict(p3b)],
    ["P3c", "review, doubted", "Entity-weighted crowding is lower with agency than without (strong)",
     f"with minus without: {f(d_crowd['w220'], 1)}", verdict(p3c)],
    ["P3d", "review", "At 641 to 660 the contrast still holds in both pairs: throughput lower, per entity higher",
     "; ".join(f"{e}: {f(d660[(e, 'biotic_power_harnessed_TW')], 1)} TW, "
               f"+{f(d660[(e, 'biotic_power_per_entity_GW')], 1)} GW" for e in CTL), verdict(p3d)],
    ["P3e", "review", "Carriers pick the truly best neighbour at least 80% of the time in generations 0 to 20",
     "; ".join(f"{e}: {best[e][0]:.3f}" for e in COG), verdict(p3e)],
]))
add("")
add("On P3c, Claude's guess before the runs was that the review's claim would fail. "
    f"At 641 to 660 the same difference is {f(d_crowd['w660'], 1)}.\n")
cap = {k: boot(pv(k, "w220", "biotic_capture_fraction_of_photo_pool")) for k in CTL.values()}
add("Checked, not predicted: the controls capture "
    + " and ".join(f"{f(cap[k])} ({NAME[k]})" for k in cap) + " of the resource pool at the endpoint.\n")

ORDER = ["weakly_variable", "predictable_seasonal", "volatile_shifting", "strong_predictable_hotspots",
         "volatile_no_cognition", "strong_predictable_no_cognition"]
for w, label in ENDS.items():
    add(f"Where the energy goes, generations {label}. Net energy is in model units. "
        "The survival threshold is 0.05.\n")
    g = lambda k, c, d=3: f(boot(pv(k, w, c)), d)  # noqa: E731
    add(table(["Scenario", "Mean net", "10th pct", "Median", "90th pct", "Share below threshold",
               "Mean-field growth", "Mean survival + births", "Realised growth"],
              [[NAME[k], g(k, "mean_net_energy_units"), g(k, "net_q10"), g(k, "net_q50"), g(k, "net_q90"),
                g(k, "frac_net_below_threshold"), g(k, "growth_meanfield"), g(k, "growth_expected"),
                f(boot(pv(k, "g" + w[1:], "growth_geo")), 4)] for k in ORDER]))
    add("")
    add(f"Where the entities are, generations {label}:\n")
    add(table(["Scenario", "Population", "Patches occupied", "Per occupied patch", "Crowding, entity-weighted",
               "Share of population in the fullest 5% of patches", "Share on peak patches"],
              [[NAME[k], g(k, "population", 0), g(k, "occupied_patch_fraction"),
                g(k, "mean_entities_per_occupied_patch", 1), g(k, "crowding_entity_weighted", 1),
                g(k, "pop_share_top5pc_patches"), g(k, "frac_on_peak")] for k in ORDER]))
    add("")
    add(f"The headline numbers, generations {label}:\n")
    add(table(["Scenario", "Throughput (TW)", "Per entity (GW)", "Share of pool captured", "Agency", "Action",
               "Cooperation", "Technology"],
              [[NAME[k], g(k, "biotic_power_harnessed_TW", 1), g(k, "biotic_power_per_entity_GW", 1),
                g(k, "biotic_capture_fraction_of_photo_pool"), g(k, "mean_agency_composite"), g(k, "mean_action"),
                g(k, "mean_cooperation"), g(k, "mean_technology")] for k in ORDER]))
    add("")

with open(os.path.join(ROOT, "RESULTS.md"), "w") as fh:
    fh.write("\n".join(md).rstrip() + "\n")


# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "text.color": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "legend.frameon": False,
                     "lines.linewidth": 2.0, "axes.titlesize": 10, "axes.titleweight": "bold",
                     "axes.titlelocation": "left"})


def band(ax, d, col, color, label, ls="-"):
    """Mean line with a 95% interval band, across replicates."""
    g = d.groupby("generation")[col]
    m, s, n = g.mean(), g.std(), g.count()
    half = 1.96 * s / np.sqrt(n)
    ax.fill_between(m.index, m - half, m + half, color=color, alpha=0.15, linewidth=0)
    ax.plot(m.index, m, color=color, label=label, ls=ls)
    return m


def end_labels(ax, items, min_gap):
    """Direct labels at the right edge, nudged apart so they never overlap. items: (y, text)."""
    items = sorted(items)
    ys = [y for y, _ in items]
    for i in range(1, len(ys)):
        ys[i] = max(ys[i], ys[i - 1] + min_gap)
    for y, (_, text) in zip(ys, items):
        ax.annotate(text, (ax.get_xlim()[1], y), xytext=(4, 0), textcoords="offset points", va="center",
                    fontsize=8, color=INK2, annotation_clip=False)


def endpoint_marks(ax):
    ax.axvline(220, color=INK2, lw=0.8, ls=":")


# Figure 1: competition
fig, axes = plt.subplots(2, 2, figsize=(10, 6.6), sharex=True, sharey=True)
lines = [("full", 0.5, C[0], "-", "full agency"), ("bonus", 0.5, C[1], "--", "bonus only"),
         ("movement", 0.5, C[2], "-.", "movement only")]
for ax, e in zip(axes.flat, COG):
    ends = []
    ax.set_xlim(0, 660)
    for arm, start, col, ls, lab in lines:
        d = mixed_s[(mixed_s.env == e) & (mixed_s.arm == arm) & np.isclose(mixed_s.start, start)]
        m = band(ax, d, "carrier_fraction", col, lab, ls)
        ends.append((m.iloc[-1], lab))
    end_labels(ax, ends, 0.06)
    for start in (0.1, 0.9):
        d = mixed_s[(mixed_s.env == e) & (mixed_s.arm == "full") & np.isclose(mixed_s.start, start)]
        ax.plot(d.groupby("generation").carrier_fraction.mean(), color=C[0], lw=1.0, alpha=0.6)
    ax.axhline(0.5, color=INK2, lw=0.8)
    endpoint_marks(ax)
    ax.set_title(f"{e} environment")
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 660)
for ax in axes[1]:
    ax.set_xlabel("generation (dotted line: the paper's endpoint)")
for ax in axes[:, 0]:
    ax.set_ylabel("share of population carrying agency")
axes[1, 1].legend(loc="lower right", fontsize=8)
fig.suptitle("E1. Carriers and non-carriers on one planet, from a 50/50 start. "
             "Thin blue lines: full agency from 10% and from 90%", x=0.01, ha="left", fontsize=11)
fig.tight_layout(rect=(0, 0, 0.93, 0.97))
fig.savefig(os.path.join(FIG, "e1_competition.png"), dpi=160)
plt.close(fig)

# Figure 2: agency against its neutral markers
fig, axes = plt.subplots(2, 2, figsize=(10, 6.6), sharex=True, sharey=True)
for ax, e in zip(axes.flat, COG):
    d = pure_s[pure_s.scenario_key == COG[e]]
    ax.set_xlim(0, 660)
    ax.set_ylim(0, 0.4)
    ends = []
    for col, color, ls, lab in (("mean_agency_composite", C[0], "-", "agency (mean of five traits)"),
                                ("marker_composite", C[1], "--", "neutral markers"),
                                ("mean_action", C[2], "-.", "action trait alone")):
        m = band(ax, d, col, color, lab, ls)
        ends.append((m.iloc[-1], lab.split(" (")[0].replace(" trait alone", "")))
    end_labels(ax, ends, 0.022)
    endpoint_marks(ax)
    ax.set_title(f"{e} environment")
for ax in axes[1]:
    ax.set_xlabel("generation (dotted line: the paper's endpoint)")
for ax in axes[:, 0]:
    ax.set_ylabel("mean trait value")
axes[0, 0].legend(loc="upper right", fontsize=8)
fig.suptitle("E2. Agency traits against markers that cost nothing and do nothing", x=0.01, ha="left", fontsize=11)
fig.tight_layout(rect=(0, 0, 0.93, 0.97))
fig.savefig(os.path.join(FIG, "e2_markers.png"), dpi=160)
plt.close(fig)

# Figure 3: demography
fig, axes = plt.subplots(2, 2, figsize=(10, 7))
pair = [(COG["strong"], C[0], "-", "strong, with agency"), (CTL["strong"], C[1], "--", "strong, no agency")]
ax = axes[0, 0]
for key, color, ls, lab in pair:
    h = pure_h[(pure_h.scenario_key == key) & (pure_h.generation == 220)].groupby("bin_left")["count"].sum()
    h = h / h.sum()
    ax.step(h.index, h.values, where="post", color=color, ls=ls, label=lab)
ax.axvline(0.05, color=INK2, lw=0.8)
ax.annotate("survival\nthreshold", (0.05, ax.get_ylim()[1] * 0.88), xytext=(-4, 0), textcoords="offset points",
            fontsize=8, color=INK2, ha="right")
ax.set_xlim(-0.7, 4)
ax.set_xlabel("net energy of one entity (model units)")
ax.set_ylabel("share of entities")
ax.set_title("Net energy at generation 220, 20 replicates pooled")
ax.legend(fontsize=8)

ax = axes[0, 1]
keys = [COG["volatile"], COG["strong"], CTL["volatile"], CTL["strong"]]
x = np.arange(len(keys))
vals = [("growth_meanfield", "w220", C[0], "from the mean entity"), ("growth_expected", "w220", C[1], "entity by entity"),
        ("growth_geo", "g220", C[2], "what happened")]
for i, (col, w, color, lab) in enumerate(vals):
    ys = [boot(pv(k, w, col))[0] for k in keys]
    ax.bar(x + (i - 1) * 0.26, np.array(ys) - 1, 0.24, bottom=1, color=color, label=lab)
    for xi, y in zip(x, ys):
        ax.annotate(f"{y:.2f}", (xi + (i - 1) * 0.26, max(y, 1)), xytext=(0, 2), textcoords="offset points",
                    ha="center", fontsize=7, color=INK2)
ax.axhline(1, color=INK2, lw=0.8)
ax.set_xticks(x, ["volatile\nagency", "strong\nagency", "volatile\nno agency", "strong\nno agency"])
ax.set_ylabel("growth factor per generation")
ax.set_title("Growth: predicted from the mean, and real")
ax.legend(fontsize=8, loc="upper right")
ax.set_ylim(0.97, 1.24)

for ax, col, ylab, title in ((axes[1, 0], "population", "entities", "Population"),
                             (axes[1, 1], "biotic_power_harnessed_TW", "TW", "Aggregate throughput")):
    for key, color, ls, lab in pair + [(COG["volatile"], C[2], "-.", "volatile, with agency"),
                                       (CTL["volatile"], C[3], ":", "volatile, no agency")]:
        band(ax, pure_s[pure_s.scenario_key == key], col, color, lab, ls)
    endpoint_marks(ax)
    ax.set_xlim(0, 660)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("generation (dotted line: the paper's endpoint)")
    ax.set_ylabel(ylab)
    ax.set_title(title)
axes[1, 0].legend(fontsize=8, loc="upper right", ncol=2)
fig.suptitle("E3. Plenty on average, hunger for many", x=0.01, ha="left", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.97))
fig.savefig(os.path.join(FIG, "e3_demography.png"), dpi=160)
plt.close(fig)

# Figure 4: where they live. One planet, replicate 0, generation 220.
fig, axes = plt.subplots(1, 3, figsize=(12, 3.9))
shape = (16, 24)
sel = lambda key: pure_p[(pure_p.scenario_key == key) & (pure_p.generation == 220)].sort_values("patch")  # noqa: E731
a, b = sel(COG["strong"]), sel(CTL["strong"])
im = axes[0].imshow(a.field.to_numpy().reshape(shape), origin="lower", aspect="auto", cmap="Oranges")
axes[0].set_title("The light the carriers chase:\nabsorbed starlight (W/m²)")
fig.colorbar(im, ax=axes[0], fraction=0.046)
vmax = 60   # one shared scale. A few patches hold more; the colour bar says so.
for ax, d, title in ((axes[1], a, "With agency"), (axes[2], b, "Without agency")):
    im = ax.imshow(d["count"].to_numpy().reshape(shape), origin="lower", aspect="auto", cmap="Blues", vmin=0, vmax=vmax)
    ax.set_title(f"{title}: {int(d['count'].sum()):,} entities,\n{int((d['count'] > 0).sum())} of 384 patches, "
                 f"fullest holds {int(d['count'].max())}")
    fig.colorbar(im, ax=ax, fraction=0.046, label="entities in patch", extend="max")
for ax in axes:
    ax.grid(False)
    ax.set_xlabel("longitude cell")
    ax.set_ylabel("latitude cell")
fig.suptitle("Where they live. Strong environment, generation 220, one planet (replicate 0)", x=0.01, ha="left",
             fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(os.path.join(FIG, "e3_map.png"), dpi=160)
plt.close(fig)

print("wrote RESULTS.md and", len(os.listdir(FIG)), "files in figures/")
