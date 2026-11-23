"""Minimal open-reactor model for evolutionary access to catalytic gradients.

This is an explicit toy model, not a chemically validated prebiotic system.
Reaction rates obey local detailed balance; selection acts on net energy
available for reproduction after declared maintenance costs. Entropy production
is measured independently and never enters the fitness function.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

import numpy as np

ARMS = ("N", "M", "D", "L", "U", "A")


@dataclass(frozen=True)
class Config:
    barriers: tuple[float, ...] = (0.0, 4.0, 8.0, 12.0)
    drift_rate: float = 0.0
    locks: int = 1
    key_bits: int = 8
    initial_catalysts: int = 80
    max_catalysts: int = 500
    residence_time: float = 1.0
    fuel_feed: float = 1.0
    fuel_outflow: float = 0.35
    delta_mu: float = 6.0
    k0: float = 0.08
    catalytic_gain: float = 35.0
    mismatch_scale: float = 1.5
    mutation_rate: float = 0.025
    reproduction_cost: float = 0.025
    maintenance_cost: float = 0.0015
    energy_storage_efficiency: float = 0.25
    steps: int = 1200
    seed: int = 1
    landscape: str = "smooth"  # smooth | rugged
    adaptive_budget: float = 0.02

    def validate(self) -> None:
        if not self.barriers or any(b < 0 for b in self.barriers):
            raise ValueError("barriers must be a non-empty tuple of non-negative values")
        if self.locks < 1 or self.key_bits < 2 or self.initial_catalysts < 1:
            raise ValueError("locks, key_bits and initial_catalysts must be positive")
        if self.steps < 1 or self.max_catalysts < self.initial_catalysts:
            raise ValueError("invalid simulation horizon or population cap")
        if not 0 <= self.mutation_rate <= 1 or not 0 <= self.drift_rate <= 1:
            raise ValueError("mutation_rate and drift_rate must lie in [0, 1]")
        if self.landscape not in ("smooth", "rugged"):
            raise ValueError("landscape must be 'smooth' or 'rugged'")


def _targets(rng: np.random.Generator, locks: int, bits: int) -> np.ndarray:
    return rng.integers(0, 2, size=(locks, bits), dtype=np.int8)


def _fitness(keys: np.ndarray, targets: np.ndarray, cfg: Config) -> np.ndarray:
    """Catalytic multiplier for each genotype/lock; no effect on equilibrium."""
    distances = np.count_nonzero(keys[:, None, :] != targets[None, :, :], axis=2)
    if cfg.landscape == "smooth":
        match = np.exp(-distances / cfg.mismatch_scale)
    else:
        # Rugged but deterministic genotype-phenotype map. Exact matches remain best.
        match = np.exp(-distances / cfg.mismatch_scale) * (
            0.65 + 0.35 * ((distances * 7 + np.sum(keys, axis=1)[:, None]) % 3) / 2
        )
    return 1.0 + cfg.catalytic_gain * match


def _reaction_step(fuel: float, catalysts: np.ndarray, targets: np.ndarray,
                   barriers: np.ndarray, cfg: Config) -> tuple[float, np.ndarray, float, float]:
    """One flow-reactor step; forward/reverse catalysis share the same multiplier."""
    nlocks = len(barriers)
    if catalysts.size:
        multipliers = _fitness(catalysts, targets, cfg).mean(axis=0)
    else:
        multipliers = np.ones(nlocks)
    # At B=0 the uncatalysed route is intentionally fast; high B suppresses it.
    catalytic_rate = cfg.k0 * np.exp(-barriers) * multipliers
    uncatalysed_rate = cfg.k0 * np.exp(-barriers)
    rate = np.maximum(uncatalysed_rate, catalytic_rate)
    # Dimensionless affinity A = Δμ/kT. Reverse/forward ratio at equilibrium is exp(-A).
    forward = rate * max(fuel, 0.0)
    reverse = rate * math.exp(-cfg.delta_mu) * max(1.0 - fuel, 0.0)
    net = forward - reverse
    flux = np.maximum(net, 0.0)
    spent = float(np.sum(flux))
    # Fuel reservoir replenishment and washout.
    fuel_next = float(np.clip(fuel + cfg.fuel_feed / cfg.steps
                              - cfg.fuel_outflow * fuel / cfg.steps
                              - spent / cfg.steps, 0.0, 1.0))
    # Reaction entropy production J * affinity; reservoir exchange is a distinct
    # non-negative idealized feed/outflow term in this coarse model.
    eps = 1e-12
    reaction_sigma = float(np.sum(net * np.log(np.maximum(forward, eps) /
                                                np.maximum(reverse, eps))))
    exchange_sigma = float(max(cfg.fuel_feed * (1.0 - fuel), 0.0)
                           + max(cfg.fuel_outflow * fuel, 0.0))
    return fuel_next, flux, max(reaction_sigma, 0.0), exchange_sigma


def _mutate(keys: np.ndarray, rate: float, rng: np.random.Generator) -> np.ndarray:
    out = keys.copy()
    mask = rng.random(out.shape) < rate
    out[mask] = 1 - out[mask]
    return out


def simulate(arm: str, cfg: Config) -> dict[str, Any]:
    """Simulate one arm. L/D share the same seeded starting key library by seed."""
    cfg.validate()
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}")
    rng = np.random.default_rng(cfg.seed)
    target_rng = np.random.default_rng(cfg.seed + 900_001)
    targets = _targets(target_rng, cfg.locks, cfg.key_bits)
    keys = rng.integers(0, 2, size=(cfg.initial_catalysts, cfg.key_bits), dtype=np.int8)
    if arm == "U":
        keys[:] = targets[0]
    if arm in ("N", "M"):
        population = np.empty((0, cfg.key_bits), dtype=np.int8) if arm == "N" else keys.copy()
    else:
        population = keys.copy()

    barriers = np.resize(np.asarray(cfg.barriers, dtype=float), cfg.locks)
    fuel = 1.0
    cumulative_sigma = cumulative_reaction = cumulative_exchange = 0.0
    cumulative_spent = 0.0
    stored_energy = 0.0
    extinct_at: int | None = None
    rows: list[dict[str, float]] = []
    target_changes = 0

    for step in range(cfg.steps):
        if cfg.drift_rate and step > 0 and rng.random() < cfg.drift_rate:
            lock = int(rng.integers(0, cfg.locks))
            bit = int(rng.integers(0, cfg.key_bits))
            targets[lock, bit] = 1 - targets[lock, bit]
            target_changes += 1

        fuel, fluxes, sigma_rxn, sigma_mix = _reaction_step(
            fuel, population, targets, barriers, cfg
        )
        sigma = sigma_rxn + sigma_mix
        cumulative_reaction += sigma_rxn
        cumulative_exchange += sigma_mix
        cumulative_sigma += sigma
        throughput = float(np.sum(fluxes))
        cumulative_spent += throughput

        # Stored energy is tracked separately and is not counted as dissipated.
        stored_energy += cfg.energy_storage_efficiency * throughput
        available = max(throughput * (1.0 - cfg.energy_storage_efficiency)
                        - cfg.maintenance_cost * len(population), 0.0)

        if arm in ("D", "L") and len(population):
            # Reproduction is driven by usable chemical free energy, not entropy.
            expected_births = available / max(cfg.reproduction_cost, 1e-12)
            births = min(int(expected_births), max(0, cfg.max_catalysts - len(population)))
            if births > 0:
                parent_idx = rng.integers(0, len(population), size=births)
                offspring = population[parent_idx].copy()
                if arm == "L":
                    offspring = _mutate(offspring, cfg.mutation_rate, rng)
                population = np.concatenate((population, offspring), axis=0)
            # Density-dependent washout limits unchecked exponential growth.
            if len(population) > cfg.initial_catalysts:
                excess = len(population) - cfg.initial_catalysts
                deaths = min(excess, max(0, int(0.015 * excess)))
                if deaths:
                    keep = rng.choice(len(population), len(population) - deaths, replace=False)
                    population = population[keep]
        elif arm == "A" and len(population):
            # Non-replicating adaptive search: replace a small fraction with random
            # candidates; charge the declared search budget from usable energy.
            trials = max(1, int(cfg.adaptive_budget * len(population)))
            candidate = rng.integers(0, 2, size=(trials, cfg.key_bits), dtype=np.int8)
            current_score = _fitness(population, targets, cfg).sum(axis=1)
            cand_score = _fitness(candidate, targets, cfg).sum(axis=1)
            for j in range(trials):
                worst = int(np.argmin(current_score))
                if cand_score[j] > current_score[worst] and available > cfg.adaptive_budget:
                    population[worst] = candidate[j]
                    current_score[worst] = cand_score[j]
                    available -= cfg.adaptive_budget
        # M and U are fixed; D inherits without mutation; L inherits with mutation.
        if arm in ("N", "D", "L") and len(population) == 0 and extinct_at is None:
            extinct_at = step

        mean_distance = (float(np.mean(np.min(
            np.count_nonzero(population[:, None, :] != targets[None, :, :], axis=2), axis=0
        ))) if len(population) else float(cfg.key_bits))
        rows.append({
            "step": float(step), "fuel": fuel, "population": float(len(population)),
            "mean_key_distance": mean_distance, "throughput": throughput,
            "sigma_reaction": sigma_rxn, "sigma_exchange": sigma_mix,
            "sigma_total": sigma, "stored_energy": stored_energy,
        })

    tail = rows[max(0, int(0.8 * len(rows))):]
    mean_pop = float(np.mean([r["population"] for r in tail]))
    mean_sigma = float(np.mean([r["sigma_total"] for r in tail]))
    mean_access = float(np.mean([r["throughput"] for r in tail]))
    return {
        "arm": arm, "seed": cfg.seed, "config": asdict(cfg),
        "targets": targets.tolist(), "final_population": int(len(population)),
        "mean_population_late": mean_pop, "mean_sigma_late": mean_sigma,
        "mean_throughput_late": mean_access,
        "cumulative_sigma": cumulative_sigma,
        "cumulative_sigma_reaction": cumulative_reaction,
        "cumulative_sigma_exchange": cumulative_exchange,
        "cumulative_fuel_spent": cumulative_spent,
        "stored_energy_final": stored_energy,
        "extinct_at": extinct_at, "target_changes": target_changes,
        "late_key_distance": float(np.mean([r["mean_key_distance"] for r in tail])),
        "trajectory": rows,
    }
