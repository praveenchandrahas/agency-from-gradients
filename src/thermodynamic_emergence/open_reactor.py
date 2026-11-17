"""Continuously driven CSTR model for a mutually catalytic chemical network.

All species exchange with finite-activity feed/product reservoirs through a
well-mixed dilution flow. The model separates reaction entropy production
from reservoir-exchange entropy production. Pump/controller work is not
included and must not be silently folded into either quantity.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

from .chemistry import R_J_MOL_K
from .raf import SPECIES, STOICHIOMETRIC_MATRIX


@dataclass(frozen=True)
class OpenReactorConfig:
    temperature_K: float = 298.15
    feed_A: float = 1.0
    feed_B: float = 1.0
    background_feed_activity: float = 1.0e-8
    catalyst_feed_activity: float = 1.0e-8
    flow_rate_s: float = 0.05
    production_forward_rate_s: float = 2.0e-2
    production_equilibrium_constant: float = 10.0
    loss_forward_rate_s: float = 1.0e-3
    loss_equilibrium_constant: float = 1.0e-4
    catalytic_strength: float = 10.0
    background_rate_factor: float = 0.01
    duration_s: float = 300.0
    time_step_s: float = 0.002
    standard_concentration_mol_L: float = 1.0
    ness_window_fraction: float = 0.2
    ness_tolerance: float = 1.0e-3

    def validate(self) -> None:
        positive = {
            "temperature_K": self.temperature_K,
            "feed_A": self.feed_A,
            "feed_B": self.feed_B,
            "background_feed_activity": self.background_feed_activity,
            "catalyst_feed_activity": self.catalyst_feed_activity,
            "flow_rate_s": self.flow_rate_s,
            "production_forward_rate_s": self.production_forward_rate_s,
            "production_equilibrium_constant": self.production_equilibrium_constant,
            "loss_forward_rate_s": self.loss_forward_rate_s,
            "loss_equilibrium_constant": self.loss_equilibrium_constant,
            "duration_s": self.duration_s,
            "time_step_s": self.time_step_s,
            "standard_concentration_mol_L": self.standard_concentration_mol_L,
            "ness_window_fraction": self.ness_window_fraction,
            "ness_tolerance": self.ness_tolerance,
        }
        for name, value in positive.items():
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.ness_window_fraction >= 1:
            raise ValueError("ness_window_fraction must be less than one")
        if not math.isfinite(self.catalytic_strength) or self.catalytic_strength < 0:
            raise ValueError("catalytic_strength must be finite and non-negative")
        if not math.isfinite(self.background_rate_factor) or self.background_rate_factor < 0:
            raise ValueError("background_rate_factor must be finite and non-negative")
        if self.background_rate_factor == 0 and self.catalytic_strength == 0:
            raise ValueError("at least one reaction-rate factor must be positive")
        steps = self.duration_s / self.time_step_s
        if abs(steps - round(steps)) > 1e-9:
            raise ValueError("duration_s must be an integer multiple of time_step_s")


def _feed_vector(cfg: OpenReactorConfig) -> list[float]:
    return [cfg.feed_A, cfg.feed_B, cfg.catalyst_feed_activity,
            cfg.catalyst_feed_activity, cfg.background_feed_activity,
            cfg.background_feed_activity, cfg.background_feed_activity,
            cfg.background_feed_activity]


def _reaction_terms(state: list[float], cfg: OpenReactorConfig):
    a, b, x, y, wx, wy, dx, dy = state
    kpf = cfg.production_forward_rate_s
    kpr = kpf / cfg.production_equilibrium_constant
    klf = cfg.loss_forward_rate_s
    klr = klf / cfg.loss_equilibrium_constant
    v = [
        (kpf * a - kpr * x * wx) * (cfg.background_rate_factor + cfg.catalytic_strength * y),
        (kpf * b - kpr * y * wy) * (cfg.background_rate_factor + cfg.catalytic_strength * x),
        klf * x - klr * dx,
        klf * y - klr * dy,
    ]
    q = [x * wx / a, y * wy / b, dx / x, dy / y]
    k = [cfg.production_equilibrium_constant, cfg.production_equilibrium_constant,
         cfg.loss_equilibrium_constant, cfg.loss_equilibrium_constant]
    delta_g = [R_J_MOL_K * cfg.temperature_K * math.log(qi / ki)
               for qi, ki in zip(q, k)]
    sigma_reaction = [vi * (-dgi) / cfg.temperature_K for vi, dgi in zip(v, delta_g)]
    return v, delta_g, sigma_reaction


def _exchange_terms(state: list[float], cfg: OpenReactorConfig):
    feed = _feed_vector(cfg)
    fluxes = [cfg.flow_rate_s * (ci - si) for ci, si in zip(feed, state)]
    # Each species exchanges with a finite-activity reservoir. The net
    # exchange flux times its chemical-potential difference is non-negative.
    sigma = [
        flux * R_J_MOL_K * math.log(ci / si) / cfg.temperature_K
        for flux, ci, si in zip(fluxes, feed, state)
    ]
    return fluxes, sigma


def _derivative(state: list[float], cfg: OpenReactorConfig) -> list[float]:
    v, _, _ = _reaction_terms(state, cfg)
    exchange, _ = _exchange_terms(state, cfg)
    reaction = [
        sum(STOICHIOMETRIC_MATRIX[i][j] * v[j] for j in range(4))
        for i in range(len(SPECIES))
    ]
    return [reaction[i] + exchange[i] for i in range(len(SPECIES))]


def _rk4(state: list[float], dt: float, cfg: OpenReactorConfig) -> list[float]:
    def shift(base, deriv, factor):
        return [max(value + factor * change, 1.0e-300)
                for value, change in zip(base, deriv)]
    k1 = _derivative(state, cfg)
    k2 = _derivative(shift(state, k1, dt / 2), cfg)
    k3 = _derivative(shift(state, k2, dt / 2), cfg)
    k4 = _derivative(shift(state, k3, dt), cfg)
    updated = [value + dt * (a + 2*b + 2*c + d) / 6
               for value, a, b, c, d in zip(state, k1, k2, k3, k4)]
    if min(updated) <= 0 or not all(math.isfinite(value) for value in updated):
        raise ArithmeticError("Integration left the positive finite activity domain; reduce time_step_s")
    return updated


def simulate_open_reactor(
    config: OpenReactorConfig | None = None,
    *,
    initial_state: list[float] | tuple[float, ...] | None = None,
) -> dict[str, Any]:
    """Integrate the continuously fed and diluted network and diagnose NESS."""
    cfg = config or OpenReactorConfig()
    cfg.validate()
    feed = _feed_vector(cfg)
    state = feed.copy() if initial_state is None else [float(value) for value in initial_state]
    if len(state) != len(SPECIES) or any(not math.isfinite(value) or value <= 0 for value in state):
        raise ValueError("initial_state must contain eight finite, strictly positive activities")
    initial = state.copy()
    n = round(cfg.duration_s / cfg.time_step_s)
    sample_stride = max(1, n // 2000)
    times = [0.0]
    trajectory = [state.copy()]
    reaction_integral = 0.0
    exchange_integral = 0.0
    reaction_sigma_min = float("inf")
    exchange_sigma_min = float("inf")
    cumulative_in = [0.0] * len(SPECIES)
    cumulative_out = [0.0] * len(SPECIES)
    previous_reaction, previous_exchange = None, None

    for step in range(n):
        _, _, sr = _reaction_terms(state, cfg)
        exchange, se = _exchange_terms(state, cfg)
        reaction_rate = sum(sr)
        exchange_rate = sum(se)
        reaction_sigma_min = min(reaction_sigma_min, min(sr))
        exchange_sigma_min = min(exchange_sigma_min, min(se))
        if previous_reaction is not None:
            reaction_integral += 0.5 * cfg.time_step_s * (previous_reaction + reaction_rate)
            exchange_integral += 0.5 * cfg.time_step_s * (previous_exchange + exchange_rate)
        previous_reaction, previous_exchange = reaction_rate, exchange_rate
        for i, (feed_i, state_i) in enumerate(zip(feed, state)):
            cumulative_in[i] += cfg.time_step_s * cfg.flow_rate_s * feed_i
            cumulative_out[i] += cfg.time_step_s * cfg.flow_rate_s * state_i
        state = _rk4(state, cfg.time_step_s, cfg)
        if (step + 1) % sample_stride == 0 or step == n - 1:
            times.append((step + 1) * cfg.time_step_s)
            trajectory.append(state.copy())

    # The initial half-step is included explicitly in the trapezoid integral.
    sr0 = sum(_reaction_terms(initial, cfg)[2])
    se0 = sum(_exchange_terms(initial, cfg)[1])
    reaction_integral += 0.5 * cfg.time_step_s * sr0
    exchange_integral += 0.5 * cfg.time_step_s * se0
    c0 = cfg.standard_concentration_mol_L
    window_start = max(0, int(len(trajectory) * (1.0 - cfg.ness_window_fraction)) - 1)
    window = trajectory[window_start:]
    start_state, end_state = window[0], window[-1]
    drift = max(abs(end - start) / max(abs(end), abs(start), 1.0e-12)
                for start, end in zip(start_state, end_state))
    means = [sum(row[i] for row in window) / len(window) for i in range(len(SPECIES))]
    cvs = []
    for i, mean in enumerate(means):
        variance = sum((row[i] - mean) ** 2 for row in window) / len(window)
        cvs.append(math.sqrt(variance) / max(abs(mean), 1.0e-12))
    max_cv = max(cvs)
    ness = drift <= cfg.ness_tolerance and max_cv <= cfg.ness_tolerance
    final_v, final_dg, final_sr = _reaction_terms(state, cfg)
    final_exchange, final_se = _exchange_terms(state, cfg)

    return {
        "model": "continuously_driven_mutually_catalytic_cstr",
        "configuration": asdict(cfg),
        "species_order": list(SPECIES),
        "feed_activities": dict(zip(SPECIES, feed)),
        "initial": dict(zip(SPECIES, initial)),
        "final": dict(zip(SPECIES, state)),
        "window_mean": dict(zip(SPECIES, means)),
        "reaction_fluxes_mol_L_s": dict(zip(["R1", "R2", "R3", "R4"], final_v)),
        "reaction_gibbs_energies_J_mol": dict(zip(["R1", "R2", "R3", "R4"], final_dg)),
        "reservoir_exchange_fluxes_activity_s": dict(zip(SPECIES, final_exchange)),
        "diagnostics": {
            "ness_detected": ness,
            "ness_window_fraction": cfg.ness_window_fraction,
            "ness_relative_endpoint_drift": drift,
            "ness_max_species_coefficient_of_variation": max_cv,
            "final_reaction_entropy_production_J_L_K_s": sum(final_sr) * c0,
            "final_reservoir_exchange_entropy_production_J_L_K_s": sum(final_se) * c0,
            "final_total_entropy_production_J_L_K_s": (sum(final_sr) + sum(final_se)) * c0,
            "integrated_reaction_entropy_production_J_L_K": reaction_integral * c0,
            "integrated_reservoir_exchange_entropy_production_J_L_K": exchange_integral * c0,
            "minimum_reaction_entropy_production_contribution": reaction_sigma_min * c0,
            "minimum_exchange_entropy_production_contribution": exchange_sigma_min * c0,
            "max_species_window_cv": max_cv,
            "cumulative_feed_activity": dict(zip(SPECIES, cumulative_in)),
            "cumulative_outflow_activity": dict(zip(SPECIES, cumulative_out)),
        },
        "accounting": {
            "reaction_boundary": "Ideal reversible reaction network inside a well-mixed reactor.",
            "exchange_boundary": "Each species exchanges with a finite-activity reservoir at the declared dilution rate. Exchange entropy production is sum_i J_i*(mu_feed_i-mu_reactor_i)/T.",
            "not_included": [
                "Mechanical pumping and mixing work.",
                "The physical construction, regeneration and maintenance of feed/product reservoirs.",
                "Heat-exchanger and temperature-control costs.",
                "Spatial transport, gradients and reactor-wall effects.",
            ],
            "warning": "Reaction and reservoir-exchange entropy production are reported separately. The exchange term is not a complete engineering cost of maintaining the reactor or its reservoirs.",
        },
        "limitations": [
            "All species are abstract and use ideal dimensionless activities; no prebiotic chemistry is identified.",
            "All species have small positive feed activities, including X and Y. This explicit background feed prevents singular reservoir chemical potentials but also supplies a continuous seed; the model does not demonstrate seed-free emergence.",
            "The well-mixed CSTR uses a single dilution rate and does not model selective retention or spatial compartments.",
            "A finite simulation window classified as NESS is an operational numerical criterion, not proof of a unique globally stable steady state.",
            "Catalysis multiplies forward and reverse rates equally and does not change reaction equilibrium constants.",
            "No replication with heredity, mutation, Darwinian evolution or life is represented.",
        ],
        "time_series": {
            "time_s": times,
            "species_activities": [dict(zip(SPECIES, row)) for row in trajectory],
        },
    }


def compare_open_reactor(config: OpenReactorConfig | None = None) -> dict[str, Any]:
    """Compare driven mutual catalysis against the same-flow uncatalysed null."""
    cfg = config or OpenReactorConfig()
    catalytic = simulate_open_reactor(cfg)
    null_cfg = OpenReactorConfig(**{**asdict(cfg), "catalytic_strength": 0.0})
    null = simulate_open_reactor(null_cfg)
    return {
        "catalytic_strength": cfg.catalytic_strength,
        "catalytic": catalytic,
        "uncatalysed_null": null,
        "comparison": {
            "catalytic_X_plus_Y": catalytic["final"]["X"] + catalytic["final"]["Y"],
            "uncatalysed_X_plus_Y": null["final"]["X"] + null["final"]["Y"],
            "X_plus_Y_ratio": ((catalytic["final"]["X"] + catalytic["final"]["Y"]) /
                               (null["final"]["X"] + null["final"]["Y"])),
            "catalytic_ness": catalytic["diagnostics"]["ness_detected"],
            "uncatalysed_ness": null["diagnostics"]["ness_detected"],
        },
        "interpretation": "This is a matched-flow comparison. It tests whether reciprocal catalysis changes steady-state abundance under the same feed composition and dilution. It does not test spontaneous emergence because the feed contains small positive X and Y activities.",
    }


def run_open_reactor_sweep(
    base: OpenReactorConfig | None = None,
    *,
    catalytic_strengths: tuple[float, ...] = (0.0, 1.0, 10.0, 100.0),
    flow_rates_s: tuple[float, ...] = (0.01, 0.05, 0.1),
) -> list[dict[str, float | bool]]:
    """Cross catalytic strength with dilution rate at otherwise matched settings."""
    cfg = base or OpenReactorConfig()
    rows = []
    for flow in flow_rates_s:
        for strength in catalytic_strengths:
            run = simulate_open_reactor(OpenReactorConfig(**{
                **asdict(cfg), "flow_rate_s": flow, "catalytic_strength": strength
            }))
            d = run["diagnostics"]
            rows.append({
                "flow_rate_s": flow,
                "catalytic_strength": strength,
                "final_X_plus_Y": run["final"]["X"] + run["final"]["Y"],
                "ness_detected": d["ness_detected"],
                "ness_relative_endpoint_drift": d["ness_relative_endpoint_drift"],
                "reaction_entropy_production_J_L_K_s": d["final_reaction_entropy_production_J_L_K_s"],
                "exchange_entropy_production_J_L_K_s": d["final_reservoir_exchange_entropy_production_J_L_K_s"],
            })
    return rows



def simulate_open_reactor_perturbation(
    config: OpenReactorConfig | None = None,
    *,
    perturbation_time_s: float = 150.0,
    removal_fraction: float = 0.99,
    post_perturbation_catalyst_feed_activity: float | None = None,
    recovery_threshold_fraction: float = 0.9,
) -> dict[str, Any]:
    """Remove X and Y from an established open reactor and measure recovery."""
    cfg = config or OpenReactorConfig()
    cfg.validate()
    if not math.isfinite(perturbation_time_s) or not 0 < perturbation_time_s < cfg.duration_s:
        raise ValueError("perturbation_time_s must lie strictly between zero and duration_s")
    if not math.isfinite(removal_fraction) or not 0 <= removal_fraction < 1:
        raise ValueError("removal_fraction must be finite and in [0, 1)")
    if (post_perturbation_catalyst_feed_activity is not None and
            (not math.isfinite(post_perturbation_catalyst_feed_activity) or
             post_perturbation_catalyst_feed_activity <= 0)):
        raise ValueError("post_perturbation_catalyst_feed_activity must be finite and positive")
    if (not math.isfinite(recovery_threshold_fraction) or
            not 0 < recovery_threshold_fraction <= 1):
        raise ValueError("recovery_threshold_fraction must be in (0, 1]")
    steps = perturbation_time_s / cfg.time_step_s
    if abs(steps - round(steps)) > 1e-9:
        raise ValueError("perturbation_time_s must be an integer multiple of time_step_s")

    before_cfg = OpenReactorConfig(**{**asdict(cfg), "duration_s": perturbation_time_s})
    before = simulate_open_reactor(before_cfg)
    pre = before["final"]
    post = dict(pre)
    post["X"] *= (1.0 - removal_fraction)
    post["Y"] *= (1.0 - removal_fraction)
    post_state = [post[name] for name in SPECIES]
    post_feed = (cfg.catalyst_feed_activity if post_perturbation_catalyst_feed_activity is None
                 else post_perturbation_catalyst_feed_activity)
    after_cfg = OpenReactorConfig(**{
        **asdict(cfg),
        "duration_s": cfg.duration_s - perturbation_time_s,
        "catalyst_feed_activity": post_feed,
    })
    after = simulate_open_reactor(after_cfg, initial_state=post_state)
    baseline = simulate_open_reactor(cfg)

    pre_xy = pre["X"] + pre["Y"]
    post_xy = post["X"] + post["Y"]
    final_xy = after["final"]["X"] + after["final"]["Y"]
    baseline_xy = baseline["final"]["X"] + baseline["final"]["Y"]
    removed_xy = pre_xy - post_xy
    recovery_fraction = (final_xy - post_xy) / removed_xy if removed_xy > 0 else 0.0
    threshold = recovery_threshold_fraction * pre_xy
    recovery_time = None
    for time_s, row in zip(after["time_series"]["time_s"],
                           after["time_series"]["species_activities"]):
        if row["X"] + row["Y"] >= threshold:
            recovery_time = time_s
            break

    return {
        "model": "continuously_driven_mutual_catalysis_perturbation",
        "configuration": asdict(cfg),
        "perturbation_time_s": perturbation_time_s,
        "removal_fraction": removal_fraction,
        "post_perturbation_catalyst_feed_activity": post_feed,
        "pre_perturbation": pre,
        "immediately_post_perturbation": post,
        "final_after_perturbation": after["final"],
        "unperturbed_final": baseline["final"],
        "diagnostics": {
            "X_plus_Y_before": pre_xy,
            "X_plus_Y_immediately_after": post_xy,
            "X_plus_Y_final": final_xy,
            "X_plus_Y_unperturbed_final": baseline_xy,
            "fraction_of_removed_XY_recovered": recovery_fraction,
            "fraction_of_preperturbation_XY_restored": final_xy / pre_xy if pre_xy else 0.0,
            "final_XY_relative_to_unperturbed": final_xy / baseline_xy if baseline_xy else 0.0,
            "recovery_threshold_fraction": recovery_threshold_fraction,
            "recovery_threshold_X_plus_Y": threshold,
            "recovery_time_after_perturbation_s": recovery_time,
            "post_perturbation_operational_ness_detected": after["diagnostics"]["ness_detected"],
            "post_perturbation_ness_relative_endpoint_drift": after["diagnostics"]["ness_relative_endpoint_drift"],
            "post_perturbation_ness_max_species_cv": after["diagnostics"]["ness_max_species_coefficient_of_variation"],
            "post_perturbation_reaction_entropy_production_J_L_K_s": after["diagnostics"]["final_reaction_entropy_production_J_L_K_s"],
            "post_perturbation_exchange_entropy_production_J_L_K_s": after["diagnostics"]["final_reservoir_exchange_entropy_production_J_L_K_s"],
        },
        "interpretation": "The intervention physically removes a fraction of X and Y while continuous feed and dilution continue. The post-event feed of X and Y can be varied independently of the pre-event history. Removal/separation work is not modelled.",
        "limitations": [
            "The network remains abstract and is continuously seeded by its catalyst feed reservoir.",
            "The removal operation and its energetic cost are not modelled.",
            "Recovery depends on the finite observation horizon, feed chemical potentials, dilution and surviving catalyst abundance.",
            "Returning to the operational NESS window does not establish biological self-repair, replication or evolution.",
        ],
    }


def run_open_reactor_recovery_sweep(
    base: OpenReactorConfig | None = None,
    *,
    removal_fractions: tuple[float, ...] = (0.9, 0.99, 0.999),
    post_catalyst_feed_activities: tuple[float, ...] = (1.0e-8, 1.0e-6, 1.0e-4),
    perturbation_time_s: float = 150.0,
) -> list[dict[str, float | bool | None]]:
    """Sweep catalyst removal against post-event catalyst reservoir feed."""
    cfg = base or OpenReactorConfig()
    rows = []
    for feed in post_catalyst_feed_activities:
        for removal in removal_fractions:
            result = simulate_open_reactor_perturbation(
                cfg,
                perturbation_time_s=perturbation_time_s,
                removal_fraction=removal,
                post_perturbation_catalyst_feed_activity=feed,
            )
            d = result["diagnostics"]
            rows.append({
                "removal_fraction": removal,
                "post_perturbation_catalyst_feed_activity": feed,
                "fraction_of_removed_XY_recovered": d["fraction_of_removed_XY_recovered"],
                "fraction_of_preperturbation_XY_restored": d["fraction_of_preperturbation_XY_restored"],
                "final_XY_relative_to_unperturbed": d["final_XY_relative_to_unperturbed"],
                "recovery_time_after_perturbation_s": d["recovery_time_after_perturbation_s"],
                "post_perturbation_operational_ness_detected": d["post_perturbation_operational_ness_detected"],
            })
    return rows
