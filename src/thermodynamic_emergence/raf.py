"""Finite-resource, mutually catalytic RAF-like batch network.

The model is deliberately abstract. Food species A and B produce X and Y;
Y catalyses A -> X + W_X and X catalyses B -> Y + W_Y. X and Y also
undergo reversible loss to D_X and D_Y. All species are dynamic: this is a
finite batch, not a chemostatted steady-state model.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

from .chemistry import R_J_MOL_K

SPECIES = ("A", "B", "X", "Y", "W_X", "W_Y", "D_X", "D_Y")
REACTIONS = ("R1: A <-> X + W_X [catalyst Y]", "R2: B <-> Y + W_Y [catalyst X]", "R3: X <-> D_X", "R4: Y <-> D_Y")
STOICHIOMETRIC_MATRIX = (
    (-1, 0, 0, 0),
    (0, -1, 0, 0),
    (1, 0, -1, 0),
    (0, 1, 0, -1),
    (1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 0, 1),
)


@dataclass(frozen=True)
class RafConfig:
    """Dimensionless activities for a finite, well-mixed batch reactor."""

    temperature_K: float = 298.15
    initial_food_A: float = 1.0
    initial_food_B: float = 1.0
    initial_X: float = 1.0e-8
    initial_Y: float = 1.0e-8
    initial_W_X: float = 1.0e-8
    initial_W_Y: float = 1.0e-8
    initial_D_X: float = 1.0e-8
    initial_D_Y: float = 1.0e-8
    production_forward_rate_s: float = 2.0e-2
    production_equilibrium_constant: float = 10.0
    loss_forward_rate_s: float = 1.0e-3
    loss_equilibrium_constant: float = 1.0e-4
    catalytic_strength: float = 100.0
    background_rate_factor: float = 1.0
    duration_s: float = 10.0
    time_step_s: float = 1.0e-3
    standard_concentration_mol_L: float = 1.0

    def validate(self) -> None:
        positive = {
            "temperature_K": self.temperature_K,
            "initial_food_A": self.initial_food_A,
            "initial_food_B": self.initial_food_B,
            "initial_X": self.initial_X,
            "initial_Y": self.initial_Y,
            "initial_W_X": self.initial_W_X,
            "initial_W_Y": self.initial_W_Y,
            "initial_D_X": self.initial_D_X,
            "initial_D_Y": self.initial_D_Y,
            "production_forward_rate_s": self.production_forward_rate_s,
            "production_equilibrium_constant": self.production_equilibrium_constant,
            "loss_forward_rate_s": self.loss_forward_rate_s,
            "loss_equilibrium_constant": self.loss_equilibrium_constant,
            "duration_s": self.duration_s,
            "time_step_s": self.time_step_s,
            "standard_concentration_mol_L": self.standard_concentration_mol_L,
        }
        for name, value in positive.items():
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if not math.isfinite(self.catalytic_strength) or self.catalytic_strength < 0:
            raise ValueError("catalytic_strength must be finite and non-negative")
        if not math.isfinite(self.background_rate_factor) or self.background_rate_factor < 0:
            raise ValueError("background_rate_factor must be finite and non-negative")
        if self.background_rate_factor == 0 and self.catalytic_strength == 0:
            raise ValueError("at least one reaction-rate factor must be positive")
        steps = self.duration_s / self.time_step_s
        if abs(steps - round(steps)) > 1e-9:
            raise ValueError("duration_s must be an integer multiple of time_step_s")


def _rates(state: tuple[float, ...] | list[float], cfg: RafConfig) -> tuple[list[float], list[float], list[float]]:
    a, b, x, y, wx, wy, dx, dy = state
    kpf = cfg.production_forward_rate_s
    kpr = kpf / cfg.production_equilibrium_constant
    klf = cfg.loss_forward_rate_s
    klr = klf / cfg.loss_equilibrium_constant
    # Catalysis multiplies forward and reverse rates equally. It changes
    # kinetics but not the equilibrium constant or equilibrium composition.
    v1 = (kpf * a - kpr * x * wx) * (cfg.background_rate_factor + cfg.catalytic_strength * y)
    v2 = (kpf * b - kpr * y * wy) * (cfg.background_rate_factor + cfg.catalytic_strength * x)
    v3 = klf * x - klr * dx
    v4 = klf * y - klr * dy
    rates = [v1, v2, v3, v4]
    quotients = [x * wx / a, y * wy / b, dx / x, dy / y]
    equilibria = [cfg.production_equilibrium_constant, cfg.production_equilibrium_constant,
                  cfg.loss_equilibrium_constant, cfg.loss_equilibrium_constant]
    affinities = [-R_J_MOL_K * cfg.temperature_K * math.log(q / k)
                  for q, k in zip(quotients, equilibria)]
    return rates, affinities, [r * affinity / cfg.temperature_K for r, affinity in zip(rates, affinities)]


def _derivative(s: list[float], cfg: RafConfig) -> list[float]:
    v, _, _ = _rates(s, cfg)
    v1, v2, v3, v4 = v
    return [-v1, -v2, v1 - v3, v2 - v4, v1, v2, v3, v4]


def _rk4(s: list[float], dt: float, cfg: RafConfig) -> list[float]:
    def shifted(base: list[float], delta: list[float], factor: float) -> list[float]:
        return [max(value + factor * change, 1.0e-300) for value, change in zip(base, delta)]
    k1 = _derivative(s, cfg)
    k2 = _derivative(shifted(s, k1, dt / 2), cfg)
    k3 = _derivative(shifted(s, k2, dt / 2), cfg)
    k4 = _derivative(shifted(s, k3, dt), cfg)
    updated = [value + dt * (a + 2*b + 2*c + d) / 6
               for value, a, b, c, d in zip(s, k1, k2, k3, k4)]
    if min(updated) <= 0:
        raise ArithmeticError("Integration produced a non-positive activity; reduce time_step_s")
    return updated


def simulate_raf_network(config: RafConfig | None = None) -> dict[str, Any]:
    """Simulate the finite-resource RAF-like network and its no-catalysis null."""
    cfg = config or RafConfig()
    cfg.validate()
    state = [cfg.initial_food_A, cfg.initial_food_B, cfg.initial_X, cfg.initial_Y,
             cfg.initial_W_X, cfg.initial_W_Y, cfg.initial_D_X, cfg.initial_D_Y]
    initial = state.copy()
    n = round(cfg.duration_s / cfg.time_step_s)
    times = [0.0]
    trajectory = [state.copy()]
    sigma_total = []
    sigma_by_reaction = [[], [], [], []]
    for step in range(n):
        rates, affinities, sigma = _rates(state, cfg)
        sigma_total.append(sum(sigma))
        for i in range(4):
            sigma_by_reaction[i].append(sigma[i])
        state = _rk4(state, cfg.time_step_s, cfg)
        times.append((step + 1) * cfg.time_step_s)
        trajectory.append(state.copy())

    rates, affinities, sigma = _rates(state, cfg)
    sigma_total.append(sum(sigma))
    for i in range(4):
        sigma_by_reaction[i].append(sigma[i])
    c0 = cfg.standard_concentration_mol_L
    integrated_sigma = cfg.time_step_s * (
        0.5 * sum(_rates(initial, cfg)[2]) + sum(sigma_total[1:-1]) + 0.5 * sigma_total[-1]
    )
    initial_total_food = initial[0] + initial[1]
    final_total_intermediates = state[2] + state[3]
    return {
        "model": "finite_resource_mutually_catalytic_raf_like_batch",
        "configuration": asdict(cfg),
        "food_set": ["A", "B"],
        "reaction_set": [
            {"id": "R1", "reaction": "A <-> X + W_X", "catalyst": "Y"},
            {"id": "R2", "reaction": "B <-> Y + W_Y", "catalyst": "X"},
        ],
        "loss_reactions": [
            {"id": "R3", "reaction": "X <-> D_X"},
            {"id": "R4", "reaction": "Y <-> D_Y"},
        ],
        "species_order": list(SPECIES),
        "stoichiometric_matrix_species_by_reaction": [list(row) for row in STOICHIOMETRIC_MATRIX],
        "raf_closure": {
            "food_generated": True,
            "reflexively_autocatalytic": True,
            "explanation": "R1 is catalysed by Y, which R2 produces; R2 is catalysed by X, which R1 produces. A and B are the only stoichiometric reactants of the RAF reaction set and belong to the food set.",
            "important_qualification": "The RAF property is a formal network-closure result. It does not establish spontaneous formation, kinetic viability in a real chemical setting, or evolution.",
        },
        "final": dict(zip(SPECIES, state)),
        "initial": dict(zip(SPECIES, initial)),
        "diagnostics": {
            "total_food_remaining": state[0] + state[1],
            "food_conversion_fraction": 1.0 - (state[0] + state[1]) / initial_total_food,
            "X_plus_Y_activity": final_total_intermediates,
            "integrated_reaction_entropy_production_J_L_K": integrated_sigma * c0,
            "final_entropy_production_rate_J_L_K_s": sum(sigma) * c0,
            "minimum_reaction_entropy_production_rate_J_L_K_s": min(min(values) for values in sigma_by_reaction) * c0,
            "moiety_balance_errors": {
                "A_X_moiety": (state[0] + state[2] + state[6]) - (initial[0] + initial[2] + initial[6]),
                "A_waste_moiety": (state[0] + state[4]) - (initial[0] + initial[4]),
                "B_Y_moiety": (state[1] + state[3] + state[7]) - (initial[1] + initial[3] + initial[7]),
                "B_waste_moiety": (state[1] + state[5]) - (initial[1] + initial[5]),
            },
        },
        "time_series": {
            "time_s": times,
            "species_activities": [dict(zip(SPECIES, row)) for row in trajectory],
            "entropy_production_rate_J_L_K_s": [value * c0 for value in sigma_total],
        },
        "accounting": {
            "definition": "sum_r v_r * (-Delta_r G_r) / T using ideal dimensionless activities",
            "boundary": "Finite batch reactor; all food, products, wastes and degradation products are dynamic. No chemostat or replenishment work is included.",
            "interpretation": "The initial chemical disequilibrium is a finite free-energy store. Entropy production is transient and must decay as the closed batch approaches equilibrium.",
        },
        "limitations": [
            "All species are abstract; no prebiotic molecular identities or measured thermodynamic data are assigned.",
            "The reaction set is RAF-like by formal catalyst closure, but the small uncatalysed background rates seed X and Y from food. This is not evidence of spontaneous molecular assembly.",
            "The reactor is well-mixed and has no spatial gradients, compartments, mineral surfaces or transport.",
            "Catalysts multiply forward and reverse rates equally, preserving detailed balance; they accelerate kinetics but do not change equilibrium composition.",
            "The finite batch has no sustained external energy input or non-equilibrium steady state; it relaxes toward equilibrium as the finite food disequilibrium is consumed.",
            "No copying with heredity, mutation, lineage or Darwinian evolution is represented.",
            "The entropy production is for this declared idealized reaction boundary, not a planetary entropy budget.",
        ],
    }


def compare_catalysis(config: RafConfig | None = None) -> dict[str, Any]:
    """Compare the mutually catalytic network with an otherwise identical null."""
    cfg = config or RafConfig()
    catalytic = simulate_raf_network(cfg)
    null_cfg = RafConfig(**{**asdict(cfg), "catalytic_strength": 0.0})
    null = simulate_raf_network(null_cfg)
    return {
        "catalytic_strength": cfg.catalytic_strength,
        "catalytic_final": catalytic["final"],
        "uncatalysed_null_final": null["final"],
        "catalytic_X_plus_Y": catalytic["diagnostics"]["X_plus_Y_activity"],
        "uncatalysed_X_plus_Y": null["diagnostics"]["X_plus_Y_activity"],
        "finite_time_amplification_ratio": catalytic["diagnostics"]["X_plus_Y_activity"] / null["diagnostics"]["X_plus_Y_activity"],
        "catalytic_integrated_entropy_production_J_L_K": catalytic["diagnostics"]["integrated_reaction_entropy_production_J_L_K"],
        "uncatalysed_integrated_entropy_production_J_L_K": null["diagnostics"]["integrated_reaction_entropy_production_J_L_K"],
        "equilibrium_warning": "The finite-time comparison measures kinetic acceleration. Catalysis does not change the equilibrium composition under the detailed-balance-preserving rate law.",
    }


def simulate_perturbation(
    config: RafConfig | None = None,
    *,
    perturbation_time_s: float = 5.0,
    removal_fraction: float = 0.99,
) -> dict[str, Any]:
    """Remove a fraction of X and Y at a defined time and measure recovery."""
    cfg = config or RafConfig()
    cfg.validate()
    if not math.isfinite(perturbation_time_s) or not 0 < perturbation_time_s < cfg.duration_s:
        raise ValueError("perturbation_time_s must lie strictly between zero and duration_s")
    if not math.isfinite(removal_fraction) or not 0 <= removal_fraction < 1:
        raise ValueError("removal_fraction must be finite and in [0, 1)")
    steps = perturbation_time_s / cfg.time_step_s
    if abs(steps - round(steps)) > 1e-9:
        raise ValueError("perturbation_time_s must be an integer multiple of time_step_s")

    before_cfg = RafConfig(**{**asdict(cfg), "duration_s": perturbation_time_s})
    before = simulate_raf_network(before_cfg)
    pre = before["final"]
    post_initial = dict(pre)
    post_initial["X"] *= (1.0 - removal_fraction)
    post_initial["Y"] *= (1.0 - removal_fraction)
    remaining_cfg = RafConfig(**{
        **asdict(cfg),
        "duration_s": cfg.duration_s - perturbation_time_s,
        "initial_food_A": post_initial["A"],
        "initial_food_B": post_initial["B"],
        "initial_X": post_initial["X"],
        "initial_Y": post_initial["Y"],
        "initial_W_X": post_initial["W_X"],
        "initial_W_Y": post_initial["W_Y"],
        "initial_D_X": post_initial["D_X"],
        "initial_D_Y": post_initial["D_Y"],
    })
    after = simulate_raf_network(remaining_cfg)
    pre_xy = pre["X"] + pre["Y"]
    post_xy = post_initial["X"] + post_initial["Y"]
    final_xy = after["diagnostics"]["X_plus_Y_activity"]
    removed_xy = pre_xy - post_xy
    recovery = (final_xy - post_xy) / removed_xy if removed_xy > 0 else 0.0
    baseline = simulate_raf_network(cfg)
    baseline_xy = baseline["diagnostics"]["X_plus_Y_activity"]
    return {
        "model": "finite_resource_mutual_catalysis_perturbation",
        "configuration": asdict(cfg),
        "perturbation_time_s": perturbation_time_s,
        "removal_fraction": removal_fraction,
        "pre_perturbation": pre,
        "immediately_post_perturbation": post_initial,
        "final_after_perturbation": after["final"],
        "unperturbed_final": baseline["final"],
        "diagnostics": {
            "X_plus_Y_before": pre_xy,
            "X_plus_Y_immediately_after": post_xy,
            "X_plus_Y_final": final_xy,
            "X_plus_Y_unperturbed_final": baseline_xy,
            "fraction_of_removed_XY_recovered": recovery,
            "fraction_of_preperturbation_XY_restored": final_xy / pre_xy if pre_xy else 0.0,
            "final_XY_relative_to_unperturbed": final_xy / baseline_xy if baseline_xy else 0.0,
            "food_remaining_at_perturbation": pre["A"] + pre["B"],
            "food_remaining_at_end": after["final"]["A"] + after["final"]["B"],
            "post_perturbation_moiety_balance_errors": after["diagnostics"]["moiety_balance_errors"],
            "post_perturbation_integrated_entropy_production_J_L_K": after["diagnostics"]["integrated_reaction_entropy_production_J_L_K"],
        },
        "interpretation": "Recovery is measured after physical removal of X and Y. The post-perturbation conservation ledger starts from the remaining material; removed catalyst material is outside the reactor boundary. Recovery is conditional on residual food, background reaction and residual catalysts.",
        "limitations": [
            "The intervention removes catalyst material but does not model the physical separation mechanism or its energetic cost.",
            "The network remains abstract and seeded; this is not spontaneous molecular assembly.",
            "The finite batch has no replenishment or sustained driving and ultimately relaxes toward equilibrium.",
            "A successful recovery in this model is not evidence of life, heredity or Darwinian evolution.",
        ],
    }


def run_perturbation_sweep(
    config: RafConfig | None = None,
    *,
    removal_fractions: tuple[float, ...] = (0.9, 0.99, 0.999),
    background_factors: tuple[float, ...] = (1.0, 0.1, 0.01, 0.001),
    perturbation_time_s: float = 5.0,
) -> list[dict[str, float]]:
    """Cross removal severity with uncatalysed background reaction factors."""
    cfg = config or RafConfig()
    rows = []
    for background in background_factors:
        for removal in removal_fractions:
            run = simulate_perturbation(
                RafConfig(**{**asdict(cfg), "background_rate_factor": background}),
                perturbation_time_s=perturbation_time_s,
                removal_fraction=removal,
            )
            d = run["diagnostics"]
            rows.append({
                "background_rate_factor": background,
                "removal_fraction": removal,
                "fraction_of_removed_XY_recovered": d["fraction_of_removed_XY_recovered"],
                "fraction_of_preperturbation_XY_restored": d["fraction_of_preperturbation_XY_restored"],
                "final_XY_relative_to_unperturbed": d["final_XY_relative_to_unperturbed"],
                "food_remaining_at_perturbation": d["food_remaining_at_perturbation"],
                "food_remaining_at_end": d["food_remaining_at_end"],
            })
    return rows
