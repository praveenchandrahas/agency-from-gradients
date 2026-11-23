#!/usr/bin/env python3
"""Deterministic parameter-grid pilot for the v0.2 coupled replicator model."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path

import matplotlib.pyplot as plt

from ega.model_v02 import ConfigV02, simulate_v02


def run_one(arm, cfg, schedule, metadata):
    result = simulate_v02(arm, cfg, target_schedule=schedule)
    trajectory = result.pop("trajectory")
    row = {
        **metadata,
        "arm": arm,
        "late_throughput": result["late_throughput"],
        "late_entropy_production": result["late_entropy_production"],
        "cumulative_fuel_reaction_extent": result["cumulative_fuel_reaction_extent"],
        "cumulative_replication_net_extent": result["cumulative_replication_net_extent"],
        "cumulative_replication_forward_extent": result["cumulative_replication_forward_extent"],
        "cumulative_replication_reverse_extent": result["cumulative_replication_reverse_extent"],
        "cumulative_maintenance_extent": result["cumulative_maintenance_extent"],
        "cumulative_entropy_production": result["cumulative_entropy_production"],
        "cumulative_fuel_free_energy": result["cumulative_fuel_free_energy"],
        "cumulative_work_generation": result["cumulative_work_generation"],
        "cumulative_work_replication": result["cumulative_work_replication"],
        "cumulative_work_maintenance": result["cumulative_work_maintenance"],
        "cumulative_reservoir_free_energy_input": result["cumulative_reservoir_free_energy_input"],
        "work_pool_free_energy_change": result["work_pool_free_energy_change"],
        "work_balance_residual": result["work_balance_residual"],
        "cumulative_free_energy_balance_residual": result["cumulative_free_energy_balance_residual"],
        "max_free_energy_balance_residual": result["max_free_energy_balance_residual"],
        "initial_catalyst_concentration": result["initial_catalyst_concentration"],
        "final_catalyst_concentration": result["final_catalyst_concentration"],
        "initial_free_energy": result["initial_free_energy"],
        "final_free_energy": result["final_free_energy"],
        "min_sigma_total": min(x["sigma_total"] for x in trajectory),
        "min_fuel": min(x["fuel"] for x in trajectory),
        "min_atp": min(x["atp"] for x in trajectory),
        "min_monomer": min(x["monomer"] for x in trajectory),
    }
    return row


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/v02-pilot"))
    args = parser.parse_args()
    out = args.out
    (out / "figures").mkdir(parents=True, exist_ok=True)

    barriers = (4.0, 8.0, 12.0)
    mutation_rates = (0.01, 0.05, 0.10)
    replication_couplings = (0.0, 0.5, 1.0)
    rare_standing = (1e-6, 1e-3)
    environments = ("static", "drifting")
    arms = ("D", "L")

    base = ConfigV02(duration=100.0, steps=500, rtol=1e-8, atol=1e-11)
    rows = []
    lookup = {}
    control_rows = []

    for barrier, mu, coupling, rare, environment in itertools.product(
        barriers, mutation_rates, replication_couplings, rare_standing, environments
    ):
        schedule = [(0.0, 0)] if environment == "static" else [(0.0, 0), (50.0, 3)]
        initial = (0.05, 0.05, 0.05, rare)
        cfg = ConfigV02(
            **{
                **base.__dict__,
                "barrier": barrier,
                "mutation_rate": mu,
                "replication_coupling": coupling,
                "initial_concentrations": initial,
            }
        )
        meta = {
            "environment": environment,
            "barrier_kT": barrier,
            "mutation_rate": mu,
            "replication_coupling": coupling,
            "rare_genotype_initial_concentration": rare,
        }
        for arm in arms:
            row = run_one(arm, cfg, schedule, meta)
            rows.append(row)
            lookup[(environment, barrier, mu, coupling, rare, arm)] = row

    # Passive and fixed-library controls are independent of mutation and
    # replication-coupling settings, so run them once per barrier/environment/
    # initial-library condition rather than duplicating identical trajectories.
    for barrier, rare, environment in itertools.product(barriers, rare_standing, environments):
        schedule = [(0.0, 0)] if environment == "static" else [(0.0, 0), (50.0, 3)]
        cfg = ConfigV02(
            **{
                **base.__dict__,
                "barrier": barrier,
                "initial_concentrations": (0.05, 0.05, 0.05, rare),
            }
        )
        meta = {
            "environment": environment,
            "barrier_kT": barrier,
            "mutation_rate": 0.0,
            "replication_coupling": 0.0,
            "rare_genotype_initial_concentration": rare,
        }
        for arm in ("N", "M"):
            row = run_one(arm, cfg, schedule, meta)
            control_rows.append(row)

    contrasts = []
    for barrier, mu, coupling, rare, environment in itertools.product(
        barriers, mutation_rates, replication_couplings, rare_standing, environments
    ):
        d = lookup[(environment, barrier, mu, coupling, rare, "D")]
        l = lookup[(environment, barrier, mu, coupling, rare, "L")]
        row = {
            "environment": environment,
            "barrier_kT": barrier,
            "mutation_rate": mu,
            "replication_coupling": coupling,
            "rare_genotype_initial_concentration": rare,
        }
        for metric in (
            "late_throughput",
            "late_entropy_production",
            "cumulative_fuel_reaction_extent",
            "cumulative_replication_net_extent",
            "cumulative_work_generation",
            "cumulative_work_replication",
            "final_catalyst_concentration",
        ):
            row[f"L_minus_D_{metric}"] = l[metric] - d[metric]
            row[f"L_over_D_{metric}"] = (
                l[metric] / d[metric] if abs(d[metric]) > 1e-30 else None
            )
        contrasts.append(row)

    write_csv(out / "replicates.csv", rows + control_rows)
    write_csv(out / "paired_contrasts.csv", contrasts)

    # Plot representative contrasts at the baseline rare standing-variation level.
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, environment in zip(axes, ("static", "drifting")):
        for coupling in replication_couplings:
            subset = [
                r for r in contrasts
                if r["environment"] == environment
                and r["barrier_kT"] == 8.0
                and r["mutation_rate"] == 0.10
                and r["replication_coupling"] == coupling
                and r["rare_genotype_initial_concentration"] == 1e-6
            ]
            subset.sort(key=lambda x: x["replication_coupling"])
            ax.plot(
                [r["replication_coupling"] for r in subset],
                [r["L_minus_D_late_throughput"] for r in subset],
                marker="o",
                label=f"coupling={coupling:g}",
            )
        ax.axhline(0.0, linewidth=1)
        ax.set_title(environment.capitalize())
        ax.set_xlabel("Replication coupling")
    axes[0].set_ylabel("L − D late fuel-conversion throughput")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(out / "figures/l_minus_d_coupling.png", dpi=160)
    plt.close(fig)

    max_diff_resid = max(
        abs(r["cumulative_free_energy_balance_residual"]) for r in rows + control_rows
    )
    max_work_resid = max(abs(r["work_balance_residual"]) for r in rows + control_rows)
    min_sigma = min(r["min_sigma_total"] for r in rows + control_rows)
    summary = {
        "status": "exploratory deterministic parameter-grid pilot",
        "runs": len(rows) + len(control_rows),
        "paired_D_L_conditions": len(contrasts),
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
        "max_integrated_free_energy_balance_residual": max_diff_resid,
        "max_work_pool_balance_residual": max_work_resid,
        "minimum_observed_total_entropy_production_rate": min_sigma,
        "inference": "No stochastic confidence intervals: this is a deterministic parameter sensitivity grid, not a replicated statistical experiment.",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    manifest = {
        "model": "ega.model_v02",
        "seed_policy": "deterministic ODE; no random seeds",
        "notes": [
            "The same initial genotype concentrations are used for D and L within each paired condition.",
            "L uses a symmetric bit-flip mutation kernel; D uses faithful inheritance.",
            "The initial rare genotype is standing variation in both arms.",
            "The same genotype-dependent catalytic factor affects energy conversion and replication, scaled by replication_coupling.",
            "Mutation has no extra proofreading/repair cost in this prototype.",
            "The work currency and monomer/polymer pools are explicitly tracked.",
            "All results are exploratory and conditional on the declared reaction network.",
        ],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
