#!/usr/bin/env python3
"""Focused v0.2 test of mutation against large standing-variation controls."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path

import matplotlib.pyplot as plt

from ega.model_v02 import ConfigV02, simulate_v02


def catalyst_free_energy(concentrations, mu_catalyst_std):
    import math
    return sum(
        c * (mu_catalyst_std + math.log(c) - 1.0)
        for c in concentrations if c > 0
    )


def run_one(arm, cfg, schedule, metadata, matched_total):
    result = simulate_v02(arm, cfg, target_schedule=schedule)
    trajectory = result.pop("trajectory")
    initial_c = tuple(cfg.initial_concentrations)
    initial_material = sum(initial_c)
    initial_c_g = catalyst_free_energy(initial_c, cfg.mu_catalyst_std)
    declared_work = (
        initial_c_g + result["cumulative_work_replication"]
        + result["cumulative_work_maintenance"]
    )
    material_investment = initial_material + result["cumulative_replication_net_extent"]
    row = {
        **metadata,
        "arm": arm,
        "matched_total_reference": matched_total,
        "late_throughput": result["late_throughput"],
        "late_entropy_production": result["late_entropy_production"],
        "late_throughput_per_catalyst": (
            result["late_throughput"] / result["final_catalyst_concentration"]
            if result["final_catalyst_concentration"] > 0 else None
        ),
        "cumulative_fuel_reaction_extent": result["cumulative_fuel_reaction_extent"],
        "cumulative_replication_net_extent": result["cumulative_replication_net_extent"],
        "cumulative_work_generation": result["cumulative_work_generation"],
        "cumulative_work_replication": result["cumulative_work_replication"],
        "cumulative_work_maintenance": result["cumulative_work_maintenance"],
        "cumulative_entropy_production": result["cumulative_entropy_production"],
        "initial_catalyst_free_energy": initial_c_g,
        "declared_work_investment": declared_work,
        "material_investment": material_investment,
        "fuel_extent_per_work": (
            result["cumulative_fuel_reaction_extent"] / declared_work
            if declared_work > 0 else None
        ),
        "fuel_extent_per_material": (
            result["cumulative_fuel_reaction_extent"] / material_investment
            if material_investment > 0 else None
        ),
        "initial_catalyst_concentration": result["initial_catalyst_concentration"],
        "final_catalyst_concentration": result["final_catalyst_concentration"],
        "initial_free_energy": result["initial_free_energy"],
        "final_free_energy": result["final_free_energy"],
        "max_free_energy_balance_residual": result["max_free_energy_balance_residual"],
        "cumulative_free_energy_balance_residual": result["cumulative_free_energy_balance_residual"],
        "work_balance_residual": result["work_balance_residual"],
        "min_sigma_total": min(x["sigma_total"] for x in trajectory),
    }
    return row, result["final_state"][3:]


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/v02-standing-controls"))
    args = parser.parse_args()
    out = args.out
    (out / "figures").mkdir(parents=True, exist_ok=True)

    barriers = (8.0,)
    mutation_rates = (0.05, 0.10)
    replication_couplings = (0.5, 1.0)
    rare_standing = (1e-6, 1e-3, 1e-2, 5e-2)
    environments = ("static", "drifting")
    base = ConfigV02(duration=100.0, steps=500, rtol=1e-8, atol=1e-11)

    rows = []
    by_key = {}
    for barrier, mu, coupling, rare, environment in itertools.product(
        barriers, mutation_rates, replication_couplings, rare_standing, environments
    ):
        schedule = [(0.0, 0)] if environment == "static" else [(0.0, 0), (50.0, 3)]
        initial = (0.05, 0.05, 0.05, rare)
        cfg = ConfigV02(**{
            **base.__dict__,
            "barrier": barrier,
            "mutation_rate": mu,
            "replication_coupling": coupling,
            "initial_concentrations": initial,
        })
        meta = {
            "environment": environment,
            "barrier_kT": barrier,
            "mutation_rate": mu,
            "replication_coupling": coupling,
            "rare_genotype_initial_concentration": rare,
        }

        d_row, _ = run_one("D", cfg, schedule, meta, None)
        l_row, l_final_c = run_one("L", cfg, schedule, meta, None)
        rows.extend([d_row, l_row])

        # Match total initial catalyst material to L's final catalyst amount.
        # Mmatched is a uniform fixed library; Dmatched is a uniform faithful-
        # copying library. Moracle is a fixed library with L's final composition
        # supplied at t=0: an explicit upper-bound benchmark, not a feasible
        # uninformed baseline.
        matched_total = float(sum(l_final_c))
        uniform = tuple([matched_total / cfg.genotype_count] * cfg.genotype_count)
        cfg_uniform = ConfigV02(**{
            **cfg.__dict__,
            "initial_concentrations": uniform,
        })
        cfg_oracle = ConfigV02(**{
            **cfg.__dict__,
            "initial_concentrations": tuple(float(x) for x in l_final_c),
        })
        mm_row, _ = run_one("Mmatched", cfg_uniform, schedule, meta, matched_total)
        dm_row, _ = run_one("Dmatched", cfg_uniform, schedule, meta, matched_total)
        mo_row, _ = run_one("Moracle", cfg_oracle, schedule, meta, matched_total)
        rows.extend([mm_row, dm_row, mo_row])

        by_key[(environment, barrier, mu, coupling, rare)] = {
            "D": d_row, "L": l_row, "Mmatched": mm_row,
            "Dmatched": dm_row, "Moracle": mo_row,
        }

    contrasts = []
    for key, arms in by_key.items():
        environment, barrier, mu, coupling, rare = key
        l = arms["L"]
        row = {
            "environment": environment,
            "barrier_kT": barrier,
            "mutation_rate": mu,
            "replication_coupling": coupling,
            "rare_genotype_initial_concentration": rare,
        }
        for comparator in ("D", "Mmatched", "Dmatched", "Moracle"):
            other = arms[comparator]
            for metric in (
                "late_throughput",
                "late_throughput_per_catalyst",
                "cumulative_fuel_reaction_extent",
                "declared_work_investment",
                "material_investment",
                "fuel_extent_per_work",
                "fuel_extent_per_material",
            ):
                a, b = l[metric], other[metric]
                row[f"L_over_{comparator}_{metric}"] = a / b if b not in (None, 0) else None
        contrasts.append(row)

    write_csv(out / "replicates.csv", rows)
    write_csv(out / "matched_contrasts.csv", contrasts)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, environment in zip(axes, environments):
        for comparator in ("D", "Mmatched", "Dmatched", "Moracle"):
            subset = [
                r for r in contrasts
                if r["environment"] == environment
                and r["mutation_rate"] == 0.10
                and r["replication_coupling"] == 1.0
                and r["barrier_kT"] == 8.0
            ]
            subset.sort(key=lambda r: r["rare_genotype_initial_concentration"])
            if subset:
                ax.plot(
                    [r["rare_genotype_initial_concentration"] for r in subset],
                    [r[f"L_over_{comparator}_late_throughput"] for r in subset],
                    marker="o", label=comparator,
                )
        ax.set_xscale("log")
        ax.axhline(1.0, linewidth=1)
        ax.set_title(environment.capitalize())
        ax.set_xlabel("Initial target-genotype concentration")
    axes[0].set_ylabel("L / comparator late throughput")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(out / "figures/late_throughput_matched_controls.png", dpi=160)
    plt.close(fig)

    max_pointwise = max(r["max_free_energy_balance_residual"] for r in rows)
    max_integrated = max(abs(r["cumulative_free_energy_balance_residual"]) for r in rows)
    max_work = max(abs(r["work_balance_residual"]) for r in rows)
    min_sigma = min(r["min_sigma_total"] for r in rows)
    summary = {
        "status": "exploratory deterministic matched-standing-variation experiment",
        "runs": len(rows),
        "paired_conditions": len(contrasts),
        "arms": ["D", "L", "Mmatched", "Dmatched", "Moracle"],
        "grid": {
            "barriers_kT": barriers,
            "mutation_rates": mutation_rates,
            "replication_couplings": replication_couplings,
            "rare_standing_concentrations": rare_standing,
            "environments": environments,
            "target_switch_time": 50.0,
            "target_before": 0,
            "target_after": 3,
        },
        "matching_rule": "Mmatched and Dmatched start with uniform genotype concentrations whose sum equals L's final catalyst concentration; Moracle starts with L's final genotype composition and the same total concentration.",
        "max_pointwise_free_energy_balance_residual": max_pointwise,
        "max_integrated_free_energy_balance_residual": max_integrated,
        "max_work_pool_balance_residual": max_work,
        "minimum_observed_total_entropy_production_rate": min_sigma,
        "inference": "Deterministic parameter grid; no stochastic confidence intervals. Moracle is an oracle upper bound, not an uninformed physical baseline.",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
