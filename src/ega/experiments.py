"""Reproducible experiment runner with L-matched static controls."""
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


def run_suite(out: Path, seeds: int = 10, steps: int = 300) -> list[dict]:
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
                    cfg = Config(barriers=(barrier,), steps=steps, seed=seed,
                                 key_bits=16, **overrides)
                    # L is run first so static controls can be matched to its
                    # late-window catalyst abundance for this paired seed.
                    l_result = simulate("L", cfg)
                    matched_count = max(1, int(round(l_result["mean_population_late"])))
                    results = {"L": l_result}
                    for arm in ("N", "M", "D", "U", "A"):
                        results[arm] = simulate(arm, cfg)
                    for arm in ("Mmatched", "Amatched", "Umatched"):
                        results[arm] = simulate(arm, cfg, fixed_population_size=matched_count)

                    for arm in ARMS:
                        result = results[arm]
                        raw.write(json.dumps({
                            "design": design, "barrier_kT": barrier, "seed": seed,
                            "arm": arm, "matched_count": matched_count,
                            "trajectory": result["trajectory"]
                        }, separators=(",", ":")) + "\n")
                        records.append({
                            "design": design, "barrier_kT": barrier, "seed": seed,
                            "arm": arm, "matched_count": matched_count,
                            "initial_population": result["initial_population"],
                            "late_sigma": result["mean_sigma_late"],
                            "late_throughput": result["mean_throughput_late"],
                            "late_throughput_per_catalyst": (
                                result["mean_throughput_late"] / result["mean_population_late"]
                                if result["mean_population_late"] > 0 else 0.0
                            ),
                            "late_sigma_per_catalyst": (
                                result["mean_sigma_late"] / result["mean_population_late"]
                                if result["mean_population_late"] > 0 else 0.0
                            ),
                            "cumulative_sigma": result["cumulative_sigma"],
                            "cumulative_fuel_spent": result["cumulative_fuel_spent"],
                            "fuel_balance_residual": result["fuel_balance_residual"],
                            "final_population": result["final_population"],
                            "mean_population_late": result["mean_population_late"],
                            "late_key_distance": result["late_key_distance"],
                            "extinct_at": result["extinct_at"],
                            "stored_energy_final": result["stored_energy_final"],
                            "reproduction_energy": result["cumulative_reproduction_energy"],
                            "maintenance_energy": result["cumulative_maintenance_energy"],
                            "adaptive_search_cost": result["cumulative_adaptive_cost"],
                            "mutation_energy": result["cumulative_mutation_energy"],
                            "target_changes": result["target_changes"],
                        })
    with (out / "replicates.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    metrics = ("late_sigma", "late_throughput", "cumulative_sigma",
               "cumulative_fuel_spent", "final_population", "mean_population_late",
               "late_key_distance", "stored_energy_final",
               "late_throughput_per_catalyst", "late_sigma_per_catalyst")
    by_key = {(r["design"], r["barrier_kT"], r["seed"], r["arm"]): r for r in records}
    summary: dict = {}
    contrasts: dict = {}
    comparators = ("M", "Mmatched", "D", "A", "Amatched", "U", "Umatched", "N")
    for design in designs:
        summary[design] = {}
        contrasts[design] = {}
        for barrier in (0.0, 4.0, 8.0, 12.0):
            key = str(barrier)
            summary[design][key] = {}
            contrasts[design][key] = {}
            for arm in ARMS:
                summary[design][key][arm] = {
                    metric: _bootstrap_mean(
                        [by_key[(design, barrier, s, arm)][metric] for s in range(seeds)],
                        seed=1000 + int(barrier * 10) + list(ARMS).index(arm))
                    for metric in metrics
                }
            for comparator in comparators:
                contrasts[design][key][f"L_minus_{comparator}"] = {
                    metric: _bootstrap_mean(
                        [by_key[(design, barrier, s, "L")][metric] -
                         by_key[(design, barrier, s, comparator)][metric]
                         for s in range(seeds)],
                        seed=2000 + int(barrier * 10) + list(ARMS).index(comparator)
                    ) for metric in ("late_sigma", "late_throughput", "cumulative_sigma",
                                     "cumulative_fuel_spent")
                }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    (out / "paired_contrasts.json").write_text(json.dumps(contrasts, indent=2))
    manifest = {
        "seeds": seeds, "steps": steps, "key_bits": 16, "arms": list(ARMS),
        "designs": designs, "barriers_kT": [0, 4, 8, 12],
        "matched_controls": "Mmatched, Amatched and Umatched use the rounded late-window L population for each paired seed",
        "primary_exploratory_contrasts": ["L_minus_Mmatched", "L_minus_D", "L_minus_Amatched"],
        "uncertainty": "paired-seed bootstrap percentile intervals; exploratory only",
        "warning": "Exploratory model output; not preregistered or empirical evidence."
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return records


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="results/matched-key16")
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--steps", type=int, default=300)
    a = p.parse_args()
    if a.seeds < 2:
        p.error("--seeds must be at least 2")
    if a.steps < 10:
        p.error("--steps must be at least 10")
    records = run_suite(Path(a.out), a.seeds, a.steps)
    print(f"Wrote {len(records)} replicate-arm rows to {a.out}")


if __name__ == "__main__":
    main()
