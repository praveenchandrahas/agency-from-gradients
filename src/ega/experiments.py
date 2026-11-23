"""Reproducible experiment runner for the first EGA simulation suite."""
from __future__ import annotations
import argparse
import csv
import json
from dataclasses import replace
from pathlib import Path
from .model import ARMS, Config, simulate

def run_suite(out: Path, seeds: int = 20, steps: int = 1200) -> list[dict]:
    out.mkdir(parents=True, exist_ok=True)
    designs = {
        "E01_static": {"drift_rate": 0.0, "locks": 1},
        "E03_drift": {"drift_rate": 0.002, "locks": 1},
        "E04_multilock": {"drift_rate": 0.0, "locks": 3},
    }
    records = []
    for design, overrides in designs.items():
        for barrier in (0.0, 4.0, 8.0, 12.0):
            for seed in range(seeds):
                cfg = Config(barriers=(barrier,), steps=steps, seed=seed, **overrides)
                for arm in ARMS:
                    result = simulate(arm, cfg)
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
                        "target_changes": result["target_changes"],
                    })
    with (out / "replicates.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)
    summary = {}
    for design in designs:
        summary[design] = {}
        for barrier in (0.0, 4.0, 8.0, 12.0):
            summary[design][str(barrier)] = {}
            for arm in ARMS:
                vals = [r for r in records if r["design"] == design
                        and r["barrier_kT"] == barrier and r["arm"] == arm]
                summary[design][str(barrier)][arm] = {
                    key: sum(float(v[key]) for v in vals) / len(vals)
                    for key in ("late_sigma", "late_throughput", "cumulative_sigma",
                                "cumulative_fuel_spent", "final_population",
                                "mean_population_late", "late_key_distance")
                }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    manifest = {"seeds": seeds, "steps": steps, "arms": list(ARMS),
                "designs": designs, "barriers_kT": [0, 4, 8, 12],
                "warning": "Exploratory model output; not preregistered or empirical evidence."}
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
