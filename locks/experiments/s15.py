"""S15 confirmatory runner. See locks/PREREGISTRATION.md.

Stage 1 runs N, D and L for one (n_bits, B) cell.
Stage 2 runs M and U, matched to the mean late catalyst count of L in the same cell, read
from stage 1's output. At B = 16 it also runs the equivalent-library sweep (M at 10x and 100x).

One JSON file per run. Example:
    PYTHONPATH=. python experiments/s15.py --stage 1 --n-bits 24 --B 16 --out out
    PYTHONPATH=. python experiments/s15.py --stage 2 --n-bits 24 --B 16 --match-from out --out out
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from multiprocessing import Pool

import numpy as np

from locks import Config, run

T_END = 4000.0
WINDOWS = [(1500.0, 2000.0), (3500.0, 4000.0)]     # secondary, primary
REC_EVERY = 50.0
LIBRARY_B = 16.0
LIBRARY_MULT = (10, 100)


def name(arm, n_bits, B, seed):
    return f"{arm}_n{n_bits}_B{B:g}_s{seed}.json"


def one(job):
    label, cfg, seed, out = job
    r = run(cfg, seed=seed, t_end=T_END, rec_every=REC_EVERY, windows=WINDOWS)
    r["label"] = label
    with open(os.path.join(out, name(label, cfg.n_bits, cfg.B[0], seed)), "w") as f:
        json.dump(r, f)
    return label, seed


def matched_count(src, n_bits, B, seeds):
    vals = []
    for s in seeds:
        with open(os.path.join(src, name("L", n_bits, B, s))) as f:
            vals.append(json.load(f)["windows"][-1]["n"])
    return int(round(float(np.mean(vals)))), vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, choices=(1, 2), required=True)
    ap.add_argument("--n-bits", type=int, required=True)
    ap.add_argument("--B", type=float, required=True)
    ap.add_argument("--seeds", default="0-19")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--match-from", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--t-end", type=float, default=None, help="plumbing checks only")
    a = ap.parse_args()
    global T_END, WINDOWS
    if a.t_end is not None:
        T_END = a.t_end
        WINDOWS = [(0.4 * T_END, 0.5 * T_END), (0.9 * T_END, T_END)]
    lo, hi = (int(x) for x in a.seeds.split("-"))
    seeds = list(range(lo, hi + 1))
    os.makedirs(a.out, exist_ok=True)
    base = Config(n_bits=a.n_bits, B=(a.B,))
    jobs = []
    if a.stage == 1:
        for arm in ("N", "D", "L"):
            jobs += [(arm, base.with_(arm=arm), s, a.out) for s in seeds]
    else:
        src = a.match_from or a.out
        n, vals = matched_count(src, a.n_bits, a.B, seeds)
        with open(os.path.join(a.out, f"match_n{a.n_bits}_B{a.B:g}.json"), "w") as f:
            json.dump(dict(n_bits=a.n_bits, B=a.B, matched=n, L_counts=vals), f)
        for arm in ("M", "U"):
            jobs += [(arm, base.with_(arm=arm, n_fixed=n), s, a.out) for s in seeds]
        if a.B == LIBRARY_B:
            for m in LIBRARY_MULT:
                jobs += [(f"M{m}", base.with_(arm="M", n_fixed=n * m), s, a.out) for s in seeds]
    # longest jobs first
    order = {"L": 0, "D": 1, "M100": 2, "M10": 3, "M": 4, "U": 5, "N": 6}
    jobs.sort(key=lambda j: order.get(j[0], 9))
    with Pool(a.workers) as p:
        for label, seed in p.imap_unordered(one, jobs):
            print(f"done {label} n{a.n_bits} B{a.B:g} seed {seed}", flush=True)


if __name__ == "__main__":
    main()
