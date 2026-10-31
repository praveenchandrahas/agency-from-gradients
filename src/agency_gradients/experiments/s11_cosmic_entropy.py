"""S11 - what is the best way to increase the entropy of a lifeless universe? (PREREGISTRATION_S11.md)

Run a search job:  python -m agency_gradients.experiments.s11_cosmic_entropy --arm main --horizon 1e14 --es-seed 0 --out out
Ablation job:      ... --arm no_bh_levers --horizon 1e12 --out out         (Phase A only, es seeds 0-2)
Far horizon:       ... --arm far --out out
Analyse:           ... --analyze DIR_WITH_CSVS --out docs/results/s11
Seeds 0-19 are the held-out confirmatory universes; training uses seeds >= 1000.
"""
from __future__ import annotations

import csv
import glob
import json
import os
from dataclasses import replace

import numpy as np

from ..cosmos.model import Params
from ..cosmos.policies import K_SEG, N_NN, N_PW, NA, NeuralPolicy, PiecewisePolicy
from ..cosmos.search import NOISE_FLOOR, gain_of, grid_strategies, phase_a, phase_b, slog
from ..runner import write_csv
from ..stats import bootstrap_diff_ci, bootstrap_mean_ci
from .common import emit, fmt

TEST_SEEDS = list(range(20))
TRAIN_SEEDS = [1000, 1001, 1002, 1003]
HORIZONS = {"1e11": 1e11, "1e12": 1e12, "1e14": 1e14}

INF = float("inf")
ABLATIONS = {
    "default": ({}, (1, 1, 1, 1, 1)),
    "no_bh_levers": ({}, (1, 0, 0, 0, 1)),
    "bh_x0.1": (dict(bh_mult=0.1), (1, 1, 1, 1, 1)),
    "bh_x10": (dict(bh_mult=10.0), (1, 1, 1, 1, 1)),
    "no_reach_limit": (dict(reach_limit=False), (1, 1, 1, 1, 1)),
    "cost_x0.5": (dict(cost_mult=0.5), (1, 1, 1, 1, 1)),
    "cost_x2": (dict(cost_mult=2.0), (1, 1, 1, 1, 1)),
    "cost_x1000": (dict(cost_mult=1000.0), (1, 1, 1, 1, 1)),
    "probe_c": (dict(v_probe=1.0), (1, 1, 1, 1, 1)),
    "probe_0.1c": (dict(v_probe=0.1), (1, 1, 1, 1, 1)),
    "domain_1e12": (dict(domain_mass=1e12), (1, 1, 1, 1, 1)),
    "domain_1e16": (dict(domain_mass=1e16), (1, 1, 1, 1, 1)),
    "domain_none": (dict(domain_mass=INF), (1, 1, 1, 1, 1)),
    "no_area_limit": (dict(area_limit=False), (1, 1, 1, 1, 1)),
    "eta_0.05": (dict(eta=0.05), (1, 1, 1, 1, 1)),
    "eta_0.3": (dict(eta=0.3), (1, 1, 1, 1, 1)),
    "no_accretion_capture": (dict(capture_accretion=False), (1, 1, 1, 1, 1)),
}
AUDIT = {  # tightenings applied to the already-optimised policies (no re-optimisation)
    "as_trained": {},
    "cost_x10": dict(cost_mult=10.0),
    "cost_x100": dict(cost_mult=100.0),
    "no_accretion_capture": dict(capture_accretion=False),
    "domain_1e12": dict(domain_mass=1e12),
    "probe_0.1c": dict(v_probe=0.1),
    "radiator_unlimited": dict(area_limit=False),
}
COLS = ["arm", "horizon", "es_seed", "method", "seed", "gain", "slog", "bh", "photon", "matter", "hawking", "abs_total",
        "ledger_err", "cap_hit", "W_final", "variant"]


def _row(arm, hz, es, method, seed, g, variant=""):
    return dict(arm=arm, horizon=hz, es_seed=es, method=method, seed=seed, gain=g["total"], slog=slog(g["total"]), bh=g["bh"],
                photon=g["photon"], matter=g["matter"], hawking=g["hawking"], abs_total=g["abs_total"],
                ledger_err=g["ledger_err"], cap_hit=int(g["cap_hit"]), W_final=g["W_final"], variant=variant)


def evaluate(rows, arm, hz, es, method, p, policy, seeds=TEST_SEEDS, variant=""):
    for s in seeds:
        rows.append(_row(arm, hz, es, method, s, gain_of(p, policy, s, check=True), variant))


def run_job(arm, hz_name, es_seeds, out, smoke=False):
    hz = HORIZONS.get(hz_name, float(hz_name))
    kw, mask = ABLATIONS["default" if arm == "main" else arm]
    p = Params(horizon_yr=hz, **kw)
    if smoke:
        p = replace(p, per_decade=8)
    rows, pol = [], {}
    gA, pA, gB, pB = (3, 4, 3, 4) if smoke else (40, 12, 60, 24)
    for es in es_seeds:
        rng = np.random.default_rng(1000 * es + 7)
        name, thA, table, _ = phase_a(p, TRAIN_SEEDS[:2] if smoke else TRAIN_SEEDS, rng, gens=gA, pairs=pA, mask=mask)
        evaluate(rows, arm, hz_name, es, "phaseA_best", p, PiecewisePolicy(thA, mask))
        pol[f"A_{es}"] = dict(theta=thA.tolist(), grid_start=name)
        if arm == "main":
            thB, _ = phase_b(p, TRAIN_SEEDS[:2] if smoke else TRAIN_SEEDS, rng, gens=gB, pairs=pB, mask=mask)
            evaluate(rows, arm, hz_name, es, "phaseB_best", p, NeuralPolicy(thB, mask))
            pol[f"B_{es}"] = dict(theta=thB.tolist())
            for tag, mk, th in (("A", lambda t: PiecewisePolicy(t, mask), thA), ("B", lambda t: NeuralPolicy(t, mask), thB)):
                for vname, vkw in AUDIT.items():
                    evaluate(rows, arm, hz_name, es, f"audit_{tag}", replace(p, **vkw), mk(th), TEST_SEEDS[:10], variant=vname)
            if es == es_seeds[0]:
                rr = np.random.default_rng(99)
                for k in range(10):
                    evaluate(rows, arm, hz_name, k, "random_piecewise", p, PiecewisePolicy(rr.standard_normal(N_PW) * 2, mask), TEST_SEEDS[:10])
                    evaluate(rows, arm, hz_name, k, "random_neural", p, NeuralPolicy(rr.standard_normal(N_NN) * 0.5, mask), TEST_SEEDS[:10])
                for gname, th in grid_strategies().items():
                    evaluate(rows, arm, hz_name, 0, f"grid:{gname}", p, PiecewisePolicy(th, mask), TEST_SEEDS)
        if arm in ("no_area_limit", "no_bh_levers", "default") or es == es_seeds[0]:
            if es == es_seeds[0]:
                for gname in ("only_collectors", "nothing"):
                    evaluate(rows, arm, hz_name, 0, f"grid:{gname}", p, PiecewisePolicy(grid_strategies()[gname], mask), TEST_SEEDS)
        print(f"  {arm} {hz_name} es {es} done", flush=True)
    os.makedirs(out, exist_ok=True)
    write_csv(rows, f"{out}/s11_runs_{arm}_{hz_name}_{es_seeds[0]}.csv")
    json.dump(pol, open(f"{out}/s11_policies_{arm}_{hz_name}_{es_seeds[0]}.json", "w"))


def run_far(out, smoke=False):
    rows = []
    seeds = TEST_SEEDS[:2] if smoke else TEST_SEEDS[:5]
    grid = grid_strategies()
    names = ["nothing", "only_collectors", "staged_collectors_then_merge_holes", "mix_funnel+merge+collectors"]
    for hk in (False, True):
        p = Params(horizon_yr=1e113, per_decade=4 if smoke else 8, hawking=hk)
        for n in names:
            evaluate(rows, "far", "1e113", 0, f"grid:{n}", p, PiecewisePolicy(grid[n]), seeds, variant="hawking" if hk else "no_hawking")
            print("  far", n, hk, flush=True)
    os.makedirs(out, exist_ok=True)
    write_csv(rows, f"{out}/s11_runs_far_1e113_0.csv")


# ---------------------------------------------------------------- analysis
def _load(d):
    rows = []
    for f in sorted(glob.glob(f"{d}/**/s11_runs_*.csv", recursive=True)):
        for r in csv.DictReader(open(f)):
            for k in ("gain", "slog", "bh", "photon", "matter", "hawking", "abs_total", "ledger_err", "W_final"):
                r[k] = float(r[k])
            r["seed"] = int(r["seed"]); r["es_seed"] = int(r["es_seed"]); r["cap_hit"] = int(r["cap_hit"])
            rows.append(r)
    return rows


def _per_seed(rows, **flt):
    """mean over ES runs of slog gain, per held-out seed."""
    by = {}
    for r in rows:
        if all(r[k] == v for k, v in flt.items()):
            by.setdefault(r["seed"], []).append(r["slog"])
    return {s: float(np.mean(v)) for s, v in by.items()}


def _vec(d, seeds):
    return [d[s] for s in seeds if s in d]


def analyze(d, out):
    rows = _load(d)
    write_csv(rows, f"{out}/s11_runs_all.csv")
    L = ["# S11 results: entropy maximisation in a lifeless toy universe", "",
         f"Rows: {len(rows)}. Held-out seeds 0-19 are draws of uncertain physical parameters (the model is deterministic), so intervals are "
         "parameter-uncertainty intervals. Gains are in k_B over the do-nothing universe; `slog` = sign(g) log10(1+|g|). "
         f"Gains below {NOISE_FLOOR:.0e} k_B are below float64 resolution of the ~3e104 BH total and are set to 0.", ""]
    mx = max((r["ledger_err"] for r in rows), default=0)
    L += [f"Max ledger relative error over all rollouts: {mx:.2e}. Runs that hit the horizon-entropy cap (BH entropy > S_CEH): "
          f"{sum(r['cap_hit'] for r in rows)} of {len(rows)}.", ""]
    hs = ["1e11", "1e12", "1e14"]

    def stat(vals):
        m, lo, hi = bootstrap_mean_ci(vals)
        return f"{fmt(m, 2)} [{fmt(lo, 2)}, {fmt(hi, 2)}]"

    L += ["## Horizon sweep, default model (log10 gain in k_B, mean over ES runs; 95% bootstrap CI over seeds 0-19)", "",
          "| horizon | do-nothing abs. total (k_B) | Phase A best | Phase B best | random piecewise | random neural | best grid strategy |", "|---|---|---|---|---|---|---|"]
    for h in hs:
        a = _per_seed(rows, arm="main", horizon=h, method="phaseA_best")
        b = _per_seed(rows, arm="main", horizon=h, method="phaseB_best")
        rp = _per_seed(rows, arm="main", horizon=h, method="random_piecewise")
        rn = _per_seed(rows, arm="main", horizon=h, method="random_neural")
        gr = {}
        for r in rows:
            if r["arm"] == "main" and r["horizon"] == h and r["method"].startswith("grid:") and r["method"] != "grid:nothing":
                gr.setdefault(r["method"], []).append(r["slog"])
        gbest = max(gr, key=lambda k: np.mean(gr[k])) if gr else "n/a"
        base = [r["abs_total"] for r in rows if r["arm"] == "main" and r["horizon"] == h and r["method"] == "grid:nothing"]
        L.append(f"| {h} yr | {np.mean(base):.3g} | {stat(list(a.values()))} | {stat(list(b.values()))} | {stat(list(rp.values()))} | "
                 f"{stat(list(rn.values()))} | {gbest.replace('grid:', '')} {fmt(np.mean(gr[gbest]), 2) if gr else ''} |")
    L += ["", "## Entropy breakdown of the best Phase A policy (mean gain over seeds and ES runs, k_B)", "",
          "| horizon | total | black holes | photons | matter | BH share |", "|---|---|---|---|---|---|"]
    for h in hs:
        rr = [r for r in rows if r["arm"] == "main" and r["horizon"] == h and r["method"] == "phaseA_best"]
        if rr:
            t = np.mean([r["gain"] for r in rr]); b_ = np.mean([r["bh"] for r in rr]); p_ = np.mean([r["photon"] for r in rr]); m_ = np.mean([r["matter"] for r in rr])
            L.append(f"| {h} | {t:.3g} | {b_:.3g} | {p_:.3g} | {m_:.3g} | {b_ / t if t else float('nan'):.4f} |")
    L += ["", "## Grid strategies (default model, mean slog over seeds 0-19)", "", "| strategy | " + " | ".join(hs) + " |", "|---|---|---|---|"]
    names = sorted({r["method"] for r in rows if r["arm"] == "main" and r["method"].startswith("grid:")})
    for n in names:
        cells = []
        for h in hs:
            v = [r["slog"] for r in rows if r["arm"] == "main" and r["horizon"] == h and r["method"] == n]
            cells.append(fmt(np.mean(v), 2) if v else "-")
        L.append(f"| {n.replace('grid:', '')} | " + " | ".join(cells) + " |")

    L += ["", "## Preregistered hypotheses", ""]

    def judge(lo, hi, cond):
        return "SUPPORTED" if cond else "NOT supported"

    # H11a
    for h in hs:
        a = _per_seed(rows, arm="main", horizon=h, method="phaseA_best")
        if a:
            m, lo, hi = bootstrap_mean_ci(list(a.values()))
            rr = [r for r in rows if r["arm"] == "main" and r["horizon"] == h and r["method"] == "phaseA_best"]
            sh = np.mean([r["bh"] for r in rr]) / np.mean([r["gain"] for r in rr])
            L.append(f"- H11a @ {h}: log10 gain {fmt(m, 2)} [{fmt(lo, 2)}, {fmt(hi, 2)}], BH share of gain {sh:.4f} -> "
                     f"{judge(lo, hi, lo > 0 and sh > 0.9)}")
    # H11b
    a14, a11 = _per_seed(rows, arm="main", horizon="1e14", method="phaseA_best"), _per_seed(rows, arm="main", horizon="1e11", method="phaseA_best")
    if a14 and a11:
        d, lo, hi = bootstrap_diff_ci(_vec(a14, TEST_SEEDS), _vec(a11, TEST_SEEDS))
        L.append(f"- H11b best log10 gain, 1e14 yr minus 1e11 yr: {fmt(d, 2)} [{fmt(lo, 2)}, {fmt(hi, 2)}] -> {judge(lo, hi, lo > 0)}")

    def cmp(arm_x, arm_y, h, label, test, method="phaseA_best"):
        ax_, ay_ = ("main" if arm_x == "default" else arm_x), ("main" if arm_y == "default" else arm_y)
        x, y = _per_seed(rows, arm=ax_, horizon=h, method=method), _per_seed(rows, arm=ay_, horizon=h, method=method)
        if not x or not y:
            L.append(f"- {label} @ {h}: missing data"); return None
        ss = [s for s in TEST_SEEDS if s in x and s in y]
        d, lo, hi = bootstrap_diff_ci([x[s] for s in ss], [y[s] for s in ss])
        L.append(f"- {label} @ {h}: {fmt(d, 2)} [{fmt(lo, 2)}, {fmt(hi, 2)}] -> {test(d, lo, hi)}")
        return d, lo, hi

    for h in hs:
        cmp("no_reach_limit", "default", h, "H11c no-reach-limit minus default (log10 gain)", lambda d, lo, hi: judge(lo, hi, lo > 0))
    for h in hs:
        xb, xa = _per_seed(rows, arm="main", horizon=h, method="phaseB_best"), _per_seed(rows, arm="main", horizon=h, method="phaseA_best")
        if xb and xa:
            d, lo, hi = bootstrap_diff_ci(_vec(xb, TEST_SEEDS), _vec(xa, TEST_SEEDS))
            L.append(f"- H11d @ {h} Phase B minus Phase A (log10 gain): {fmt(d, 2)} [{fmt(lo, 2)}, {fmt(hi, 2)}] -> {judge(lo, hi, lo > 0)}")
    for h in hs:
        cmp("default", "no_bh_levers", h, "H11e default minus no-BH-levers (log10 gain; need > 5)", lambda d, lo, hi: judge(lo, hi, lo > 5))
    # H11f: photon route without area limit
    for h in hs:
        ph = [r["photon"] for r in rows if r["arm"] == "no_area_limit" and r["horizon"] == h and r["method"] == "grid:only_collectors"]
        bh = [r["bh"] for r in rows if r["arm"] == "main" and r["horizon"] == h and r["method"] == "phaseA_best"]
        if ph and bh:
            lp, lb = [slog(x) for x in ph], [slog(x) for x in bh]
            d, lo, hi = bootstrap_diff_ci(lp, lb)
            L.append(f"- H11f @ {h}: photon gain of collectors-only without area limit: log10 {fmt(np.mean(lp), 2)}; best BH-route {fmt(np.mean(lb), 2)}; "
                     f"difference {fmt(d, 2)} [{fmt(lo, 2)}, {fmt(hi, 2)}] -> {judge(lo, hi, lo > 0)}")
    for arm, exp in (("bh_x0.1", -1.0), ("bh_x10", 1.0)):
        for h in hs:
            cmp(arm, "default", h, f"H11g {arm} minus default (expected {exp:+.0f} +- 0.5)", lambda d, lo, hi, e=exp: "within" if abs(d - e) <= 0.5 else "OUTSIDE")
    for arm in ("cost_x0.5", "cost_x2"):
        for h in hs:
            cmp(arm, "default", h, f"H11h {arm} minus default (CI inside +-0.5?)", lambda d, lo, hi: judge(lo, hi, lo > -0.5 and hi < 0.5))
    L += ["", "## All ablations: best Phase A log10 gain (mean over ES runs; CI over seeds)", "", "| ablation | " + " | ".join(hs) + " |", "|---|---|---|---|"]
    for arm in ABLATIONS:
        cells = []
        for h in hs:
            v = _per_seed(rows, arm=("main" if arm == "default" else arm), horizon=h, method="phaseA_best")
            cells.append(stat(list(v.values())) if v else "-")
        L.append(f"| {arm} | " + " | ".join(cells) + " |")
    L += ["", "## Exploit audit: best policies re-evaluated under tightened assumptions (no re-optimisation; mean slog, seeds 0-9)", "",
          "| policy | variant | " + " | ".join(hs) + " |", "|---|---|---|---|---|"]
    for tag in ("A", "B"):
        for v in AUDIT:
            cells = []
            for h in hs:
                x = [r["slog"] for r in rows if r["method"] == f"audit_{tag}" and r["variant"] == v and r["horizon"] == h]
                cells.append(fmt(np.mean(x), 2) if x else "-")
            L.append(f"| {tag} | {v} | " + " | ".join(cells) + " |")
    far = [r for r in rows if r["arm"] == "far"]
    if far:
        L += ["", "## Far horizon 1e113 yr (SPECULATIVE; seeds 0-4)", "", "| strategy | variant | log10 gain | BH entropy gain | Hawking radiation entropy |", "|---|---|---|---|---|"]
        for n in sorted({r["method"] for r in far}):
            for v in ("no_hawking", "hawking"):
                x = [r for r in far if r["method"] == n and r["variant"] == v]
                if x:
                    L.append(f"| {n.replace('grid:', '')} | {v} | {np.mean([r['slog'] for r in x]):.2f} | {np.mean([r['bh'] for r in x]):.3g} | {np.mean([r['hawking'] for r in x]):.3g} |")
    emit(L, f"{out}/s11_report.md")


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", default="main")
    ap.add_argument("--horizon", default="1e14")
    ap.add_argument("--es-seed", type=int, default=0)
    ap.add_argument("--n-es", type=int, default=1, help="ES runs in this job (ablations: 3)")
    ap.add_argument("--out", default="out")
    ap.add_argument("--analyze", default=None)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args(argv)
    if a.analyze:
        return analyze(a.analyze, a.out)
    if a.arm == "far":
        return run_far(a.out, a.smoke)
    run_job(a.arm, a.horizon, list(range(a.es_seed, a.es_seed + a.n_es)), a.out, a.smoke)


if __name__ == "__main__":
    main()
