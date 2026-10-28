"""Run (Config, seed) jobs, optionally in parallel, and write CSV."""
from __future__ import annotations

import csv
import os
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache

from .config import Config
from .probes import viability_probe
from .world import World, passive_entropy_rate


@lru_cache(maxsize=None)
def _passive(cfg: Config) -> float:
    return passive_entropy_rate(cfg)


def run_one(job: dict) -> dict:
    cfg: Config = job["cfg"]
    seed: int = job["seed"]
    w = World(cfg, seed).run()
    row = dict(job["labels"])
    row["seed"] = seed
    row.update(w.summary(passive_rate=_passive(cfg)))
    if job.get("probe"):
        row.update(viability_probe(w, seed=seed))
    return row


def run_jobs(jobs: list[dict], workers: int = 1, progress: bool = True) -> list[dict]:
    if workers <= 1:
        out = []
        for i, j in enumerate(jobs):
            out.append(run_one(j))
            if progress and (i + 1) % 10 == 0:
                print(f"  {i + 1}/{len(jobs)}", flush=True)
        return out
    with ProcessPoolExecutor(max_workers=workers) as ex:
        out = []
        for i, r in enumerate(ex.map(run_one, jobs, chunksize=1)):
            out.append(r)
            if progress and (i + 1) % 10 == 0:
                print(f"  {i + 1}/{len(jobs)}", flush=True)
        return out


def write_csv(rows: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=keys)
        wr.writeheader()
        wr.writerows(rows)
