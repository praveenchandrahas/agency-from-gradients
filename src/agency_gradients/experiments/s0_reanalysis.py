"""S0 - re-analysis of saved genome trajectories from the earlier Studies 1 and 2.

Question (open from Study 2): did entropy-selected agents evolve *higher forage
thresholds* that keep them below Tier-2 eligibility, despite a higher nominal
invest_propensity?

ASSUMED INPUT SCHEMA (the original evo_*.json files were not available when this
was written, so this is a best guess - adjust ``find_trajectory`` if yours differ):
  * one JSON file per run, e.g. evo_entropy_seed3.json
  * somewhere inside, a key containing "genome" whose value is a list over
    generations, each a list over agents, each a list of floats, with
    index 0 = forage_thresh and index 1 = repair_thresh.
  * the condition is read from the file name: "entropy", "survival" or "random".
If the structure is not found the script stops and prints the keys it saw.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys

import numpy as np

CONDITIONS = ("entropy", "survival", "random")


def condition_of(path: str) -> str:
    name = os.path.basename(path).lower()
    for c in CONDITIONS:
        if c in name:
            return c
    return "unknown"


def _looks_like_traj(x) -> bool:
    try:
        return (isinstance(x, list) and len(x) > 0 and isinstance(x[0], list) and len(x[0]) > 0
                and isinstance(x[0][0], list) and len(x[0][0]) >= 2
                and isinstance(x[0][0][0], (int, float)))
    except Exception:
        return False


def find_trajectory(obj, path=""):
    """Return (path, list-of-generations) for the first genome trajectory found."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "genome" in str(k).lower() and _looks_like_traj(v):
                return f"{path}/{k}", v
        for k, v in obj.items():
            hit = find_trajectory(v, f"{path}/{k}")
            if hit:
                return hit
    elif isinstance(obj, list) and not _looks_like_traj(obj):
        for i, v in enumerate(obj[:50]):
            hit = find_trajectory(v, f"{path}[{i}]")
            if hit:
                return hit
    return None


def keys_seen(obj, depth=0, maxdepth=3):
    if depth > maxdepth or not isinstance(obj, dict):
        return []
    out = []
    for k, v in obj.items():
        out.append("  " * depth + str(k))
        out += keys_seen(v, depth + 1, maxdepth)
    return out


def analyse(files, forage_idx=0, repair_idx=1, tier2_threshold=None, last=5):
    rows, summary = [], {}
    for f in files:
        with open(f) as fh:
            data = json.load(fh)
        hit = find_trajectory(data)
        if hit is None:
            sys.exit(f"No genome trajectory found in {f}. Keys seen:\n" + "\n".join(keys_seen(data)))
        where, traj = hit
        cond = condition_of(f)
        for g, agents in enumerate(traj):
            a = np.asarray(agents, dtype=float)
            if a.ndim != 2 or a.shape[0] == 0:
                continue
            rows.append(dict(file=os.path.basename(f), condition=cond, generation=g, n=a.shape[0],
                             forage_mean=a[:, forage_idx].mean(), repair_mean=a[:, repair_idx].mean()))
        tail = np.concatenate([np.asarray(x, dtype=float) for x in traj[-last:] if len(x)], axis=0)
        s = summary.setdefault(cond, dict(forage=[], repair=[], inelig=[]))
        s["forage"].append(tail[:, forage_idx].mean())
        s["repair"].append(tail[:, repair_idx].mean())
        if tier2_threshold is not None:
            s["inelig"].append(float((tail[:, forage_idx] > tier2_threshold).mean()))
    return rows, summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pattern", help="glob for the saved JSON files, e.g. 'data/evo_*.json'")
    ap.add_argument("--forage-index", type=int, default=0)
    ap.add_argument("--repair-index", type=int, default=1)
    ap.add_argument("--tier2-threshold", type=float, default=None,
                    help="forage_thresh above which an agent is below Tier-2 eligibility")
    ap.add_argument("--last", type=int, default=5, help="final generations to pool")
    ap.add_argument("--out", default="results")
    args = ap.parse_args(argv)
    files = sorted(glob.glob(args.pattern))
    if not files:
        sys.exit(f"No files match {args.pattern!r}")
    rows, summary = analyse(files, args.forage_index, args.repair_index, args.tier2_threshold, args.last)
    os.makedirs(args.out, exist_ok=True)
    with open(f"{args.out}/s0_trajectories.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(files)} files; final-{args.last}-generation means per condition")
    for cond, s in sorted(summary.items()):
        line = (f"  {cond:9s} runs={len(s['forage'])} forage_thresh={np.mean(s['forage']):.3f} "
                f"repair_thresh={np.mean(s['repair']):.3f}")
        if s["inelig"]:
            line += f" frac_below_tier2_eligibility={np.mean(s['inelig']):.3f}"
        print(line)


if __name__ == "__main__":
    main()
