"""Shared runner: fan runs out over processes, write one CSV of runs and one of time series."""
from __future__ import annotations

import csv
import math
import os
import sys
import time
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from starlight import Config, run  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")

STEPS = 40_000          # evolving runs
STEPS_FIXED = 10_000    # fixed-trait controls: nothing evolves, so they settle fast
LATE = 5_000            # late window: the last 5,000 steps
REC = 200
SEEDS = range(0, 20)    # confirmatory seeds. Pilots used seeds >= 1000 only.

LATE_FIELDS = ("capture", "capture_b", "heat", "heat_b", "emitted", "pop", "a", "m", "g", "f", "mg",
               "directed_rate", "move_rate", "light_at_org", "e_mean")


def _one(task):
    labels, cfg, seed, steps = task
    rows = run(cfg, seed, steps, rec_every=REC, check=True)
    late = [r for r in rows if r["t"] > steps - LATE]
    out = dict(labels)
    out.update(seed=seed, steps=steps, extinct=rows[-1]["extinct"],
               ledger_worst=max(r["ledger_worst"] for r in rows))
    for k in LATE_FIELDS:
        vals = [r[k] for r in late if not (isinstance(r[k], float) and math.isnan(r[k]))]
        # capture, heat and population are zero once a world is extinct; traits are undefined
        out[k] = float(np.mean([r[k] for r in late])) if k in ("capture", "capture_b", "heat", "heat_b",
                                                              "emitted", "pop") \
            else (float(np.mean(vals)) if vals else float("nan"))
    series = [dict(labels, seed=seed, **{k: r[k] for k in ("t", "speed", "pop", "capture", "capture_b",
                                                           "heat", "heat_b", "a", "m", "g", "f",
                                                           "directed_rate", "move_rate")})
              for r in rows[::5]]            # every 1,000 steps is enough for plots
    return out, series


def execute(name: str, tasks: list, smoke: bool = False):
    os.makedirs(RESULTS, exist_ok=True)
    if smoke:
        tasks = [(lab, cfg, seed, 2_000) for lab, cfg, seed, _ in tasks if seed < 2]
    t0 = time.time()
    with Pool(os.cpu_count()) as pool:
        res = pool.map(_one, tasks, chunksize=1)
    suffix = "_smoke" if smoke else ""
    runs = [r for r, _ in res]
    series = [s for _, ss in res for s in ss]
    for kind, data in (("runs", runs), ("series", series)):
        path = os.path.join(RESULTS, f"{name}_{kind}{suffix}.csv")
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)
    print(f"{name}: {len(runs)} runs in {time.time() - t0:.0f}s, "
          f"{sum(r['extinct'] for r in runs)} extinct, "
          f"worst ledger error {max(r['ledger_worst'] for r in runs):.2e}")
    return runs


BASE = Config()
__all__ = ["BASE", "Config", "replace", "execute", "STEPS", "STEPS_FIXED", "SEEDS"]
