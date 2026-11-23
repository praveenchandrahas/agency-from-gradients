"""Shared runner. Fans runs out over processes and writes four CSVs per experiment.

  <name>_windows.csv   one row per run and window: means of every metric
  <name>_series.csv    every few generations, a chosen set of columns
  <name>_hist.csv      net-energy histograms at the snapshot generations
  <name>_patches.csv   per-patch state at the snapshot generations, replicate 0 only

Raw per-generation tables are not kept. Every run is deterministic given its
seed, so they can be regenerated.
"""
from __future__ import annotations

import hashlib
import os
import platform
import sys
import time
from dataclasses import replace
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from planet import Config, NET_EDGES, Options, build_world, run  # noqa: E402

RESULTS = os.path.join(ROOT, "results")

GENERATIONS = 660            # three times the paper's 220. The first 220 are the paper's, bit for bit.
REPLICATES = range(0, 20)    # replicates 0 to 5 are the paper's own seeds
SNAPSHOTS = (220, 660)
# name: (first generation, last generation), inclusive
WINDOWS = {"g0": (0, 0), "early": (0, 20), "g220": (220, 220), "w220": (201, 220),
           "g660": (660, 660), "w660": (641, 660)}
GROWTH_SPAN = 50             # geometric-mean growth over the 50 generations that end a window

_WORLD = None


def _world(cfg):
    global _WORLD
    if _WORLD is None:
        _WORLD = build_world(cfg)
    return _WORLD


def _one(task):
    labels, scenario_key, replicate, opt, generations, series_cols, series_every = task
    cfg = replace(Config(), generations=generations)
    snaps_at = tuple(g for g in SNAPSHOTS if g <= generations) or (generations,)
    df, snaps = run(scenario_key, replicate, cfg, _world(cfg), replace(opt, snapshot_generations=snaps_at))
    numeric = df.select_dtypes("number").drop(columns=["replicate"])
    last = int(df.generation.iloc[-1])
    pop = df.set_index("generation").population
    windows = []
    for name, (lo, hi) in WINDOWS.items():
        if hi > generations:
            continue
        sel = numeric[(numeric.generation >= lo) & (numeric.generation <= hi)]
        row = dict(labels, replicate=replicate, window=name, last_generation=last, extinct=int(last < generations))
        row.update(sel.drop(columns=["generation"]).mean().to_dict() if len(sel) else {})
        if hi - GROWTH_SPAN >= 0 and hi in pop.index:
            row["growth_geo"] = float((pop[hi] / pop[hi - GROWTH_SPAN]) ** (1.0 / GROWTH_SPAN))
        windows.append(row)
    keep = df[(df.generation % series_every == 0) | df.generation.isin(SNAPSHOTS)]
    series = keep[["generation"] + series_cols].assign(**labels, replicate=replicate)
    hist, patches = [], []
    for s in snaps:
        nz = np.flatnonzero(s["net_hist"])
        hist.append(pd.DataFrame(dict(labels, replicate=replicate, generation=s["generation"],
                                      bin_left=NET_EDGES[nz], count=s["net_hist"][nz], count_c=s["net_hist_c"][nz])))
        if replicate == 0:
            patches.append(pd.DataFrame(dict(labels, generation=s["generation"], patch=np.arange(len(s["patch_count"])),
                                             count=s["patch_count"], count_c=s["patch_count_c"],
                                             field=s["patch_field"], resource=s["patch_resource"],
                                             capture_fraction=s["patch_capture_fraction"],
                                             is_peak=s["patch_is_peak"].astype(int))))
    return windows, series, hist, patches


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def write_run_info():
    lines = [
        f"frozen: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
        f"PREREGISTRATION.md sha256: {sha(os.path.join(ROOT, 'PREREGISTRATION.md'))}",
        f"engine.py sha256: {sha(os.path.join(ROOT, 'planet', 'engine.py'))}",
        f"v0_2.py sha256: {sha(os.path.join(ROOT, 'planet', 'v0_2.py'))}",
        f"python {platform.python_version()} numpy {np.__version__} pandas {pd.__version__}",
    ]
    path = os.path.join(RESULTS, "RUN_INFO.txt")
    if not os.path.exists(path):
        with open(path, "w") as fh:
            fh.write("\n".join(lines) + "\n")


def execute(name: str, tasks: list, series_cols: list, series_every: int = 5, smoke: bool = False):
    """tasks: (labels, scenario_key, replicate, Options)."""
    os.makedirs(RESULTS, exist_ok=True)
    generations = GENERATIONS
    if smoke:
        tasks = [t for t in tasks if t[2] < 2]
        generations = 30
    else:
        write_run_info()
    full = [(lab, key, rep, opt, generations, series_cols, series_every) for lab, key, rep, opt in tasks]
    t0 = time.time()
    with Pool(os.cpu_count()) as pool:
        res = pool.map(_one, full, chunksize=1)
    suffix = "_smoke" if smoke else ""
    windows = pd.DataFrame([w for r in res for w in r[0]])
    tables = {"windows": windows}
    for i, kind in ((1, "series"), (2, "hist"), (3, "patches")):
        parts = [r[i] if i == 1 else pd.concat(r[i]) for r in res if len(r[i])]
        if parts:
            tables[kind] = pd.concat(parts, ignore_index=True)
    for kind, table in tables.items():
        table.to_csv(os.path.join(RESULTS, f"{name}_{kind}{suffix}.csv"), index=False, float_format="%.6g")
    runs = windows.drop_duplicates(subset=[c for c in windows.columns if c in tasks[0][0]] + ["replicate"])
    print(f"{name}: {len(runs)} runs in {time.time() - t0:.0f}s, {int(runs.extinct.sum())} extinct")
    return tables


__all__ = ["Options", "execute", "REPLICATES", "GENERATIONS"]
