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

ARMS = ("N", "M", "D", "L", "U", "A", "Mmatched", "Dmatched", "Amatched", "Umatched")


@dataclass(frozen=True)
class Config:
    barriers: tuple[float, ...] = (0.0, 4.0, 8.0, 12.0)
    drift_rate: float = 0.0
    locks: int = 1
    key_bits: int = 16
    initial_catalysts: int = 80
    max_catalysts: int = 500
    fuel_feed: float = 1.0
    fuel_outflow: float = 0.35
    delta_mu: float = 6.0
    k0: float = 0.08
    catalytic_gain: float = 35.0
    mismatch_scale: float = 1.5
    mutation_rate: float = 0.025
    mutation_energy_cost: float = 2.0e-9
    reproduction_cost: float = 1.0e-8
    maintenance_cost: float = 1.0e-10
    energy_storage_efficiency: float = 0.0
    steps: int = 1200
    duration: float = 100.0  # residence-time units
    seed: int = 1
    landscape: str = "smooth"  # smooth | rugged
    adaptive_budget: float = 1.0e-9
    turnover_rate: float = 0.02

    def validate(self) -> None:
        if not self.barriers or any(b < 0 for b in self.barriers):
            raise ValueError("barriers must be a non-empty tuple of non-negative values")
        if self.locks < 1 or self.key_bits < 2 or self.initial_catalysts < 1:
            raise ValueError("locks, key_bits and initial_catalysts must be positive")
        if self.steps < 1 or self.duration <= 0 or self.max_catalysts < self.initial_catalysts:
            raise ValueError("invalid simulation horizon or population cap")
        if not 0 <= self.mutation_rate <= 1 or not 0 <= self.drift_rate <= 1:
            raise ValueError("mutation_rate and drift_rate must lie in [0, 1]")
        if self.catalytic_gain <= 0 or self.mismatch_scale <= 0:
            raise ValueError("catalytic_gain and mismatch_scale must be positive")
        if self.reproduction_cost <= 0 or self.maintenance_cost < 0:
            raise ValueError("reproduction cost must be positive and maintenance non-negative")
        if self.mutation_energy_cost < 0 or self.adaptive_budget < 0 or self.turnover_rate < 0:
            raise ValueError("mutation/search costs and turnover rate must be non-negative")
        if self.fuel_feed <= 0 or self.fuel_feed > 1 or self.fuel_outflow < 0 or self.delta_mu <= 0 or self.k0 <= 0:
            raise ValueError("fuel_feed must be in (0,1], affinity/rate positive, outflow non-negative")
        if not 0 <= self.energy_storage_efficiency < 1:
            raise ValueError("energy_storage_efficiency must lie in [0, 1)")
        if self.energy_storage_efficiency != 0:
            raise ValueError("energy storage coupling is not implemented in v0.1; set it to zero")
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
                   barriers: np.ndarray, cfg: Config, dt: float | None = None
                   ) -> tuple[float, np.ndarray, float, float]:
    """One flow-reactor step; forward/reverse catalysis share the same multiplier."""
    if dt is None:
        dt = cfg.duration / cfg.steps
    nlocks = len(barriers)
    if catalysts.size:
        individual = _fitness(catalysts, targets, cfg)
        match_strength = np.mean(individual - 1.0, axis=0) / cfg.catalytic_gain
        abundance = min(len(catalysts) / cfg.initial_catalysts, 5.0)
        multipliers = 1.0 + cfg.catalytic_gain * match_strength * abundance
    else:
        multipliers = np.ones(nlocks)
    # At B=0 the uncatalysed route is intentionally fast; high B suppresses it.
    uncatalysed_rate = cfg.k0 * np.exp(-barriers)
    # At B=0 there is no kinetic lock to unlock: all catalysts collapse to
    # the same baseline rate. Catalytic leverage grows with barrier height.
    leverage = 1.0 - np.exp(-barriers)
    rate = uncatalysed_rate * (1.0 + (multipliers - 1.0) * leverage)
    # Dimensionless affinity A = Δμ/kT. Reverse/forward ratio at equilibrium is exp(-A).
    forward = rate * max(fuel, 0.0)
    reverse = rate * math.exp(-cfg.delta_mu) * max(1.0 - fuel, 0.0)
    net = forward - reverse
    flux = net
    spent = float(np.sum(net))
    # Fuel reservoir replenishment and washout.
    # A single ideal feed/outflow stream at concentration fuel_feed. The
    # exchange entropy is J_ex * (mu_feed - mu_reactor)/T, with
    # J_ex = q(c_feed-c); this is non-negative for ideal activities.
    fuel_next = float(np.clip(fuel + cfg.fuel_outflow * (cfg.fuel_feed - fuel) * dt
                              - spent * dt, 0.0, cfg.fuel_feed))
    # Reaction entropy production J * affinity; reservoir exchange is a distinct
    # non-negative idealized feed/outflow term in this coarse model.
    eps = 1e-12
    reaction_sigma = float(np.sum(net * np.log(np.maximum(forward, eps) /
                                                np.maximum(reverse, eps))))
    exchange_flux = cfg.fuel_outflow * (cfg.fuel_feed - fuel)
    exchange_sigma = float(exchange_flux * math.log(
        max(cfg.fuel_feed, eps) / max(fuel, eps)
    ))
    return fuel_next, flux, max(reaction_sigma, 0.0), exchange_sigma


def _mutate(keys: np.ndarray, rate: float, rng: np.random.Generator) -> np.ndarray:
    out = keys.copy()
    mask = rng.random(out.shape) < rate
    out[mask] = 1 - out[mask]
    return out


def simulate(arm: str, cfg: Config, fixed_population_size: int | None = None) -> dict[str, Any]:
    """Simulate one arm. L/D share the same seeded starting key library by seed."""
    cfg.validate()
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}")
    matched_arms = ("Mmatched", "Dmatched", "Amatched", "Umatched")
    if arm in matched_arms and (fixed_population_size is None or fixed_population_size < 1
                                or fixed_population_size > cfg.max_catalysts):
        raise ValueError(f"{arm} requires fixed_population_size in [1, max_catalysts]")
    if arm not in matched_arms and fixed_population_size is not None:
        raise ValueError("fixed_population_size is only valid for matched control arms")
    initial_count = fixed_population_size if arm in matched_arms else cfg.initial_catalysts
    rng = np.random.default_rng(cfg.seed)
    target_rng = np.random.default_rng(cfg.seed + 900_001)
    drift_rng = np.random.default_rng(cfg.seed + 700_003)
    targets = _targets(target_rng, cfg.locks, cfg.key_bits)
    keys = rng.integers(0, 2, size=(initial_count, cfg.key_bits), dtype=np.int8)
    if arm in ("U", "Umatched"):
        repeats = int(math.ceil(initial_count / cfg.locks))
        keys = np.tile(targets, (repeats, 1))[:initial_count].copy()
    if arm == "N":
        population = np.empty((0, cfg.key_bits), dtype=np.int8)
    else:
        population = keys.copy()

    initial_population_actual = len(population)
    barriers = np.resize(np.asarray(cfg.barriers, dtype=float), cfg.locks)
    fuel = float(cfg.fuel_feed)
    cumulative_sigma = cumulative_reaction = cumulative_exchange = 0.0
    cumulative_spent = 0.0
    initial_fuel = fuel
    cumulative_feed_exchange = 0.0
    stored_energy = 0.0
    cumulative_reproduction_energy = 0.0
    cumulative_maintenance_energy = 0.0
    cumulative_adaptive_cost = 0.0
    cumulative_mutation_energy = 0.0
    initial_construction_energy = initial_population_actual * cfg.reproduction_cost
    extinct_at: int | None = None
    rows: list[dict[str, float]] = []
    target_changes = 0
    drift_events: list[tuple[int, int, int]] = []

    for step in range(cfg.steps):
        dt = cfg.duration / cfg.steps
        drift_probability = 1.0 - math.exp(-cfg.drift_rate * dt)
        if cfg.drift_rate and step > 0 and drift_rng.random() < drift_probability:
            lock = int(drift_rng.integers(0, cfg.locks))
            bit = int(drift_rng.integers(0, cfg.key_bits))
            targets[lock, bit] = 1 - targets[lock, bit]
            target_changes += 1
            drift_events.append((step, lock, bit))

        fuel_before = fuel
        fuel, fluxes, sigma_rxn, sigma_mix = _reaction_step(
            fuel, population, targets, barriers, cfg, dt
        )
        sigma = sigma_rxn + sigma_mix
        cumulative_feed_exchange += cfg.fuel_outflow * (cfg.fuel_feed - fuel_before) * dt
        cumulative_reaction += sigma_rxn * dt
        cumulative_exchange += sigma_mix * dt
        cumulative_sigma += sigma * dt
        throughput = float(np.sum(fluxes))
        cumulative_spent += throughput * dt

        # Reaction extent times affinity is the model's free-energy release.
        # Storage, maintenance and reproduction are separate ledger entries.
        released_energy = throughput * cfg.delta_mu
        stored_energy += cfg.energy_storage_efficiency * released_energy * dt
        maintenance_this_step = cfg.maintenance_cost * len(population) * dt
        cumulative_maintenance_energy += maintenance_this_step
        available = max((released_energy * (1.0 - cfg.energy_storage_efficiency)
                         - cfg.maintenance_cost * len(population)) * dt, 0.0)

        if arm in ("D", "L", "Dmatched") and len(population):
            # Reproduction is driven by usable chemical free energy, not entropy.
            expected_mutation_cost = (cfg.key_bits * cfg.mutation_rate *
                                      cfg.mutation_energy_cost) if arm == "L" else 0.0
            effective_birth_cost = cfg.reproduction_cost + expected_mutation_cost
            expected_births = available / max(effective_birth_cost, 1e-12)
            births = min(int(expected_births), max(0, cfg.max_catalysts - len(population)))
            if births > 0:
                # Differential reproduction is based on catalytic contribution
                # to usable chemical throughput, never on entropy production.
                reproductive_weights = np.mean(_fitness(population, targets, cfg), axis=1)
                reproductive_weights = reproductive_weights / reproductive_weights.sum()
                parent_idx = rng.choice(len(population), size=births, p=reproductive_weights)
                offspring = population[parent_idx].copy()
                if arm == "L":
                    mutated = _mutate(offspring, cfg.mutation_rate, rng)
                    mutation_count = int(np.count_nonzero(mutated != offspring))
                    mutation_cost = mutation_count * cfg.mutation_energy_cost
                    cumulative_mutation_energy += mutation_cost
                    offspring = mutated
                population = np.concatenate((population, offspring), axis=0)
            # Turnover is a declared per-residence-time loss process. If usable
            # free energy cannot replace losses, the lineage can decline/extinguish.
            death_probability = 1.0 - math.exp(-cfg.turnover_rate * dt)
            deaths = int(rng.binomial(len(population), death_probability))
            if deaths:
                keep = rng.choice(len(population), len(population) - deaths, replace=False)
                population = population[keep]
        elif arm in ("A", "Amatched") and len(population):
            # Non-replicating adaptive search: replace a small fraction with random
            # candidates; charge the declared search budget from usable energy.
            trials = max(1, int(0.05 * len(population)))
            current_score = _fitness(population, targets, cfg).sum(axis=1)
            for _ in range(trials):
                # Pay for each candidate evaluation before generating/scoring it.
                if available <= cfg.adaptive_budget:
                    break
                available -= cfg.adaptive_budget
                cumulative_adaptive_cost += cfg.adaptive_budget
                candidate = rng.integers(0, 2, size=(1, cfg.key_bits), dtype=np.int8)
                cand_score = float(_fitness(candidate, targets, cfg).sum())
                worst = int(np.argmin(current_score))
                if cand_score > current_score[worst]:
                    population[worst] = candidate[0]
                    current_score[worst] = cand_score
        # M and U are fixed; D inherits without mutation; L inherits with mutation.
        if arm in ("D", "L", "Dmatched") and len(population) == 0 and extinct_at is None:
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
        "targets": targets.tolist(), "initial_population": int(initial_population_actual),
        "final_population": int(len(population)),
        "mean_population_late": mean_pop, "mean_sigma_late": mean_sigma,
        "mean_throughput_late": mean_access,
        "cumulative_sigma": cumulative_sigma,
        "cumulative_sigma_reaction": cumulative_reaction,
        "cumulative_sigma_exchange": cumulative_exchange,
        "cumulative_fuel_spent": cumulative_spent,
        "cumulative_feed_exchange": cumulative_feed_exchange,
        "fuel_balance_residual": fuel - initial_fuel - cumulative_feed_exchange + cumulative_spent,
        "stored_energy_final": stored_energy,
        "initial_construction_energy": initial_construction_energy,
        "cumulative_reproduction_energy": cumulative_reproduction_energy,
        "cumulative_maintenance_energy": cumulative_maintenance_energy,
        "cumulative_adaptive_cost": cumulative_adaptive_cost,
        "cumulative_mutation_energy": cumulative_mutation_energy,
        "extinct_at": extinct_at, "target_changes": target_changes,
        "drift_events": drift_events,
        "late_key_distance": float(np.mean([r["mean_key_distance"] for r in tail])),
        "trajectory": rows,
    }
