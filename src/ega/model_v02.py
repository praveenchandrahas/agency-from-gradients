"""Thermodynamically coupled minimal autocatalytic replicator model (v0.2).

Species pools:
    F + D <-> W + T        fuel conversion / work-currency synthesis
    C_i + M + T <-> C_i + C_j + P + D
                             genotype-specific autocatalytic replication
    T <-> D                 generic maintenance / ATP hydrolysis

Catalysts multiply forward and reverse rates equally. Replication consumes the
same T pool produced by the fuel-conversion reaction. All reaction affinities
are derived from one set of standard chemical potentials. The declared
isothermal CSTR boundary includes fuel/waste and monomer/polymer exchange.
This is still an abstract reaction network, not validated prebiotic chemistry.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Sequence

import numpy as np
from scipy.integrate import simpson, solve_ivp


@dataclass(frozen=True)
class ConfigV02:
    key_bits: int = 2
    barrier: float = 8.0
    gain: float = 35.0
    mismatch_scale: float = 1.5
    replication_coupling: float = 1.0
    mutation_rate: float = 0.10

    # Standard chemical potentials, in kBT units.
    mu_fuel_std: float = 12.0
    mu_waste_std: float = 0.0
    mu_atp_std: float = 6.0
    mu_adp_std: float = 0.0
    mu_monomer_std: float = 0.0
    mu_polymer_std: float = 0.0
    mu_catalyst_std: float = 7.0

    # Kinetic and flow parameters.
    k0: float = 0.8
    krep: float = 0.001
    kmaint: float = 0.0001
    q_fuel: float = 0.35
    fuel_feed: float = 0.99
    q_monomer: float = 0.20
    monomer_feed: float = 0.50
    monomers_per_catalyst: int = 1
    atp_per_birth: int = 1

    duration: float = 100.0
    steps: int = 1000
    rtol: float = 1e-8
    atol: float = 1e-12
    initial_concentrations: tuple[float, ...] = (0.05, 0.05, 0.05, 1e-6)

    @property
    def genotype_count(self) -> int:
        return 2 ** self.key_bits

    @property
    def mu1(self) -> float:
        # F + D -> W + T
        return self.mu_fuel_std + self.mu_adp_std - self.mu_waste_std - self.mu_atp_std

    @property
    def mu2(self) -> float:
        # C_i + mM + nT -> C_i + C_j + mP + nD
        return (
            self.monomers_per_catalyst * (self.mu_monomer_std - self.mu_polymer_std)
            + self.atp_per_birth * (self.mu_atp_std - self.mu_adp_std)
            - self.mu_catalyst_std
        )

    @property
    def mu3(self) -> float:
        # T -> D
        return self.mu_atp_std - self.mu_adp_std

    def validate(self) -> None:
        if self.key_bits < 1 or self.key_bits > 6:
            raise ValueError("key_bits must lie in [1, 6] for the dense genotype model")
        if len(self.initial_concentrations) != self.genotype_count:
            raise ValueError("initial_concentrations must contain one value per genotype")
        if any(x <= 0 for x in self.initial_concentrations):
            raise ValueError("all initial genotype concentrations must be positive")
        if self.barrier < 0 or self.gain < 0 or self.mismatch_scale <= 0:
            raise ValueError("invalid barrier or catalytic landscape parameters")
        if not 0 <= self.replication_coupling <= 1:
            raise ValueError("replication_coupling must lie in [0, 1]")
        if not 0 <= self.mutation_rate <= 0.5:
            raise ValueError("mutation_rate must lie in [0, 0.5]")
        if not 0 < self.fuel_feed < 1 or not 0 < self.monomer_feed < 1:
            raise ValueError("feed fractions must lie strictly inside (0, 1)")
        if min(self.k0, self.krep, self.kmaint, self.q_fuel, self.q_monomer) <= 0:
            raise ValueError("kinetic and flow rates must be positive")
        if self.monomers_per_catalyst < 1 or self.atp_per_birth < 1:
            raise ValueError("replication stoichiometries must be positive integers")
        if self.duration <= 0 or self.steps < 10 or self.rtol <= 0 or self.atol <= 0:
            raise ValueError("invalid integration settings")


def mutation_kernel(key_bits: int, mutation_rate: float) -> np.ndarray:
    """Symmetric bit-flip mutation kernel over integer-encoded bit strings."""
    if key_bits < 1 or not 0 <= mutation_rate <= 0.5:
        raise ValueError("invalid key length or mutation rate")
    n = 2 ** key_bits
    kernel = np.empty((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            hamming = (i ^ j).bit_count()
            kernel[i, j] = mutation_rate ** hamming * (1.0 - mutation_rate) ** (key_bits - hamming)
    return kernel


def hamming_distances(key_bits: int, target: int) -> np.ndarray:
    if not 0 <= target < 2 ** key_bits:
        raise ValueError("target genotype is outside the key space")
    return np.asarray([(i ^ target).bit_count() for i in range(2 ** key_bits)], dtype=float)


def evaluate_state(
    state: Sequence[float],
    cfg: ConfigV02,
    target: int,
    kernel: np.ndarray,
    replication: bool = True,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Evaluate deterministic reaction rates, affinities and entropy production."""
    y = np.asarray(state, dtype=float)
    n = cfg.genotype_count
    if y.shape != (3 + n,):
        raise ValueError(f"state must have {3+n} entries: fuel, ATP, monomer, then genotypes")
    f, atp, monomer = y[:3]
    c = y[3:]
    if not (0 < f < 1 and 0 < atp < 1 and 0 < monomer < 1):
        raise ValueError("fuel, ATP and monomer activities must lie strictly inside (0, 1)")
    if np.any(c < 0):
        raise ValueError("genotype concentrations cannot be negative")
    if kernel.shape != (n, n) or not np.allclose(kernel, kernel.T, atol=1e-12):
        raise ValueError("mutation kernel must be square and symmetric")
    if not np.allclose(kernel.sum(axis=1), 1.0, atol=1e-12):
        raise ValueError("mutation kernel rows must sum to one")

    waste, adp, polymer = 1.0 - f, 1.0 - atp, 1.0 - monomer
    distances = hamming_distances(cfg.key_bits, target)
    match = np.exp(-distances / cfg.mismatch_scale)
    alpha = 1.0 + cfg.gain * match
    leverage = 1.0 - math.exp(-cfg.barrier)

    # R1: F + D <-> W + T. The uncatalysed route remains present.
    drive1 = f * adp - math.exp(-cfg.mu1) * waste * atp
    j1_uncatalysed = cfg.k0 * math.exp(-cfg.barrier) * drive1
    j1_catalysed = (
        cfg.k0 * math.exp(-cfg.barrier) * leverage * (alpha - 1.0) * c * drive1
    )
    j1 = j1_uncatalysed + float(j1_catalysed.sum())

    # R2: C_i + mM + nT <-> C_i + C_j + mP + nD.
    # The same genotype-specific catalyst accelerates both directions. This is
    # the explicit autocatalytic/pleiotropic assumption varied by replication_coupling.
    krep_i = cfg.krep * (
        1.0 + cfg.replication_coupling * (alpha - 1.0) * leverage
    )
    forward = np.zeros((n, n), dtype=float)
    reverse = np.zeros((n, n), dtype=float)
    if replication:
        forward = (
            krep_i[:, None] * kernel * c[:, None]
            * (monomer ** cfg.monomers_per_catalyst)
            * (atp ** cfg.atp_per_birth)
        )
        reverse = (
            krep_i[:, None] * kernel * c[:, None] * c[None, :]
            * math.exp(-cfg.mu2)
            * (polymer ** cfg.monomers_per_catalyst)
            * (adp ** cfg.atp_per_birth)
        )
    j2_matrix = forward - reverse
    j2 = float(j2_matrix.sum())

    # R3: T <-> D, a generic maintenance/hydrolysis sink present in every arm.
    j3 = cfg.kmaint * (
        atp - math.exp(-cfg.mu3) * adp
    )

    dy = np.zeros_like(y)
    dy[0] = cfg.q_fuel * (cfg.fuel_feed - f) - j1
    dy[1] = j1 - cfg.atp_per_birth * j2 - j3
    dy[2] = cfg.q_monomer * (cfg.monomer_feed - monomer) - cfg.monomers_per_catalyst * j2
    if replication:
        dy[3:] = j2_matrix.sum(axis=0)

    # Local-detailed-balance affinities from the same standard potentials.
    affinity1 = cfg.mu1 + math.log(f * adp / (waste * atp))
    affinity2 = (cfg.mu2 + (
        cfg.monomers_per_catalyst * math.log(monomer / polymer)
        + cfg.atp_per_birth * math.log(atp / adp)
        - np.log(np.maximum(c, 1e-300))
    )) if replication else np.zeros(n, dtype=float)
    affinity3 = cfg.mu3 + math.log(atp / adp)

    sigma1 = j1 * affinity1
    sigma2 = float(np.sum(j2_matrix * affinity2[None, :])) if replication else 0.0
    sigma3 = j3 * affinity3
    w0 = 1.0 - cfg.fuel_feed
    p0 = 1.0 - cfg.monomer_feed
    sigma_flow_fuel = cfg.q_fuel * (
        (cfg.fuel_feed - f) * math.log(cfg.fuel_feed / f)
        + (w0 - waste) * math.log(w0 / waste)
    )
    sigma_flow_monomer = cfg.q_monomer * (
        (cfg.monomer_feed - monomer) * math.log(cfg.monomer_feed / monomer)
        + (p0 - polymer) * math.log(p0 / polymer)
    )
    sigma_total = sigma1 + sigma2 + sigma3 + sigma_flow_fuel + sigma_flow_monomer

    work_potential = cfg.mu3 + math.log(atp / adp)
    fuel_potential_drop = (
        cfg.mu_fuel_std - cfg.mu_waste_std + math.log(f / waste)
    )
    f0, w0 = cfg.fuel_feed, 1.0 - cfg.fuel_feed
    m0, p0 = cfg.monomer_feed, 1.0 - cfg.monomer_feed
    reservoir_free_energy_input_rate = (
        cfg.q_fuel * (
            (f0 - f) * (cfg.mu_fuel_std + math.log(f0))
            + (w0 - waste) * (cfg.mu_waste_std + math.log(w0))
        )
        + cfg.q_monomer * (
            (m0 - monomer) * (cfg.mu_monomer_std + math.log(m0))
            + (p0 - polymer) * (cfg.mu_polymer_std + math.log(p0))
        )
    )
    diagnostics = {
        "target": int(target),
        "distances": distances,
        "catalytic_factors": alpha,
        "replication_rate_constants": krep_i,
        "j1_uncatalysed": j1_uncatalysed,
        "j1_catalysed_by_genotype": j1_catalysed,
        "j1_total": j1,
        "j2_matrix": j2_matrix,
        "j2_forward": float(forward.sum()),
        "j2_reverse": float(reverse.sum()),
        "j2_net": j2,
        "j3_maintenance": j3,
        "affinity1": affinity1,
        "affinity2": affinity2,
        "affinity3": affinity3,
        "sigma_reaction1": sigma1,
        "sigma_replication": sigma2,
        "sigma_maintenance": sigma3,
        "sigma_flow_fuel": sigma_flow_fuel,
        "sigma_flow_monomer": sigma_flow_monomer,
        "sigma_total": sigma_total,
        "work_potential": work_potential,
        "fuel_potential_drop": fuel_potential_drop,
        "reservoir_free_energy_input_rate": reservoir_free_energy_input_rate,
        "fuel_free_energy_rate": j1 * fuel_potential_drop,
        "work_generation_rate": j1 * work_potential,
        "work_replication_rate": cfg.atp_per_birth * j2 * work_potential,
        "work_maintenance_rate": j3 * work_potential,
    }
    return dy, diagnostics


def free_energy_density(state: Sequence[float], cfg: ConfigV02) -> float:
    """Ideal-mixture free-energy density for the complete declared internal state."""
    y = np.asarray(state, dtype=float)
    f, atp, monomer = y[:3]
    c = y[3:]
    species = [
        (f, cfg.mu_fuel_std), (1.0 - f, cfg.mu_waste_std),
        (atp, cfg.mu_atp_std), (1.0 - atp, cfg.mu_adp_std),
        (monomer, cfg.mu_monomer_std), (1.0 - monomer, cfg.mu_polymer_std),
    ]
    total = 0.0
    for x, mu0 in species:
        if x > 0:
            total += x * (mu0 + math.log(x) - 1.0)
    for x in c:
        if x > 0:
            total += x * (cfg.mu_catalyst_std + math.log(x) - 1.0)
    return float(total)



def work_pool_free_energy(state: Sequence[float], cfg: ConfigV02) -> float:
    """Free energy stored in the internal T/D work-currency pool."""
    atp = float(np.asarray(state, dtype=float)[1])
    adp = 1.0 - atp
    return float(
        atp * (cfg.mu_atp_std + math.log(atp) - 1.0)
        + adp * (cfg.mu_adp_std + math.log(adp) - 1.0)
    )


def free_energy_balance(state: Sequence[float], cfg: ConfigV02, target: int,
                        kernel: np.ndarray, replication: bool = True) -> dict[str, float]:
    """Check external chemical free-energy input - dG/dt = total entropy production."""
    y = np.asarray(state, dtype=float)
    dy, diag = evaluate_state(y, cfg, target, kernel, replication)
    f, atp, monomer = y[:3]
    c = y[3:]
    waste, adp, polymer = 1.0 - f, 1.0 - atp, 1.0 - monomer

    mu_f = cfg.mu_fuel_std + math.log(f)
    mu_w = cfg.mu_waste_std + math.log(waste)
    mu_t = cfg.mu_atp_std + math.log(atp)
    mu_d = cfg.mu_adp_std + math.log(adp)
    mu_m = cfg.mu_monomer_std + math.log(monomer)
    mu_p = cfg.mu_polymer_std + math.log(polymer)
    gradient = np.asarray(
        [mu_f - mu_w, mu_t - mu_d, mu_m - mu_p]
        + [cfg.mu_catalyst_std + math.log(x) if x > 0 else 0.0 for x in c],
        dtype=float,
    )
    dG_dt = float(np.dot(gradient, dy))

    f0, w0 = cfg.fuel_feed, 1.0 - cfg.fuel_feed
    m0, p0 = cfg.monomer_feed, 1.0 - cfg.monomer_feed
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
    residual = reservoir_input - dG_dt - diag["sigma_total"]
    return {
        "reservoir_free_energy_input_rate": float(reservoir_input),
        "system_free_energy_change_rate": dG_dt,
        "entropy_production_rate": float(diag["sigma_total"]),
        "residual": float(residual),
    }


def simulate_v02(
    arm: str,
    cfg: ConfigV02,
    target_schedule: Sequence[tuple[float, int]] | None = None,
) -> dict[str, Any]:
    """Run N, M, D or L over a piecewise-constant target schedule."""
    cfg.validate()
    if arm not in ("N", "M", "D", "L"):
        raise ValueError("v0.2 currently supports arms N, M, D and L")
    n = cfg.genotype_count
    c0 = np.asarray(cfg.initial_concentrations, dtype=float)
    if arm == "N":
        c0 = np.zeros(n, dtype=float)
    initial = np.concatenate(([cfg.fuel_feed, 0.5, cfg.monomer_feed], c0))
    replication = arm in ("D", "L")
    if arm == "L":
        kernel = mutation_kernel(cfg.key_bits, cfg.mutation_rate)
    else:
        kernel = np.eye(n)

    if target_schedule is None:
        schedule = [(0.0, 0)]
    else:
        schedule = list(target_schedule)
    if not schedule or schedule[0][0] != 0.0:
        raise ValueError("target_schedule must begin at time 0")
    if any(t < 0 or t >= cfg.duration or not 0 <= target < n
           for t, target in schedule):
        raise ValueError("invalid target schedule")
    if any(schedule[i][0] >= schedule[i + 1][0] for i in range(len(schedule) - 1)):
        raise ValueError("target schedule times must be strictly increasing")

    time_parts: list[np.ndarray] = []
    state_parts: list[np.ndarray] = []
    target_parts: list[np.ndarray] = []
    segment_solutions: list[tuple[np.ndarray, np.ndarray, int]] = []
    for idx, (start, target) in enumerate(schedule):
        stop = schedule[idx + 1][0] if idx + 1 < len(schedule) else cfg.duration
        points = max(2, int(round(cfg.steps * (stop - start) / cfg.duration)) + 1)
        t_eval = np.linspace(start, stop, points)
        def rhs(t: float, y: np.ndarray) -> np.ndarray:
            return evaluate_state(y, cfg, target, kernel, replication)[0]
        sol = solve_ivp(
            rhs, (start, stop), initial, method="BDF", t_eval=t_eval,
            rtol=cfg.rtol, atol=cfg.atol, max_step=cfg.duration / cfg.steps,
        )
        if not sol.success:
            raise RuntimeError(f"v0.2 integration failed: {sol.message}")
        segment_solutions.append((sol.t.copy(), sol.y.copy(), int(target)))
        if np.any(sol.y[:3] <= 0) or np.any(sol.y[:3] >= 1):
            raise RuntimeError("integration left the positive activity domain; reduce the timestep")
        if np.any(sol.y[3:] < -1e-10):
            raise RuntimeError("integration produced a negative genotype concentration")
        if time_parts:
            time_parts.append(sol.t[1:])
            state_parts.append(sol.y[:, 1:])
            target_parts.append(np.full(len(sol.t) - 1, target, dtype=int))
        else:
            time_parts.append(sol.t)
            state_parts.append(sol.y)
            target_parts.append(np.full(len(sol.t), target, dtype=int))
        initial = sol.y[:, -1]

    times = np.concatenate(time_parts)
    states = np.concatenate(state_parts, axis=1)
    targets = np.concatenate(target_parts)
    trajectory: list[dict[str, Any]] = []
    max_balance_residual = 0.0
    for k, t in enumerate(times):
        state = states[:, k]
        _, diag = evaluate_state(state, cfg, int(targets[k]), kernel, replication)
        balance = free_energy_balance(state, cfg, int(targets[k]), kernel, replication)
        max_balance_residual = max(max_balance_residual, abs(balance["residual"]))
        row = {
            "time": float(t), "fuel": float(state[0]), "atp": float(state[1]),
            "monomer": float(state[2]), "total_catalyst": float(state[3:].sum()),
            "target": int(targets[k]), "j1_total": float(diag["j1_total"]),
            "j2_net": float(diag["j2_net"]), "j2_forward": float(diag["j2_forward"]),
            "j2_reverse": float(diag["j2_reverse"]),
            "j3_maintenance": float(diag["j3_maintenance"]),
            "sigma_total": float(diag["sigma_total"]),
            "sigma_reaction1": float(diag["sigma_reaction1"]),
            "sigma_replication": float(diag["sigma_replication"]),
            "sigma_maintenance": float(diag["sigma_maintenance"]),
            "sigma_flow_fuel": float(diag["sigma_flow_fuel"]),
            "sigma_flow_monomer": float(diag["sigma_flow_monomer"]),
        }
        for i, value in enumerate(state[3:]):
            row[f"catalyst_{i}"] = float(value)
        trajectory.append(row)

    def integral(key: str) -> float:
        # Integrate each constant-target segment separately. Rates can jump at
        # a target switch even though the chemical state remains continuous.
        total = 0.0
        for segment_times, segment_states, segment_target in segment_solutions:
            values = []
            for k in range(len(segment_times)):
                _, segment_diag = evaluate_state(
                    segment_states[:, k], cfg, segment_target, kernel, replication
                )
                values.append(segment_diag[key])
            total += float(simpson(np.asarray(values, dtype=float), x=segment_times))
        return total

    late_start = int(0.8 * len(trajectory))
    late = trajectory[late_start:]
    cumulative_sigma = integral("sigma_total")
    cumulative_work_generation = integral("work_generation_rate")
    cumulative_work_replication = integral("work_replication_rate")
    cumulative_work_maintenance = integral("work_maintenance_rate")
    cumulative_reservoir_input = integral("reservoir_free_energy_input_rate")
    initial_free_energy = free_energy_density(states[:, 0], cfg)
    final_free_energy = free_energy_density(states[:, -1], cfg)
    initial_work_free_energy = work_pool_free_energy(states[:, 0], cfg)
    final_work_free_energy = work_pool_free_energy(states[:, -1], cfg)
    return {
        "arm": arm,
        "config": asdict(cfg),
        "target_schedule": [(float(t), int(x)) for t, x in schedule],
        "initial_state": states[:, 0].tolist(),
        "final_state": states[:, -1].tolist(),
        "initial_catalyst_concentration": float(states[3:, 0].sum()),
        "final_catalyst_concentration": float(states[3:, -1].sum()),
        "late_throughput": float(np.mean([r["j1_total"] for r in late])),
        "late_entropy_production": float(np.mean([r["sigma_total"] for r in late])),
        "cumulative_fuel_reaction_extent": integral("j1_total"),
        "cumulative_replication_net_extent": integral("j2_net"),
        "cumulative_replication_forward_extent": integral("j2_forward"),
        "cumulative_replication_reverse_extent": integral("j2_reverse"),
        "cumulative_maintenance_extent": integral("j3_maintenance"),
        "cumulative_entropy_production": cumulative_sigma,
        "cumulative_fuel_free_energy": integral("fuel_free_energy_rate"),
        "cumulative_work_generation": cumulative_work_generation,
        "cumulative_work_replication": cumulative_work_replication,
        "cumulative_work_maintenance": cumulative_work_maintenance,
        "cumulative_reservoir_free_energy_input": cumulative_reservoir_input,
        "work_pool_free_energy_change": final_work_free_energy - initial_work_free_energy,
        "work_balance_residual": (
            cumulative_work_generation - cumulative_work_replication
            - cumulative_work_maintenance
            - (final_work_free_energy - initial_work_free_energy)
        ),
        "cumulative_free_energy_balance_residual": (
            cumulative_reservoir_input - (final_free_energy - initial_free_energy)
            - cumulative_sigma
        ),
        "max_free_energy_balance_residual": max_balance_residual,
        "initial_free_energy": initial_free_energy,
        "final_free_energy": final_free_energy,
        "trajectory": trajectory,
    }
