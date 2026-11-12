"""S14 - before the replicator: does a driven soup start copying itself?

No agents, no genomes, no birth rule, no fitness. A flow reactor of binary polymers, a fuel and
a heat bath, with every reaction reversible and obeying detailed balance. See
PREREGISTRATION_S14.md.

Arms: R (random chemistries), N (the same with catalysis deleted), P (a designed self-copier),
M (the same reactions catalysed from outside), C (exploratory: arm R under a day/night feed).
Run:     python -m agency_gradients.experiments.s14_soup --arm R --chem0 0 --chems 20 --out out
Gates:   python -m agency_gradients.experiments.s14_soup --arm gates --out out
Analyse: python -m agency_gradients.experiments.s14_soup --analyze DIR --out out
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from ..runner import write_csv
from ..soup.chemistry import (COPIER, COPIER_SEED, SoupParams, designed_chemistry, equilibrium_counts,
                              random_chemistry)
from ..soup.detect import potential_raf, realised_raf, shuffle_percentile, sterilised_twin, twin_lag
from ..soup.reactor import Reactor
from .common import emit, fmt

PRM = SoupParams()
DRIVES = (0.0, 4.0, 8.0, 12.0)
TOP, LOW = 12.0, 4.0
ARM_CODE = {"R": 1, "N": 2, "P": 3, "M": 4, "C": 5}
DAY_NIGHT = 10                      # exploratory arm C: period in residence times
LAG_MIN = 10.0                      # criterion (ii)
VARIANTS = {"main": (1.0, 1.0), "half": (0.5, 0.5), "double": (2.0, 2.0)}   # (n_min, j_min)
N_BOOT = 4000


def _chem(arm: str, chem_id: int, prm: SoupParams):
    if arm in ("R", "C"):
        return random_chemistry(chem_id, prm)
    if arm == "N":
        return random_chemistry(chem_id, prm).without_catalysis()
    return designed_chemistry(arm, prm)


def eq_poly_frac(chem, prm: SoupParams) -> float:
    eq = equilibrium_counts(chem, prm.n_mono, prm.n_mono, prm.c0)
    return float((np.where(chem.lens >= 3, chem.lens, 0) * eq).sum() / (chem.lens * eq).sum())


def run_one(job: dict) -> dict:
    arm, cid, dmu, prm = job["arm"], job["chem"], job["dmu"], job.get("prm", PRM)
    detect = job.get("detect", True)
    chem = _chem(arm, cid, prm)
    di = DRIVES.index(dmu) if dmu in DRIVES else 99
    ss = [14, 2, ARM_CODE[arm], int(cid), di]
    rx = Reactor(chem, prm, dmu, np.random.SeedSequence(ss), flux_ep=arm in ("P", "M"),
                 day_night=DAY_NIGHT if arm == "C" else 0)
    if arm == "P":
        rx.n[chem.index(COPIER)] = COPIER_SEED
        rx.n_start, rx.phi0 = rx.n.copy(), rx.phi(rx.n)
    t0 = time.time()
    rx.run()
    late, led = rx.late(), rx.ledger_residuals()
    sig = rx.series["sigma"][rx.late_from:]
    sd = float(sig.std(ddof=1))
    row = dict(arm=arm, chem=cid, dmu=dmu, capture=late["capture"], sigma_rate=late["sigma_rate"],
               sigma_flux_rate=late["sigma_flux_rate"] if rx.flux_ep else float("nan"),
               sigma_z=float(sig.mean() / (sd / np.sqrt(len(sig)))) if sd > 0 else 0.0,
               poly_frac=late["poly_frac"], poly_frac_eq=eq_poly_frac(chem, prm) if dmu == 0 else float("nan"),
               leak_frac=late["leak"] / max(late["fuel_in"], 1.0),
               led_mass=led["mass"], led_fuel=led["fuel"], led_phi=led["phi_rel"],
               steps=rx.steps, rejects=rx.rejects)
    if detect:
        any_raf = False
        for name, (n_min, j_min) in VARIANTS.items():
            r = realised_raf(rx, n_min, j_min)
            row.update({f"raf_{name}": int(r["raf"]), f"raf_size_{name}": r["raf_size"]})
            any_raf |= bool(r["raf"])
        row.update(lag_025=float("nan"), lag_050=float("nan"), lag_100=float("nan"),
                   c_intact_lag=float("nan"), c_twin_lag=float("nan"), q=float("nan"))
        if any_raf or arm in ("P", "M"):
            tw = sterilised_twin(rx, np.random.SeedSequence(ss + [7]))
            for f in (0.25, 0.5, 1.0):
                row[f"lag_{int(f * 100):03d}"] = twin_lag(rx, tw, f)
            w = max(1, int(row["lag_050"]))
            row["c_intact_lag"] = rx.window(rx.late_from, rx.late_from + w)["capture"]
            row["c_twin_lag"] = tw.window(0, w)["capture"]
            row["q"] = shuffle_percentile(rx, np.random.SeedSequence(ss + [8]))
        if arm in ("R", "C"):
            row.update({k: int(v) for k, v in potential_raf(chem).items()})
    row["seconds"] = round(time.time() - t0, 1)
    return row


# ---- gates that do not depend on the arms ---------------------------------------------

def ldb_identity_error(chem, prm: SoupParams, dmu: float, seed: int = 0, trials: int = 8) -> float:
    """Gate 3a. For single events, ln[a_forward(n) / a_backward(n')] must equal Phi(n) - Phi(n').
    The catalyst prefactor is divided out (it differs between n and n' only when a participant
    is itself a catalyst, and it multiplies both directions)."""
    rx = Reactor(chem, prm, dmu, seed)
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(trials):
        n = rng.integers(0, 60, chem.n_species)
        a0 = rx.propensities(n)
        p0 = rx._prefactors(n)
        for r in range(chem.n_sites):
            for kind in (0, 1):
                n1 = n.copy()
                n1[chem.x[r]] -= 1; n1[chem.y[r]] -= 1; n1[chem.z[r]] += 1
                if kind:
                    n1[chem.iF] -= 1; n1[chem.iW] += 1
                if n1.min() < 0:
                    continue
                af, ab = a0[2 * kind][r], rx.propensities(n1)[1 + 2 * kind][r]
                if af > 0 and ab > 0:
                    corr = np.log(p0[kind][r] / rx._prefactors(n1)[kind][r])
                    worst = max(worst, abs(np.log(af / ab) - corr - (rx.phi(n) - rx.phi(n1))))
        n1 = n.copy(); n1[chem.iF] -= 1; n1[chem.iW] += 1
        if n1.min() >= 0 and a0[4] > 0:
            worst = max(worst, abs(np.log(a0[4] / rx.propensities(n1)[5]) - (rx.phi(n) - rx.phi(n1))))
    return float(worst)


def closed_box(chem, prm: SoupParams, dmu: float, seed) -> dict:
    """Gate 1. No flow. Fuel and waste start in their equilibrium ratio. The soup must settle
    at the Boltzmann composition and its entropy production must fall to zero within noise."""
    n0 = np.zeros(chem.n_species, np.int64)
    n0[chem.index("a")] = n0[chem.index("b")] = prm.n_mono
    f = prm.n_fuel * np.exp(-dmu) / (1.0 + np.exp(-dmu))
    n0[chem.iF] = int(round(f)); n0[chem.iW] = prm.n_fuel - int(round(f))
    rx = Reactor(chem, prm, dmu, seed, flow=False, n0=n0, flux_ep=True).run()
    eq = equilibrium_counts(chem, prm.n_mono, prm.n_mono, prm.c0)
    mean_n = rx.mean_late_counts()
    d2 = chem.lens == 2
    sig = rx.series["sigma"][rx.late_from:]
    led = rx.ledger_residuals()
    return dict(dmu=dmu, dimers=float(mean_n[d2].sum()), dimers_eq=float(eq[d2].sum()),
                dimer_rel_err=float(abs(mean_n[d2].sum() / eq[d2].sum() - 1.0)),
                sigma_z=float(sig.mean() / (sig.std(ddof=1) / np.sqrt(len(sig)))),
                sigma_rate=float(sig.mean()), early_sigma=float(rx.series["sigma"][:20].sum()),
                led_mass=led["mass"], led_phi=led["phi_rel"], fw=led["fw_closed"])


def run_gates(out: str, prm: SoupParams = PRM) -> dict:
    chem = random_chemistry(1000, prm)          # a plumbing chemistry, never an evidence seed
    res = dict(ldb_error=max(ldb_identity_error(chem, prm, d, seed=i) for i, d in enumerate((0.0, 8.0, 12.0))),
               closed=[closed_box(chem, prm, d, np.random.SeedSequence([14, 3, i])) for i, d in enumerate((0.0, 8.0))])
    res["gate1"] = all(c["dimer_rel_err"] < 0.10 and abs(c["sigma_z"]) < 4.0 and c["led_mass"] == 0 and c["fw"] == 0
                       for c in res["closed"])
    res["gate3a"] = res["ldb_error"] < 1e-8
    os.makedirs(out, exist_ok=True)
    with open(f"{out}/s14_gates.json", "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    return res


# ---- analysis ---------------------------------------------------------------------------

def _boot(values_by_cluster: list[list[float]], stat=np.mean, seed: int = 0):
    """Percentile bootstrap that resamples clusters (chemistries) and pools their values."""
    cl = [np.asarray(v, float) for v in values_by_cluster if len(v)]
    if not cl:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    point = float(stat(np.concatenate(cl)))
    b = np.empty(N_BOOT)
    for i in range(N_BOOT):
        pick = rng.integers(0, len(cl), len(cl))
        b[i] = stat(np.concatenate([cl[j] for j in pick]))
    return point, float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975))


def emerged(r: dict, variant: str = "main", lag_key: str = "lag_050", lag_min: float = LAG_MIN,
            closure_only: bool = False) -> bool:
    if not r.get(f"raf_{variant}"):
        return False
    return True if closure_only else (r[lag_key] >= lag_min)


def analyze(rows: list[dict], gates: dict | None, out: str):
    by = lambda arm, dmu=None: [r for r in rows if r["arm"] == arm and (dmu is None or r["dmu"] == dmu)]
    L = ["# S14 results", "", "runs: " + ", ".join(f"{a}={len(by(a))}" for a in ARM_CODE), ""]

    # ---- gates
    L += ["## Gates (all must pass, or nothing below is reported as a result)", ""]
    g = {}
    if gates:
        g["1 detailed balance (closed box)"] = bool(gates["gate1"])
        g["3a detailed-balance identity"] = bool(gates["gate3a"])
    g["2 ledgers (mass, fuel exact; free-energy books to 1e-6)"] = all(
        r["led_mass"] == 0 and r["led_fuel"] == 0 and r["led_phi"] < 1e-6 for r in rows)
    ctrl = by("P") + by("M")
    g["3b flux entropy production agrees with the books in the controls (5%)"] = bool(ctrl) and all(
        abs(r["sigma_flux_rate"] / r["sigma_rate"] - 1.0) < 0.05 for r in ctrl)
    g["3c entropy production is not negative in any late window (z > -4)"] = all(r["sigma_z"] > -4.0 for r in rows)
    r0 = by("R", 0.0)
    ex = np.array([r["poly_frac"] - r["poly_frac_eq"] for r in r0])
    g["4 no drive, no structure"] = bool(len(ex)) and bool(
        ex.mean() - 3 * ex.std(ddof=1) / np.sqrt(len(ex)) <= 0
        and all(r["poly_frac"] <= 2 * r["poly_frac_eq"] + 0.005 for r in r0))
    nP, nM = sum(emerged(r) for r in by("P")), sum(emerged(r) for r in by("M"))
    g[f"5 detector: P fires in {nP}/{len(by('P'))} (need >= 8 of 10), M in {nM}/{len(by('M'))} (need <= 2 of 10)"] = (
        len(by("P")) == 10 and len(by("M")) == 10 and nP >= 8 and nM <= 2)
    for k, v in g.items():
        L.append(f"- Gate {k}: {'PASS' if v else 'FAIL'}")
    if gates:
        for c in gates["closed"]:
            L.append(f"  - closed box, drive {c['dmu']:g}: dimers {fmt(c['dimers'], 1)} vs equilibrium {fmt(c['dimers_eq'], 1)}; "
                     f"late entropy production z = {fmt(c['sigma_z'], 2)}")
        L.append(f"  - detailed-balance identity, worst error: {gates['ldb_error']:.2e}")
    if len(ex):
        L.append(f"  - no drive: mean polymer fraction minus equilibrium = {ex.mean():.5f} (max run {ex.max():.5f})")
    ok = all(g.values()) and gates is not None
    L += ["", f"**All gates pass: {'YES' if ok else 'NO'}**", ""]

    # ---- arms
    L += ["## Arms (late window; mean [95% bootstrap interval])", "",
          "| arm | drive | runs | capture | entropy rate (k_B per residence time) | polymer fraction | E rate | closure alone |",
          "|---|---|---|---|---|---|---|---|"]
    for arm in ("R", "N", "C", "P", "M"):
        for d in DRIVES:
            rs = by(arm, d)
            if not rs:
                continue
            cell = lambda k: "{} [{}, {}]".format(*[fmt(v, 4) for v in _boot([[r[k]] for r in rs])])
            sg = "{} [{}, {}]".format(*[fmt(v, 1) for v in _boot([[r["sigma_rate"]] for r in rs])])
            e = np.mean([emerged(r) for r in rs]) if "raf_main" in rs[0] else np.nan
            c = np.mean([emerged(r, closure_only=True) for r in rs]) if "raf_main" in rs[0] else np.nan
            L.append(f"| {arm} | {d:g} | {len(rs)} | {cell('capture')} | {sg} | {cell('poly_frac')} | {fmt(e)} | {fmt(c)} |")

    # ---- hypotheses
    L += ["", "## Preregistered hypotheses", ""]
    top, low = by("R", TOP), {r["chem"]: r for r in by("R", LOW)}
    rate, lo, hi = _boot([[float(emerged(r))] for r in top])
    L.append(f"- **H14a** copying appears. E rate in arm R at the top drive: {fmt(rate)} [{fmt(lo)}, {fmt(hi)}] "
             f"({sum(emerged(r) for r in top)} of {len(top)} chemistries). Lower bound above 0.05: "
             f"{'SUPPORTED' if lo > 0.05 else 'NOT supported'}. Against 0.01: {'yes' if lo > 0.01 else 'no'}; "
             f"against 0.10: {'yes' if lo > 0.10 else 'no'}.")
    pairs = [[float(emerged(r)) - float(emerged(low[r["chem"]]))] for r in top if r["chem"] in low]
    d, lo, hi = _boot(pairs)
    L.append(f"- **H14b** more drive, more copying. E rate at drive {TOP:g} minus at drive {LOW:g}, paired by chemistry: "
             f"{fmt(d)} [{fmt(lo)}, {fmt(hi)}] -> {'SUPPORTED' if lo > 0 else 'NOT supported'}.")
    em = [r for r in by("R") if r["dmu"] > 0 and emerged(r)]
    chems = sorted({r["chem"] for r in em})
    if len(em) >= 5:
        d, lo, hi = _boot([[r["c_intact_lag"] - r["c_twin_lag"] for r in em if r["chem"] == c] for c in chems])
        L.append(f"- **H14c** (check, expected by construction) copiers spend the fuel. Capture, intact minus sterilised twin, "
                 f"over the twin's lag: {fmt(d)} [{fmt(lo)}, {fmt(hi)}] ({len(em)} runs) -> {'SUPPORTED' if lo > 0 else 'NOT supported'}.")
        q, lo, hi = _boot([[r["q"] for r in em if r["chem"] == c] for c in chems])
        qs = np.array([r["q"] for r in em])
        L.append(f"- **H14d** copiers are tuned to the drive. Mean shuffle percentile q: {fmt(q)} [{fmt(lo)}, {fmt(hi)}] "
                 f"-> {'SUPPORTED (above 0.5)' if lo > 0.5 else 'REVERSED (below 0.5)' if hi < 0.5 else 'NOT supported'}. "
                 f"Share with q > 0.95: {fmt((qs > 0.95).mean())}; with q < 0.05: {fmt((qs < 0.05).mean())}.")
    else:
        L.append(f"- **H14c**, **H14d**: NOT RUN. Only {len(em)} arm-R runs met the emergence criterion (fewer than 5).")

    # ---- sensitivity and descriptive
    L += ["", "## Sensitivity of the emergence criterion (arm R, top drive)", ""]
    for lab, kw in (("as registered", {}), ("activity cut-offs halved", dict(variant="half")),
                    ("activity cut-offs doubled", dict(variant="double")),
                    ("twin fraction 0.25", dict(lag_key="lag_025")), ("twin fraction 1.0", dict(lag_key="lag_100")),
                    ("lag 5 residence times", dict(lag_min=5.0)), ("lag 20 residence times", dict(lag_min=20.0)),
                    ("closure alone", dict(closure_only=True))):
        L.append(f"- {lab}: {sum(emerged(r, **kw) for r in top)} of {len(top)}")
    L += ["", "## Descriptive (not preregistered as tests)", ""]
    if top and "pot_raf" in top[0]:
        pr = [r for r in top if r["pot_raf"]]
        L.append(f"- Chemistries where a closed set is possible at all (structural, from the catalysis table): "
                 f"{len(pr)} of {len(top)}; of those, {sum(r['pot_raf_fuel'] > 0 for r in pr)} include a fuel-coupled join.")
    for d in DRIVES:
        rs = by("R", d)
        if rs and "raf_main" in rs[0]:
            L.append(f"- Arm R, drive {d:g}: closure in {sum(emerged(r, closure_only=True) for r in rs)}, "
                     f"E in {sum(emerged(r) for r in rs)} of {len(rs)}.")
    cy = {r["chem"]: r for r in by("C")}
    if cy:
        both = [r for r in top if r["chem"] in cy]
        L.append(f"- Exploratory, day/night feed (arm C, period {DAY_NIGHT}, same mean, same chemistries as arm R at the top drive): "
                 f"E in {sum(emerged(cy[r['chem']]) for r in both)} of {len(both)} under cycling against "
                 f"{sum(emerged(r) for r in both)} under a steady feed; closure alone {sum(emerged(cy[r['chem']], closure_only=True) for r in both)} "
                 f"against {sum(emerged(r, closure_only=True) for r in both)}.")
    for arm in ("P", "M"):
        rs = by(arm)
        if rs:
            L.append(f"- Arm {arm}: twin lag (residence times, censored at 100) "
                     f"{sorted(int(r['lag_050']) for r in rs)}; mean q {fmt(np.mean([r['q'] for r in rs]))}; "
                     f"mean capture {fmt(np.mean([r['capture'] for r in rs]))}.")
    emit(L, f"{out}/s14_report.md")
    return ok


def _read(path: str) -> list[dict]:
    rows = []
    for f in sorted(glob.glob(f"{path}/**/s14_runs*.csv", recursive=True)):
        for r in csv.DictReader(open(f)):
            rows.append({k: (v if k == "arm" else float(v) if v not in ("", "nan") else float("nan")) for k, v in r.items()})
    for r in rows:
        r["chem"] = int(r["chem"])
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", type=str, default="R", help="R, N, P, M, C, or gates")
    ap.add_argument("--chem0", type=int, default=0, help="first chemistry (pilots use >= 1000)")
    ap.add_argument("--chems", type=int, default=20)
    ap.add_argument("--drives", type=str, default=None, help="comma-separated; default is the arm's registered set")
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 2))
    ap.add_argument("--out", type=str, default="results")
    ap.add_argument("--no-detect", action="store_true", help="plumbing pilots of arm R: skip the detector")
    ap.add_argument("--analyze", type=str, default=None)
    args = ap.parse_args(argv)
    if args.analyze:
        rows = _read(args.analyze)
        gfiles = sorted(glob.glob(f"{args.analyze}/**/s14_gates.json", recursive=True))
        gates = json.load(open(gfiles[-1])) if gfiles else None
        keys = list(dict.fromkeys(k for r in rows for k in r))
        os.makedirs(args.out, exist_ok=True)
        with open(f"{args.out}/s14_all.csv", "w", newline="") as f:      # not s14_runs*: never re-read as input
            wr = csv.DictWriter(f, fieldnames=keys, restval="")
            wr.writeheader(); wr.writerows(rows)
        ok = analyze(rows, gates, args.out)
        raise SystemExit(0 if ok else 2)
    if args.arm == "gates":
        res = run_gates(args.out)
        raise SystemExit(0 if res["gate1"] and res["gate3a"] else 2)
    if args.drives:
        drives = [float(d) for d in args.drives.split(",")]
    else:
        drives = list(DRIVES) if args.arm in ("R", "N") else [TOP]
    ids = range(args.chem0, args.chem0 + args.chems)
    jobs = [dict(arm=args.arm, chem=c, dmu=d, detect=not args.no_detect) for c in ids for d in drives]
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i, r in enumerate(ex.map(run_one, jobs, chunksize=1)):
            rows.append(r)
            if (i + 1) % 10 == 0 or i + 1 == len(jobs):
                print(f"  {i + 1}/{len(jobs)}", flush=True)
    write_csv(rows, f"{args.out}/s14_runs_{args.arm}_{args.chem0}.csv")


if __name__ == "__main__":
    main()
