"""Minimal chemostatted autocatalytic network for local chemical disequilibrium.

This is an abstract, dimensionless-activity model, not a proposed prebiotic
reaction or a quantitative model of a particular geochemical environment.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import math
from typing import Any, Iterable

R_J_MOL_K = 8.31446261815324


@dataclass(frozen=True)
class ChemicalConfig:
    """Parameters for A + X <-> 2X + W and X <-> D.

    Activities are dimensionless relative to a 1 mol/L standard state.
    A, W and D are chemostatted by external reservoirs; X is dynamic.
    Rate constants are expressed in s^-1 under this normalized activity
    convention. Equilibrium constants are dimensionless.
    """

    temperature_K: float = 298.15
    feed_activity: float = 1.0
    waste_activity: float = 1.0
    degraded_activity: float = 1.0e-8
    growth_equilibrium_constant: float = 10.0
    growth_forward_rate_s: float = 1.0e-1
    decay_equilibrium_constant: float = 1.0e-4
    decay_forward_rate_s: float = 1.0e-2
    initial_catalyst_activity: float = 1.0e-4
    duration_s: float = 5_000.0
    time_step_s: float = 0.1
    standard_concentration_mol_L: float = 1.0
    background_control_feed_activity: float = 1.0e-6

    def validate(self) -> None:
        positive = {
            "temperature_K": self.temperature_K,
            "growth_equilibrium_constant": self.growth_equilibrium_constant,
            "growth_forward_rate_s": self.growth_forward_rate_s,
            "decay_equilibrium_constant": self.decay_equilibrium_constant,
            "decay_forward_rate_s": self.decay_forward_rate_s,
            "duration_s": self.duration_s,
            "time_step_s": self.time_step_s,
            "standard_concentration_mol_L": self.standard_concentration_mol_L,
            "background_control_feed_activity": self.background_control_feed_activity,
        }
        for name, value in positive.items():
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        nonnegative = {
            "feed_activity": self.feed_activity,
            "waste_activity": self.waste_activity,
            "degraded_activity": self.degraded_activity,
            "initial_catalyst_activity": self.initial_catalyst_activity,
        }
        for name, value in nonnegative.items():
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if self.feed_activity == 0 or self.waste_activity == 0 or self.degraded_activity == 0:
            raise ValueError("Chemostat activities must be positive; zero activity is singular in ideal chemical potentials")
        steps = self.duration_s / self.time_step_s
        if abs(steps - round(steps)) > 1e-9:
            raise ValueError("duration_s must be an integer multiple of time_step_s")


def _reaction_state(x: float, cfg: ChemicalConfig) -> dict[str, float]:
    """Return rates, reaction free energies and entropy production density."""
    # Detailed-balance-compatible reverse rates: K = k_forward/k_reverse.
    k1f = cfg.growth_forward_rate_s
    k1r = k1f / cfg.growth_equilibrium_constant
    k2f = cfg.decay_forward_rate_s
    k2r = k2f / cfg.decay_equilibrium_constant

    a, w, d = cfg.feed_activity, cfg.waste_activity, cfg.degraded_activity
    # R1: A + X <-> 2X + W. X cancels from the reaction quotient.
    q1 = max(x * w / a, 1.0e-300)
    dg1 = R_J_MOL_K * cfg.temperature_K * math.log(q1 / cfg.growth_equilibrium_constant)
    v1 = k1f * a * x - k1r * x * x * w

    # R2: X <-> D.
    q2 = max(d / max(x, 1.0e-300), 1.0e-300)
    dg2 = R_J_MOL_K * cfg.temperature_K * math.log(q2 / cfg.decay_equilibrium_constant)
    v2 = k2f * x - k2r * d

    # Affinity is -Delta G. Flux and affinity have the same sign for each
    # reversible mass-action reaction under the detailed-balance rates above.
    c0 = cfg.standard_concentration_mol_L
    sigma1 = c0 * v1 * (-dg1) / cfg.temperature_K
    sigma2 = c0 * v2 * (-dg2) / cfg.temperature_K
    return {
        "growth_rate_activity_s": v1,
        "decay_rate_activity_s": v2,
        "growth_delta_g_J_mol": dg1,
        "decay_delta_g_J_mol": dg2,
        "growth_entropy_production_J_L_K_s": sigma1,
        "decay_entropy_production_J_L_K_s": sigma2,
        "total_entropy_production_J_L_K_s": sigma1 + sigma2,
    }


def equilibrium_catalyst_activity(config: ChemicalConfig) -> float:
    """Return the positive fixed point of the one-state deterministic model.

    The ODE is quadratic in X because both reactions are reversible
    mass-action processes and A, W and D are chemostatted.
    """
    config.validate()
    k1f = config.growth_forward_rate_s
    k1r = k1f / config.growth_equilibrium_constant
    k2f = config.decay_forward_rate_s
    k2r = k2f / config.decay_equilibrium_constant
    quadratic = k1r * config.waste_activity
    linear = k1f * config.feed_activity - k2f
    source = k2r * config.degraded_activity
    return (linear + math.sqrt(linear * linear + 4.0 * quadratic * source)) / (2.0 * quadratic)


def _dx_dt(x: float, cfg: ChemicalConfig) -> float:
    state = _reaction_state(x, cfg)
    return state["growth_rate_activity_s"] - state["decay_rate_activity_s"]


def _rk4_step(x: float, dt: float, cfg: ChemicalConfig) -> float:
    k1 = _dx_dt(x, cfg)
    k2 = _dx_dt(max(x + 0.5 * dt * k1, 0.0), cfg)
    k3 = _dx_dt(max(x + 0.5 * dt * k2, 0.0), cfg)
    k4 = _dx_dt(max(x + dt * k3, 0.0), cfg)
    updated = x + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    if updated < -1.0e-12:
        raise ArithmeticError("Integration produced a negative catalyst activity; reduce time_step_s")
    return max(updated, 0.0)


def simulate_chemical_network(config: ChemicalConfig | None = None) -> dict[str, Any]:
    """Simulate catalyst abundance and thermodynamic dissipation over time."""
    cfg = config or ChemicalConfig()
    cfg.validate()
    n_steps = round(cfg.duration_s / cfg.time_step_s)
    x = cfg.initial_catalyst_activity
    times = [0.0]
    activities = [x]
    entropy_rates: list[float] = []
    growth_entropy_rates: list[float] = []
    decay_entropy_rates: list[float] = []
    growth_rates: list[float] = []
    decay_rates: list[float] = []

    for step in range(n_steps):
        state = _reaction_state(x, cfg)
        entropy_rates.append(state["total_entropy_production_J_L_K_s"])
        growth_entropy_rates.append(state["growth_entropy_production_J_L_K_s"])
        decay_entropy_rates.append(state["decay_entropy_production_J_L_K_s"])
        growth_rates.append(state["growth_rate_activity_s"])
        decay_rates.append(state["decay_rate_activity_s"])
        x = _rk4_step(x, cfg.time_step_s, cfg)
        times.append((step + 1) * cfg.time_step_s)
        activities.append(x)

    final_state = _reaction_state(x, cfg)
    background_config = replace(cfg, feed_activity=cfg.background_control_feed_activity)
    background_activity = equilibrium_catalyst_activity(background_config)
    predicted_equilibrium = equilibrium_catalyst_activity(cfg)
    enrichment = x / max(background_activity, 1.0e-300)
    integrated_entropy = cfg.time_step_s * (
        0.5 * entropy_rates[0] + sum(entropy_rates[1:])
        + 0.5 * final_state["total_entropy_production_J_L_K_s"]
    )
    tail = activities[max(0, int(0.9 * len(activities))):]
    tail_min = min(tail)
    tail_max = max(tail)
    return {
        "model": "chemostatted_autocatalytic_network",
        "configuration": asdict(cfg),
        "reaction_network": {
            "R1": "A + X <-> 2X + W",
            "R2": "X <-> D",
            "interpretation": "A, W and D are chemostatted reservoirs; X is the dynamic autocatalyst.",
        },
        "final": {
            "catalyst_activity": x,
            "background_control_equilibrium_activity": background_activity,
            "analytic_equilibrium_catalyst_activity": predicted_equilibrium,
            "relative_error_from_analytic_equilibrium": abs(x - predicted_equilibrium) / max(predicted_equilibrium, 1.0e-300),
            "catalyst_enrichment_over_background": enrichment,
            "linear_invasion_threshold_feed_activity": cfg.decay_forward_rate_s / cfg.growth_forward_rate_s,
            "net_growth_rate_activity_s": final_state["growth_rate_activity_s"] - final_state["decay_rate_activity_s"],
            **final_state,
        },
        "persistence_diagnostics": {
            "last_10_percent_min_activity": tail_min,
            "last_10_percent_max_activity": tail_max,
            "last_10_percent_relative_range": (tail_max - tail_min) / max(x, 1.0e-300),
            "enriched_over_background_10x": enrichment >= 10.0,
        },
        "time_series": {
            "time_s": times,
            "catalyst_activity": activities,
            "entropy_production_rate_J_L_K_s": entropy_rates + [final_state["total_entropy_production_J_L_K_s"]],
            "growth_entropy_production_rate_J_L_K_s": growth_entropy_rates + [final_state["growth_entropy_production_J_L_K_s"]],
            "decay_entropy_production_rate_J_L_K_s": decay_entropy_rates + [final_state["decay_entropy_production_J_L_K_s"]],
            "growth_rate_activity_s": growth_rates + [final_state["growth_rate_activity_s"]],
            "decay_rate_activity_s": decay_rates + [final_state["decay_rate_activity_s"]],
        },
        "accounting": {
            "entropy_production_definition": "sum_r v_r * (-DeltaG_r) / T, with activities relative to the 1 mol/L standard state",
            "free_energy_dissipation_rate_J_L_s": cfg.temperature_K * final_state["total_entropy_production_J_L_K_s"],
            "integrated_entropy_production_J_L_K": integrated_entropy,
            "standard_concentration_mol_L": cfg.standard_concentration_mol_L,
            "warning": "This is an ideal-solution, chemostatted reaction-network entropy-production estimate, not a complete planetary entropy budget.",
        },
        "limitations": [
            "A, W and D are abstract species; no specific prebiotic chemistry is represented.",
            "The model is well-mixed and has no spatial gradients, diffusion, compartments or mineral surfaces.",
            "Chemostats hold reservoir activities fixed; their pumps and external apparatus are outside the model boundary.",
            "The model has autocatalysis but no heredity, mutation, lineage or Darwinian evolution.",
            "The reaction standard free energies are implied by illustrative equilibrium constants, not measured chemical data.",
            "The entropy production is for the specified idealized reaction network and boundary, not total entropy production of the environment.",
        ],
    }


def run_feed_sweep(feed_activities: Iterable[float], base_config: ChemicalConfig | None = None) -> list[dict[str, float]]:
    """Run independent feed-activity experiments using a common base setup."""
    from dataclasses import replace as dataclass_replace

    base = base_config or ChemicalConfig()
    results = []
    for feed in feed_activities:
        cfg = dataclass_replace(base, feed_activity=float(feed))
        result = simulate_chemical_network(cfg)
        final = result["final"]
        results.append({
            "feed_activity": float(feed),
            "final_catalyst_activity": final["catalyst_activity"],
            "analytic_equilibrium_catalyst_activity": final["analytic_equilibrium_catalyst_activity"],
            "relative_equilibrium_error": final["relative_error_from_analytic_equilibrium"],
            "enrichment_over_background": final["catalyst_enrichment_over_background"],
            "entropy_production_rate_J_L_K_s": final["total_entropy_production_J_L_K_s"],
        })
    return results
