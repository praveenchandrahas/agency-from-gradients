"""Reproducible experiment runner for the first EGA simulation suite."""
from __future__ import annotations
import argparse
import csv
import gzip
import json
from pathlib import Path
import numpy as np
from .model import ARMS, Config, simulate


def _bootstrap_mean(values: list[float], seed: int = 12345, draws: int = 5000) -> dict:
    x = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    samples = rng.choice(x, size=(draws, len(x)), replace=True).mean(axis=1)
    return {"mean": float(x.mean()), "sd": float(x.std(ddof=1)) if len(x) > 1 else 0.0,
            "ci95_low": float(np.quantile(samples, 0.025)),
            "ci95_high": float(np.quantile(samples, 0.975)), "n": int(len(x))}


def run_suite(out: Path, seeds: int = 20, steps: int = 1200) -> list[dict]:
    out.mkdir(parents=True, exist_ok=True)
    designs = {
        "E01_static": {"drift_rate": 0.0, "locks": 1},
        "E03_drift": {"drift_rate": 0.002, "locks": 1},
        "E04_multilock": {"drift_rate": 0.0, "locks": 3},
    }
    records: list[dict] = []
    trajectory_path = out / "trajectories.jsonl.gz"
    with gzip.open(trajectory_path, "wt", encoding="utf-8") as raw:
        for design, overrides in designs.items():
            for barrier in (0.0, 4.0, 8.0, 12.0):
                for seed in range(seeds):
                    cfg = Config(barriers=(barrier,), steps=steps, seed=seed, **overrides)
                    for arm in ARMS:
                        result = simulate(arm, cfg)
                        raw.write(json.dumps({
                            "design": design, "barrier_kT": barrier, "seed": seed,
                            "arm": arm, "trajectory": result["trajectory"]
                        }, separators=(",", ":")) + "\n")
                        records.append({
                            "design": design, "barrier_kT": barrier, "seed": seed,
                            "arm": arm, "late_sigma": result["mean_sigma_late"],
                            "late_throughput": result["mean_throughput_late"],
                            "cumulative_sigma": result["cumulative_sigma"],
                            "cumulative_fuel_spent": result["cumulative_fuel_spent"],
                            "final_population": result["final_population"],
                            "mean_population_late": result["mean_population_late"],
                            "late_key_distance": result["late_key_distance"],
                            "extinct_at": result["extinct_at"],
                            "stored_energy_final": result["stored_energy_final"],
                            "reproduction_energy": result["cumulative_reproduction_energy"],
                            "maintenance_energy": result["cumulative_maintenance_energy"],
                            "adaptive_search_cost": result["cumulative_adaptive_cost"],
                            "target_changes": result["target_changes"],
                        })
    with (out / "replicates.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    metrics = ("late_sigma", "late_throughput", "cumulative_sigma",
               "cumulative_fuel_spent", "final_population", "mean_population_late",
               "late_key_distance", "stored_energy_final")
    summary: dict = {}
    contrasts: dict = {}
    for design in designs:
        summary[design] = {}
        contrasts[design] = {}
        for barrier in (0.0, 4.0, 8.0, 12.0):
            key = str(barrier)
            summary[design][key] = {}
            contrasts[design][key] = {}
            cells = {(arm, seed): next(r for r in records if r["design"] == design
                     and r["barrier_kT"] == barrier and r["arm"] == arm and r["seed"] == seed)
                     for arm in ARMS for seed in range(seeds)}
            for arm in ARMS:
                summary[design][key][arm] = {
                    metric: _bootstrap_mean([cells[(arm, s)][metric] for s in range(seeds)],
                                            seed=1000 + int(barrier * 10) + list(ARMS).index(arm))
                    for metric in metrics
                }
            for comparator in ("M", "D", "A", "U", "N"):
                contrasts[design][key][f"L_minus_{comparator}"] = {
                    metric: _bootstrap_mean(
                        [cells[("L", s)][metric] - cells[(comparator, s)][metric]
                         for s in range(seeds)],
                        seed=2000 + int(barrier * 10) + list(ARMS).index(comparator)
                    ) for metric in ("late_sigma", "late_throughput", "cumulative_sigma",
                                     "cumulative_fuel_spent")
                }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    (out / "paired_contrasts.json").write_text(json.dumps(contrasts, indent=2))
    manifest = {
        "seeds": seeds, "steps": steps, "arms": list(ARMS),
        "designs": designs, "barriers_kT": [0, 4, 8, 12],
        "primary_exploratory_contrasts": ["L_minus_M", "L_minus_D", "L_minus_A"],
        "uncertainty": "paired-seed bootstrap percentile intervals; exploratory only",
        "warning": "Exploratory model output; not preregistered or empirical evidence."
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return records


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="results/initial")
    p.add_argument("--seeds", type=int, default=20)
    p.add_argument("--steps", type=int, default=1200)
    a = p.parse_args()
    records = run_suite(Path(a.out), a.seeds, a.steps)
    print(f"Wrote {len(records)} replicate-arm rows to {a.out}")


if __name__ == "__main__":
    main()
