"""Lineage-associated energy-harvesting replicator model (v0.3).

A genotype-specific reversible reaction charges a low-energy replicator into
a high-energy state. Replication consumes that high-energy state. Replication
kinetics are genotype-independent; selection can arise only through differential
energy capture. This is an abstract, thermodynamically closed toy network.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Sequence

import numpy as np
from scipy.integrate import simpson, solve_ivp


@dataclass(frozen=True)
class ConfigV03:
    barrier: float = 8.0
    key_bits: int = 2
    initial_genotype_concentrations: tuple[float, ...] = (0.05, 0.05, 0.05, 1e-6)
    initial_high_fraction: float = 0.5
    mutation_rate: float = 0.10

    fuel_feed: float = 0.99
    monomer_feed: float = 0.50
    q_fuel: float = 0.35
    q_monomer: float = 0.20

    mu_fuel_std: float = 12.0
    mu_waste_std: float = 0.0
    mu_low_std: float = 7.0
    mu_high_std: float = 13.0
    mu_monomer_std: float = 0.0
    mu_polymer_std: float = 0.0

    k0: float = 0.8
    k_replication: float = 1e-3
    k_maintenance: float = 1e-4
    catalytic_gain: float = 35.0
    mismatch_scale: float = 1.5

    duration: float = 100.0
    steps: int = 1000
    rtol: float = 1e-8
    atol: float = 1e-11

    @property
    def genotype_count(self) -> int:
        return 2 ** self.key_bits

    @property
    def delta_mu1(self) -> float:
        return self.mu_fuel_std + self.mu_low_std - self.mu_waste_std - self.mu_high_std

    @property
    def delta_mu2(self) -> float:
        return self.mu_high_std + self.mu_monomer_std - 2 * self.mu_low_std - self.mu_polymer_std

    @property
    def delta_mu3(self) -> float:
        return self.mu_high_std - self.mu_low_std

    def validate(self) -> None:
        if self.barrier < 0 or self.key_bits < 1 or self.key_bits > 6:
            raise ValueError("barrier must be non-negative and key_bits must lie in [1, 6]")
        if len(self.initial_genotype_concentrations) != self.genotype_count:
            raise ValueError("initial_genotype_concentrations must have length 2**key_bits")
        if any((not math.isfinite(x)) or x <= 0 for x in self.initial_genotype_concentrations):
            raise ValueError("all initial genotype concentrations must be finite and positive")
        if not 0 < self.initial_high_fraction < 1:
            raise ValueError("initial_high_fraction must lie strictly between 0 and 1")
        if not 0 <= self.mutation_rate <= 0.5:
            raise ValueError("mutation_rate must lie in [0, 0.5]")
        if not 0 < self.fuel_feed < 1 or not 0 < self.monomer_feed < 1:
            raise ValueError("feed activities must lie strictly between 0 and 1")
        if min(self.q_fuel, self.q_monomer, self.k0, self.k_replication,
               self.k_maintenance, self.catalytic_gain, self.mismatch_scale) <= 0:
            raise ValueError("flow rates, kinetic constants, gain and mismatch scale must be positive")
        if self.duration <= 0 or self.steps < 2 or self.rtol <= 0 or self.atol <= 0:
            raise ValueError("invalid integration horizon or tolerances")
        if not all(math.isfinite(x) for x in (
            self.mu_fuel_std, self.mu_waste_std, self.mu_low_std,
            self.mu_high_std, self.mu_monomer_std, self.mu_polymer_std
        )):
            raise ValueError("standard chemical potentials must be finite")


def genotype_keys(key_bits: int) -> np.ndarray:
    n = 2 ** key_bits
    return np.asarray([[(i >> b) & 1 for b in range(key_bits)] for i in range(n)],
                      dtype=np.int8)


def mutation_kernel(key_bits: int, mutation_rate: float) -> np.ndarray:
    keys = genotype_keys(key_bits)
    distances = np.count_nonzero(keys[:, None, :] != keys[None, :, :], axis=2)
    kernel = mutation_rate ** distances * (1.0 - mutation_rate) ** (key_bits - distances)
    kernel /= kernel.sum(axis=1, keepdims=True)
    return kernel


def _safe_log(x: np.ndarray | float) -> np.ndarray | float:
    return np.log(np.maximum(x, 1e-300))


def evaluate_state(
    state: Sequence[float],
    cfg: ConfigV03,
    target: int,
    kernel: np.ndarray,
    replication: bool,
    arm: str,
) -> tuple[np.ndarray, dict[str, Any]]:
    y = np.asarray(state, dtype=float)
    n = cfg.genotype_count
    f, monomer = float(y[0]), float(y[1])
    waste, polymer = 1.0 - f, 1.0 - monomer
    low = y[2:2 + n]
    high = y[2 + n:2 + 2 * n]

    keys = genotype_keys(cfg.key_bits)
    target_key = keys[target]
    distances = np.count_nonzero(keys != target_key[None, :], axis=1)
    match = np.exp(-distances / cfg.mismatch_scale)
    alpha = 1.0 + cfg.catalytic_gain * match
    if arm == "N":
        alpha = np.ones(n, dtype=float)
    leverage = 1.0 - math.exp(-cfg.barrier)
    # Genotype match affects energy capture only. It never enters k_replication.
    k1 = cfg.k0 * math.exp(-cfg.barrier) * (
        1.0 + leverage * (alpha - 1.0)
    )

    j1 = k1 * (
        f * low - math.exp(-cfg.delta_mu1) * waste * high
    )
    if replication:
        j2 = cfg.k_replication * kernel * (
            high[:, None] * monomer
            - math.exp(-cfg.delta_mu2) * polymer * low[:, None] * low[None, :]
        )
    else:
        j2 = np.zeros((n, n), dtype=float)
    j3 = cfg.k_maintenance * (
        high - math.exp(-cfg.delta_mu3) * low
    )

    parent_births = j2.sum(axis=1)
    offspring_births = j2.sum(axis=0)

    dy = np.zeros_like(y)
    dy[0] = cfg.q_fuel * (cfg.fuel_feed - f) - float(j1.sum())
    dy[1] = cfg.q_monomer * (cfg.monomer_feed - monomer) - float(j2.sum())
    dy[2:2 + n] = -j1 + j3 + parent_births + offspring_births
    dy[2 + n:2 + 2 * n] = j1 - j3 - parent_births

    a1 = (
        cfg.delta_mu1 + _safe_log(f) + _safe_log(low)
        - _safe_log(waste) - _safe_log(high)
    )
    a2 = (
        cfg.delta_mu2 + _safe_log(high[:, None]) + _safe_log(monomer)
        - _safe_log(polymer) - _safe_log(low[:, None])
        - _safe_log(low[None, :])
    )
    a3 = cfg.delta_mu3 + _safe_log(high) - _safe_log(low)

    sigma1 = float(np.sum(j1 * a1))
    sigma2 = float(np.sum(j2 * a2)) if replication else 0.0
    sigma3 = float(np.sum(j3 * a3))

    f0, w0 = cfg.fuel_feed, 1.0 - cfg.fuel_feed
    m0, p0 = cfg.monomer_feed, 1.0 - cfg.monomer_feed
    sigma_fuel_flow = cfg.q_fuel * (
        (f0 - f) * math.log(f0 / max(f, 1e-300))
        + (w0 - waste) * math.log(w0 / max(waste, 1e-300))
    )
    sigma_monomer_flow = cfg.q_monomer * (
        (m0 - monomer) * math.log(m0 / max(monomer, 1e-300))
        + (p0 - polymer) * math.log(p0 / max(polymer, 1e-300))
    )
    sigma_flow = float(sigma_fuel_flow + sigma_monomer_flow)
    sigma_total = sigma1 + sigma2 + sigma3 + sigma_flow

    reservoir_input = (
        cfg.q_fuel * (
            (f0 - f) * (cfg.mu_fuel_std + math.log(f0))
            + (w0 - waste) * (cfg.mu_waste_std + math.log(w0))
        )
        + cfg.q_monomer * (
            (m0 - monomer) * (cfg.mu_monomer_std + math.log(m0))
            + (p0 - polymer) * (cfg.mu_polymer_std + math.log(p0))
        )
    )

    return dy, {
        "j1": j1,
        "j2": j2,
        "j3": j3,
        "alpha": alpha,
        "k1": k1,
        "sigma1": sigma1,
        "sigma2": sigma2,
        "sigma3": sigma3,
        "sigma_flow": sigma_flow,
        "sigma_total": sigma_total,
        "reservoir_free_energy_input_rate": float(reservoir_input),
    }


def free_energy_density(state: Sequence[float], cfg: ConfigV03) -> float:
    y = np.asarray(state, dtype=float)
    n = cfg.genotype_count
    f, monomer = float(y[0]), float(y[1])
    waste, polymer = 1.0 - f, 1.0 - monomer
    low = y[2:2 + n]
    high = y[2 + n:2 + 2 * n]
    species = [
        (f, cfg.mu_fuel_std), (waste, cfg.mu_waste_std),
        (monomer, cfg.mu_monomer_std), (polymer, cfg.mu_polymer_std),
    ]
    species.extend((float(x), cfg.mu_low_std) for x in low)
    species.extend((float(x), cfg.mu_high_std) for x in high)
    return float(sum(x * (mu + math.log(x) - 1.0) for x, mu in species if x > 0))


def free_energy_balance(
    state: Sequence[float], cfg: ConfigV03, target: int,
    kernel: np.ndarray, replication: bool, arm: str,
) -> tuple[float, float, float, float]:
    dy, diag = evaluate_state(state, cfg, target, kernel, replication, arm)
    y = np.asarray(state, dtype=float)
    n = cfg.genotype_count
    f, monomer = float(y[0]), float(y[1])
    waste, polymer = 1.0 - f, 1.0 - monomer
    low = y[2:2 + n]
    high = y[2 + n:2 + 2 * n]
    gradient = [
        cfg.mu_fuel_std + math.log(f) - cfg.mu_waste_std - math.log(waste),
        cfg.mu_monomer_std + math.log(monomer) - cfg.mu_polymer_std - math.log(polymer),
    ]
    gradient.extend(cfg.mu_low_std + math.log(x) for x in low)
    gradient.extend(cfg.mu_high_std + math.log(x) for x in high)
    d_g = float(np.dot(np.asarray(gradient), dy))
    ext = diag["reservoir_free_energy_input_rate"]
    sigma = diag["sigma_total"]
    return float(ext - d_g - sigma), float(ext), d_g, float(sigma)


def simulate_v03(
    arm: str,
    cfg: ConfigV03 = ConfigV03(),
    target_schedule: Sequence[tuple[float, int]] | None = None,
) -> dict[str, Any]:
    cfg.validate()
    if arm not in ("N", "M", "D", "L"):
        raise ValueError("v0.3 supports arms N, M, D and L")
    if target_schedule is None:
        target_schedule = ((0.0, 0),)
    schedule = [(float(t), int(target)) for t, target in target_schedule]
    if not schedule or schedule[0][0] != 0.0:
        raise ValueError("target_schedule must begin at time zero")
    if any(schedule[i][0] >= schedule[i + 1][0] for i in range(len(schedule) - 1)):
        raise ValueError("target_schedule times must be strictly increasing")
    if any(target < 0 or target >= cfg.genotype_count for _, target in schedule):
        raise ValueError("target index outside genotype space")
    if schedule[-1][0] >= cfg.duration:
        raise ValueError("target changes must occur before the simulation endpoint")

    replication = arm in ("D", "L")
    kernel = mutation_kernel(cfg.key_bits, cfg.mutation_rate) if arm == "L" else np.eye(cfg.genotype_count)
    initial_c = np.asarray(cfg.initial_genotype_concentrations, dtype=float)
    initial_low = initial_c * (1.0 - cfg.initial_high_fraction)
    initial_high = initial_c * cfg.initial_high_fraction
    initial_state = np.concatenate(([cfg.fuel_feed, cfg.monomer_feed], initial_low, initial_high))

    segment_solutions: list[tuple[np.ndarray, np.ndarray, int]] = []
    y0 = initial_state.copy()
    for idx, (start, target) in enumerate(schedule):
        stop = schedule[idx + 1][0] if idx + 1 < len(schedule) else cfg.duration
        points = max(2, int(round((stop - start) / cfg.duration * cfg.steps)) + 1)
        t_eval = np.linspace(start, stop, points)
        sol = solve_ivp(
            lambda t, y: evaluate_state(y, cfg, target, kernel, replication, arm)[0],
            (start, stop), y0, method="BDF", t_eval=t_eval,
            rtol=cfg.rtol, atol=cfg.atol, max_step=cfg.duration / cfg.steps,
        )
        if not sol.success:
            raise RuntimeError(f"v0.3 integration failed: {sol.message}")
        if np.min(sol.y[:2]) < -1e-10 or np.min(sol.y[2:]) < -1e-10:
            raise RuntimeError("v0.3 integration left the non-negative state domain")
        if np.max(sol.y[0]) > 1 + 1e-10 or np.max(sol.y[1]) > 1 + 1e-10:
            raise RuntimeError("v0.3 integration exceeded a normalized pool boundary")
        segment_solutions.append((sol.t.copy(), sol.y.copy(), target))
        y0 = sol.y[:, -1].copy()

    time_parts, state_parts, target_parts = [], [], []
    for idx, (segment_times, segment_states, target) in enumerate(segment_solutions):
        time_parts.append(segment_times if idx == 0 else segment_times[1:])
        state_parts.append(segment_states if idx == 0 else segment_states[:, 1:])
        target_parts.append(np.full(len(segment_times) if idx == 0 else len(segment_times) - 1,
                                   target, dtype=int))
    times = np.concatenate(time_parts)
    states = np.concatenate(state_parts, axis=1)
    targets = np.concatenate(target_parts)

    trajectory: list[dict[str, float]] = []
    pointwise_residuals = []
    for k, time in enumerate(times):
        state = states[:, k]
        target = int(targets[k])
        _, diag = evaluate_state(state, cfg, target, kernel, replication, arm)
        residual, _, _, _ = free_energy_balance(state, cfg, target, kernel, replication, arm)
        pointwise_residuals.append(abs(residual))
        n = cfg.genotype_count
        low = state[2:2 + n]
        high = state[2 + n:2 + 2 * n]
        trajectory.append({
            "time": float(time),
            "target": float(target),
            "fuel": float(state[0]),
            "monomer": float(state[1]),
            "total_replicator": float(np.sum(low + high)),
            "fuel_throughput": float(np.sum(diag["j1"])),
            "replication_extent_rate": float(np.sum(diag["j2"])),
            "sigma1": diag["sigma1"],
            "sigma2": diag["sigma2"],
            "sigma3": diag["sigma3"],
            "sigma_flow": diag["sigma_flow"],
            "sigma_total": diag["sigma_total"],
        })

    def integral(key: str) -> float:
        total = 0.0
        for segment_times, segment_states, target in segment_solutions:
            vals = []
            for k in range(len(segment_times)):
                _, diag = evaluate_state(
                    segment_states[:, k], cfg, target, kernel, replication, arm
                )
                if key == "fuel_extent":
                    vals.append(float(np.sum(diag["j1"])))
                elif key == "replication_extent":
                    vals.append(float(np.sum(diag["j2"])))
                elif key == "sigma_total":
                    vals.append(diag["sigma_total"])
                elif key == "sigma1":
                    vals.append(diag["sigma1"])
                elif key == "sigma2":
                    vals.append(diag["sigma2"])
                elif key == "sigma3":
                    vals.append(diag["sigma3"])
                elif key == "sigma_flow":
                    vals.append(diag["sigma_flow"])
                elif key == "reservoir_input":
                    vals.append(diag["reservoir_free_energy_input_rate"])
                else:
                    raise KeyError(key)
            total += float(simpson(np.asarray(vals, dtype=float), x=segment_times))
        return total

    late = trajectory[max(0, int(0.8 * len(trajectory))):]
    final_low = states[2:2 + cfg.genotype_count, -1]
    final_high = states[2 + cfg.genotype_count:, -1]
    final_c = final_low + final_high
    initial_g = free_energy_density(initial_state, cfg)
    final_g = free_energy_density(states[:, -1], cfg)
    cumulative_sigma = integral("sigma_total")
    cumulative_reservoir = integral("reservoir_input")
    return {
        "arm": arm,
        "config": asdict(cfg),
        "target_schedule": schedule,
        "initial_state": initial_state.tolist(),
        "final_state": states[:, -1].tolist(),
        "initial_genotype_abundance": initial_c.tolist(),
        "final_genotype_abundance": final_c.tolist(),
        "final_low_energy_replicators": final_low.tolist(),
        "final_high_energy_replicators": final_high.tolist(),
        "initial_total_replicator": float(initial_c.sum()),
        "final_total_replicator": float(final_c.sum()),
        "late_throughput": float(np.mean([r["fuel_throughput"] for r in late])),
        "late_entropy_production": float(np.mean([r["sigma_total"] for r in late])),
        "cumulative_fuel_extent": integral("fuel_extent"),
        "cumulative_replication_extent": integral("replication_extent"),
        "cumulative_entropy_production": cumulative_sigma,
        "cumulative_sigma1": integral("sigma1"),
        "cumulative_sigma2": integral("sigma2"),
        "cumulative_sigma3": integral("sigma3"),
        "cumulative_sigma_flow": integral("sigma_flow"),
        "cumulative_reservoir_free_energy_input": cumulative_reservoir,
        "initial_free_energy": initial_g,
        "final_free_energy": final_g,
        "cumulative_free_energy_balance_residual": (
            cumulative_reservoir - (final_g - initial_g) - cumulative_sigma
        ),
        "max_pointwise_free_energy_balance_residual": float(max(pointwise_residuals)),
        "minimum_observed_entropy_production_rate": float(
            min(r["sigma_total"] for r in trajectory)
        ),
        "target_changes": len(schedule) - 1,
        "trajectory": trajectory,
    }
