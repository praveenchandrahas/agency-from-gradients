"""The v0.2 planet model, instrumented.

`v0_2.py` is the published source, copied in unchanged. This file runs the same
rules and adds three things the paper did not have:

1. Mixed populations. Each entity carries a heritable flag: agency carrier or
   not. Carriers follow the cognition-enabled rules. Non-carriers follow the
   cognition-disabled rules. Both live on the same planet and compete.
2. Neutral markers. Five extra numbers per entity. They start like the five
   agency traits, mutate like them, clip like them, cost nothing and do nothing.
3. Demography. Births, deaths, crowding and the spread of net energy, every
   generation.

With every option at its default, `run` gives the same numbers as
`v0_2.run_one`, bit for bit. The tests check that. The extras draw their random
numbers from a second stream, so they cannot disturb the first.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import math

import numpy as np
import pandas as pd

from . import v0_2 as base

TI = base.TRAIT_INDEX
AGENCY = slice(1, 6)  # sensing, processing, prediction, planning, action

# Environment groups, exactly as in v0_2.run_one. Paired scenarios share weather.
ENV_GROUP = {
    "weakly_variable": 0,
    "predictable_seasonal": 1,
    "volatile_shifting": 2,
    "volatile_no_cognition": 2,
    "strong_predictable_hotspots": 3,
    "strong_predictable_no_cognition": 3,
}

# The four environments, named by their cognition-enabled scenario key.
ENVIRONMENTS = {
    "weak": "weakly_variable",
    "seasonal": "predictable_seasonal",
    "volatile": "volatile_shifting",
    "strong": "strong_predictable_hotspots",
}

# Neutral markers start with the same means and spread as the five agency traits.
MARKER_MEANS = np.array([0.08, 0.07, 0.06, 0.05, 0.08])
MARKER_INIT_SD = 0.045

NET_EDGES = np.round(np.arange(-0.70, 8.0001, 0.05), 2)
QUANTILES = (1, 5, 10, 25, 50, 75, 90, 95, 99)


@dataclass(frozen=True)
class Options:
    """What to switch on, beyond the published model."""

    # None: a pure population, as published. A number: a mixed population that
    # starts with this fraction of agency carriers.
    carrier_fraction: float | None = None
    # Equation 4 of the paper: the stipulated capacity bonus for agency traits.
    eq4_bonus: bool = True
    # The modelled behaviour: carriers move to the best-scored neighbouring patch.
    directed_movement: bool = True
    # Generations at which to keep a histogram of net energy and patch counts.
    snapshot_generations: tuple[int, ...] = ()

    @property
    def published(self) -> bool:
        return self.carrier_fraction is None and self.eq4_bonus and self.directed_movement


def _streams(config: base.Config, scenario_key: str, replicate: int, opt: Options):
    """Three random streams: weather, biology, extras."""
    scenario_index = list(base.SCENARIOS).index(scenario_key)
    group = ENV_GROUP[scenario_key]
    env_rng = np.random.default_rng(config.seed + 100_003 * replicate + 7_919 * group)
    frac_code = 2000 if opt.carrier_fraction is None else int(round(1000 * opt.carrier_fraction))
    arm = [config.seed, replicate, scenario_index, frac_code, int(opt.eq4_bonus), int(opt.directed_movement)]
    if opt.published:
        rng = np.random.default_rng(config.seed + 100_003 * replicate + 1_009 * scenario_index)
    else:
        rng = np.random.default_rng(arm)
    aux = np.random.default_rng(arm + [424_242])
    return env_rng, rng, aux


def _mean(x: np.ndarray) -> float:
    return float(np.mean(x)) if len(x) else float("nan")


def run(
    scenario_key: str,
    replicate: int,
    config: base.Config,
    world: dict[str, Any],
    opt: Options = Options(),
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """One run. Returns one row per generation, and the requested snapshots."""
    scenario = base.SCENARIOS[scenario_key]
    if opt.carrier_fraction is not None and not scenario["cognition_enabled"]:
        raise ValueError("mixed runs are named by the cognition-enabled scenario of their environment")
    env_rng, rng, aux = _streams(config, scenario_key, replicate, opt)

    # Same draws as v0_2.initialize_population. Carrier status is decided afterwards.
    traits, locations = base.initialize_population(rng, config, world, True)
    n0 = len(traits)
    if opt.carrier_fraction is None:
        carrier = np.full(n0, bool(scenario["cognition_enabled"]))
    else:
        carrier = np.zeros(n0, dtype=bool)
        carrier[aux.permutation(n0)[: int(round(opt.carrier_fraction * n0))]] = True
    traits[~carrier, AGENCY] = 0.0
    markers = np.clip(aux.normal(MARKER_MEANS, MARKER_INIT_SD, size=(n0, 5)), 0.0, 1.0)

    n_cells = world["cells"]
    base_albedo = world["base_albedo"]
    neighbours = world["neighbours"]
    infrastructure = np.zeros(n_cells, dtype=float)
    weather = np.zeros(world["shape"], dtype=float)
    costs = np.asarray(config.trait_costs, dtype=float)
    rows: list[dict[str, Any]] = []
    snaps: list[dict[str, Any]] = []

    for generation in range(config.generations + 1):
        start_locations = locations.copy()
        fresh = base.smooth_field(env_rng.normal(0.0, scenario["weather_sigma"], size=world["shape"]))
        weather = scenario["weather_persistence"] * weather + math.sqrt(
            max(0.0, 1.0 - scenario["weather_persistence"] ** 2)
        ) * fresh
        # v0_2 draws next-step weather here and uses it only for a field it never reads.
        # The draw is kept, so the weather history stays identical.
        env_rng.normal(0.0, scenario["weather_sigma"], size=world["shape"])
        flux_now = base.seasonal_irradiance(generation, weather, scenario, world, config.stellar_flux_multiplier)
        forecast_weather = scenario["weather_persistence"] * weather
        flux_forecast = base.seasonal_irradiance(
            generation + 1, forecast_weather, scenario, world, config.stellar_flux_multiplier
        )
        current_field = flux_now * (1.0 - base_albedo)
        forecast_field = flux_forecast * (1.0 - base_albedo)

        # --- movement ---------------------------------------------------------
        idx_c = np.flatnonzero(carrier)
        idx_n = np.flatnonzero(~carrier)
        choice_true_best = float("nan")
        if len(idx_c) and opt.directed_movement:
            loc_c = locations[idx_c]
            cand = neighbours[loc_c]
            t = traits[idx_c]
            sensing, processing = t[:, TI["sensing"]], t[:, TI["processing"]]
            prediction, planning, action = t[:, TI["prediction"]], t[:, TI["planning"]], t[:, TI["action"]]
            obs_sigma = config.sensing_noise * (1.0 - sensing * processing) + 0.012
            pred_sigma = config.prediction_noise * (1.0 - prediction * processing) + 0.012
            current_obs = current_field[cand] + rng.normal(0.0, obs_sigma[:, None], size=cand.shape)
            future_obs = forecast_field[cand] + rng.normal(0.0, pred_sigma[:, None], size=cand.shape)
            future_weight = config.planning_horizon_weight * planning * prediction
            scores = (1.0 - future_weight[:, None]) * current_obs + future_weight[:, None] * future_obs
            best = np.argmax(scores, axis=1)
            proposed = cand[np.arange(len(loc_c)), best]
            move_probability = np.clip(config.baseline_move_probability + 0.92 * action, 0.0, 0.95)
            move = rng.random(len(loc_c)) < move_probability
            new_loc = np.where(move, proposed, loc_c)
            if len(idx_n) == 0:
                locations = new_loc
            else:
                locations[idx_c] = new_loc
            # How often does the noisy choice equal the truly best neighbour?
            truly_best = cand[np.arange(len(loc_c)), np.argmax(current_field[cand], axis=1)]
            choice_true_best = float(np.mean(proposed == truly_best))
            idx_random = idx_n
        else:
            idx_random = np.arange(len(locations)) if not opt.directed_movement else idx_n
        if len(idx_random) or len(traits) == 0:
            move = rng.random(len(idx_random)) < config.baseline_move_probability
            if np.any(move):
                choices = rng.integers(0, 9, size=int(np.sum(move)))
                who = idx_random[move]
                locations[who] = neighbours[locations[who], choices]

        if len(traits) == 0:
            break

        # --- harvest ----------------------------------------------------------
        coop = traits[:, TI["cooperation"]]
        tech = traits[:, TI["technology"]]
        collector = traits[:, TI["collector"]]
        action_all = traits[:, TI["action"]]
        local_count = np.bincount(locations, minlength=n_cells).astype(float)
        local_coop_sum = np.bincount(locations, weights=coop, minlength=n_cells)
        local_coop_mean = np.divide(
            local_coop_sum, local_count, out=np.zeros_like(local_coop_sum), where=local_count > 0
        )
        local_coop = local_coop_mean[locations]
        collector_area = 0.18 + 1.55 * collector
        tech_multiplier = 1.0 + config.technology_capacity_gain * tech * local_coop
        coop_multiplier = 1.0 + config.cooperation_capacity_gain * coop * local_coop
        infra_multiplier = 1.0 + config.infrastructure_capacity_gain * infrastructure[locations]

        spatial_opportunity = float(np.std(flux_now) / max(np.mean(flux_now), 1e-12))
        temporal_opportunity = float(scenario["seasonal_amplitude"] + 1.5 * scenario["weather_sigma"])
        forecastability = 0.30 + 0.70 * scenario["weather_persistence"]
        behaviour_gain = (
            0.35 * spatial_opportunity * 0.5 * (traits[:, 1] + traits[:, 2])
            + 0.30 * temporal_opportunity * forecastability * 0.5 * (traits[:, 3] + traits[:, 4])
            + 0.22 * (spatial_opportunity + temporal_opportunity) * traits[:, 5]
        )
        if not opt.eq4_bonus:
            behaviour_gain = np.zeros_like(behaviour_gain)
        behaviour_multiplier = 1.0 + behaviour_gain
        capacity = collector_area * tech_multiplier * coop_multiplier * infra_multiplier * behaviour_multiplier
        capacity = np.clip(capacity, 0.02, 8.0)
        capacity_by_patch = np.bincount(locations, weights=capacity, minlength=n_cells)
        area_by_patch = np.bincount(locations, weights=collector_area, minlength=n_cells)

        cover = 1.0 - np.exp(-config.cover_sensitivity * area_by_patch)
        albedo = np.clip(base_albedo - config.max_biotic_albedo_reduction * cover, 0.035, 0.90)
        albedo_abiotic = base_albedo
        patch_area = world["patch_area"]
        absorbed_power_cell = flux_now * patch_area * (1.0 - albedo)
        absorbed_power_abiotic_cell = flux_now * patch_area * (1.0 - albedo_abiotic)
        absorbed_power = float(np.sum(absorbed_power_cell))
        absorbed_power_abiotic = float(np.sum(absorbed_power_abiotic_cell))

        resource_units = (
            absorbed_power_cell
            * config.generation_seconds
            * config.baseline_resource_efficiency
            / config.resource_unit_joules
        )
        capture_fraction_patch = 1.0 - np.exp(-config.capture_sensitivity * capacity_by_patch)
        harvested_units_patch = resource_units * capture_fraction_patch
        total_harvested_units = float(np.sum(harvested_units_patch))
        local_captured = harvested_units_patch[locations]
        local_capacity_total = capacity_by_patch[locations]
        gross_energy = np.divide(
            local_captured * capacity,
            local_capacity_total,
            out=np.zeros_like(capacity),
            where=local_capacity_total > 0,
        )

        maintenance = config.baseline_metabolic_cost + np.sum((traits**2) * costs[None, :], axis=1)
        maintenance += 0.012 * np.maximum(0.0, action_all)  # movement wear; zero for non-carriers
        net_energy = gross_energy - maintenance

        invest_weight = np.maximum(net_energy, 0.0) * coop * tech
        investment_by_patch = np.bincount(locations, weights=invest_weight, minlength=n_cells)
        infrastructure = np.clip(
            (1.0 - config.infrastructure_decay) * infrastructure
            + config.infrastructure_build_rate * investment_by_patch,
            0.0,
            config.max_infrastructure,
        )

        # --- survival and births ---------------------------------------------
        survival_probability = config.survival_base + config.survival_gain * base.sigmoid(
            config.survival_slope * (net_energy - config.survival_threshold)
        )
        survival_probability = np.clip(survival_probability, 0.02, 0.995)
        survived_mask = rng.random(len(traits)) < survival_probability
        mean_net_energy = float(np.mean(net_energy))
        birth_rate_per_entity = config.birth_rate_base + config.birth_rate_gain * float(
            base.sigmoid(config.birth_rate_slope * (mean_net_energy - config.birth_energy_threshold))
        )
        n_births = int(rng.poisson(len(traits) * birth_rate_per_entity))

        # --- the published metrics, unchanged ---------------------------------
        rad_biotic = base.radiative_entropy_production(
            float(np.average(albedo, weights=flux_now)), config.stellar_flux_multiplier
        )
        rad_abiotic = base.radiative_entropy_production(
            float(np.average(albedo_abiotic, weights=flux_now)), config.stellar_flux_multiplier
        )
        bio_power = total_harvested_units * config.resource_unit_joules / config.generation_seconds
        potential_bio_power = float(np.sum(resource_units)) * config.resource_unit_joules / config.generation_seconds
        moved_fraction = float(np.mean(locations != start_locations)) if generation > 0 else 0.0
        pure_cognition = opt.carrier_fraction is None and bool(scenario["cognition_enabled"])
        if opt.carrier_fraction is None:
            cognitive_mean = float(np.mean(np.mean(traits[:, AGENCY], axis=1))) if pure_cognition else 0.0
        else:
            cognitive_mean = _mean(np.mean(traits[carrier][:, AGENCY], axis=1))
        gross_sorted = np.sort(np.maximum(gross_energy, 0.0))
        top_n = max(1, int(math.ceil(0.10 * len(gross_sorted))))
        top10_energy_share = float(np.sum(gross_sorted[-top_n:]) / max(np.sum(gross_sorted), 1e-12))
        survival_mean = float(np.mean(survival_probability))
        occupied_patches = int(np.count_nonzero(local_count))
        n = len(traits)
        row: dict[str, Any] = {
            "scenario_key": scenario_key,
            "scenario": scenario["label"],
            "replicate": replicate,
            "generation": generation,
            "population": n,
            "mean_gross_energy_units": float(np.mean(gross_energy)),
            "mean_maintenance_units": float(np.mean(maintenance)),
            "mean_net_energy_units": float(np.mean(net_energy)),
            "net_energy_p10": float(np.percentile(net_energy, 10)),
            "net_energy_p50": float(np.percentile(net_energy, 50)),
            "net_energy_p90": float(np.percentile(net_energy, 90)),
            "gross_energy_gini": base.gini_coefficient(gross_energy),
            "top10_gross_energy_share": top10_energy_share,
            "mean_survival_probability": survival_mean,
            "birth_rate_per_entity": float(birth_rate_per_entity),
            "occupied_patch_fraction": float(occupied_patches / n_cells),
            "mean_entities_per_occupied_patch": float(n / max(occupied_patches, 1)),
            "total_biotic_harvest_units": total_harvested_units,
            "potential_biotic_resource_units": float(np.sum(resource_units)),
            "biotic_capture_fraction_of_photo_pool": float(
                total_harvested_units / max(float(np.sum(resource_units)), 1e-12)
            ),
            "biotic_power_harnessed_W": float(bio_power),
            "biotic_power_harnessed_TW": float(bio_power / 1e12),
            "biotic_power_per_entity_GW": float(bio_power / max(n, 1) / 1e9),
            "biotic_kardashev_equivalent": float((np.log10(max(bio_power, 1.0)) - 6.0) / 10.0),
            "biotic_power_as_fraction_of_absorbed": float(bio_power / max(absorbed_power, 1.0)),
            "potential_biotic_power_TW": float(potential_bio_power / 1e12),
            "abiotic_absorbed_power_W": absorbed_power_abiotic,
            "biotic_absorbed_power_W": absorbed_power,
            "extra_absorbed_power_vs_abiotic_W": absorbed_power - absorbed_power_abiotic,
            "global_albedo_biotic": rad_biotic["global_albedo"],
            "global_albedo_abiotic": rad_abiotic["global_albedo"],
            "radiative_entropy_production_biotic_W_K": rad_biotic["radiative_entropy_production_W_K"],
            "radiative_entropy_production_abiotic_W_K": rad_abiotic["radiative_entropy_production_W_K"],
            "delta_radiative_entropy_production_W_K": (
                rad_biotic["radiative_entropy_production_W_K"] - rad_abiotic["radiative_entropy_production_W_K"]
            ),
            "delta_radiative_entropy_percent": 100.0
            * (
                rad_biotic["radiative_entropy_production_W_K"]
                / max(rad_abiotic["radiative_entropy_production_W_K"], 1e-12)
                - 1.0
            ),
            "mean_collector": float(np.mean(traits[:, 0])),
            "mean_sensing": float(np.mean(traits[:, 1])),
            "mean_processing": float(np.mean(traits[:, 2])),
            "mean_prediction": float(np.mean(traits[:, 3])),
            "mean_planning": float(np.mean(traits[:, 4])),
            "mean_action": float(np.mean(traits[:, 5])),
            "mean_agency_composite": cognitive_mean,
            "mean_cooperation": float(np.mean(traits[:, 6])),
            "mean_technology": float(np.mean(traits[:, 7])),
            "mean_infrastructure": float(np.mean(infrastructure)),
            "mean_local_cover": float(np.mean(cover)),
            "mean_behaviour_gain": float(np.mean(behaviour_gain)),
            "mean_mobility_fraction": moved_fraction,
        }

        # --- the additions ----------------------------------------------------
        own_count = local_count[locations]                      # entities sharing my patch, me included
        survivors = int(np.sum(survived_mask))
        surv_at_mean = float(
            np.clip(
                config.survival_base
                + config.survival_gain
                * base.sigmoid(config.survival_slope * (mean_net_energy - config.survival_threshold)),
                0.02,
                0.995,
            )
        )
        is_peak = current_field >= np.max(current_field[neighbours], axis=1)   # local maximum of the scored field
        counts_sorted = np.sort(local_count)[::-1]
        top5pc = max(1, int(round(0.05 * n_cells)))
        row.update(
            {
                "survivors": survivors,
                "survivors_c": int(np.sum(survived_mask & carrier)),
                "births": n_births,
                "growth_realized": (survivors + n_births) / n,
                "growth_expected": survival_mean + birth_rate_per_entity,
                "survival_at_mean_net": surv_at_mean,
                "growth_meanfield": surv_at_mean + birth_rate_per_entity,
                "frac_net_below_threshold": float(np.mean(net_energy < config.survival_threshold)),
                "frac_net_negative": float(np.mean(net_energy < 0.0)),
                "crowding_entity_weighted": float(np.mean(own_count)),
                "crowding_median": float(np.median(own_count)),
                "max_patch_count": float(counts_sorted[0]),
                "pop_share_top5pc_patches": float(np.sum(counts_sorted[:top5pc]) / n),
                "resource_share_occupied": float(
                    np.sum(resource_units[local_count > 0]) / max(float(np.sum(resource_units)), 1e-12)
                ),
                "n_peak_patches": int(np.sum(is_peak)),
                "frac_on_peak": float(np.mean(is_peak[locations])),
                "choice_true_best": choice_true_best,
                "spatial_opportunity_cv": spatial_opportunity,
                "n_carriers": int(np.sum(carrier)),
                "carrier_fraction": float(np.mean(carrier)),
                "marker_composite": float(np.mean(markers)),
            }
        )
        for q in QUANTILES:
            row[f"net_q{q:02d}"] = float(np.percentile(net_energy, q))
        for k in range(5):
            row[f"marker_{k + 1}"] = float(np.mean(markers[:, k]))
        for tag, mask in (("c", carrier), ("n", ~carrier)):
            row[f"net_mean_{tag}"] = _mean(net_energy[mask])
            row[f"gross_mean_{tag}"] = _mean(gross_energy[mask])
            row[f"survival_mean_{tag}"] = _mean(survival_probability[mask])
            row[f"crowding_{tag}"] = _mean(own_count[mask])
            row[f"frac_on_peak_{tag}"] = _mean(is_peak[locations[mask]].astype(float))
            row[f"occupied_fraction_{tag}"] = float(len(np.unique(locations[mask])) / n_cells)
            row[f"harvest_units_{tag}"] = float(np.sum(gross_energy[mask]))
            row[f"collector_{tag}"] = _mean(collector[mask])
            row[f"cooperation_{tag}"] = _mean(coop[mask])
            row[f"technology_{tag}"] = _mean(tech[mask])
            row[f"marker_composite_{tag}"] = _mean(np.mean(markers[mask], axis=1))
            row[f"births_{tag}"] = float("nan")
        row["action_c"] = _mean(action_all[carrier])
        rows.append(row)

        if generation in opt.snapshot_generations:
            snap = {
                "generation": generation,
                "net_hist": np.histogram(np.clip(net_energy, NET_EDGES[0], NET_EDGES[-1] - 1e-9), bins=NET_EDGES)[0],
                "net_hist_c": np.histogram(
                    np.clip(net_energy[carrier], NET_EDGES[0], NET_EDGES[-1] - 1e-9), bins=NET_EDGES
                )[0],
                "patch_count": local_count.copy(),
                "patch_count_c": np.bincount(locations[carrier], minlength=n_cells).astype(float),
                "patch_field": current_field.copy(),
                "patch_resource": resource_units.copy(),
                "patch_capture_fraction": capture_fraction_patch.copy(),
                "patch_is_peak": is_peak.copy(),
            }
            snaps.append(snap)

        if generation == config.generations:
            break

        # --- reproduction -----------------------------------------------------
        survivor_traits = traits[survived_mask]
        survivor_locations = locations[survived_mask]
        if n_births:
            log_weights = config.selection_strength * (net_energy - float(np.mean(net_energy)))
            log_weights -= float(np.max(log_weights))
            parent_weights = np.exp(np.clip(log_weights, -40.0, 0.0))
            parent_weights /= np.sum(parent_weights)
            parent_ids = rng.choice(len(traits), size=n_births, replace=True, p=parent_weights)
            parent_carrier = carrier[parent_ids]
            # Same draws as v0_2.mutate_offspring.
            child_traits = traits[parent_ids] + rng.normal(0.0, config.mutation_sd, size=(n_births, traits.shape[1]))
            child_traits = np.clip(child_traits, 0.0, 1.0)
            innovation = rng.random(n_births) < config.tech_innovation_probability
            if np.any(innovation):
                child_traits[innovation, TI["technology"]] = np.clip(
                    child_traits[innovation, TI["technology"]] + config.tech_innovation_step, 0.0, 1.0
                )
            child_traits[~parent_carrier, AGENCY] = 0.0
            child_locations = locations[parent_ids].copy()
            disperse_prob = np.clip(
                config.dispersal_base + config.dispersal_action_gain * traits[parent_ids, TI["action"]], 0.0, 0.60
            )
            disperse = rng.random(len(parent_ids)) < disperse_prob
            if np.any(disperse):
                move_choice = rng.integers(0, 9, size=int(np.sum(disperse)))
                child_locations[disperse] = neighbours[child_locations[disperse], move_choice]
            # Markers: same mutation size, same clipping, second random stream.
            child_markers = np.clip(
                markers[parent_ids] + aux.normal(0.0, config.mutation_sd, size=(n_births, 5)), 0.0, 1.0
            )
            row["births_c"] = float(np.sum(parent_carrier))
            row["births_n"] = float(n_births - np.sum(parent_carrier))
            source_net = np.concatenate([net_energy[survived_mask], net_energy[parent_ids]])
            traits = np.vstack([survivor_traits, child_traits])
            locations = np.concatenate([survivor_locations, child_locations]).astype(np.int32)
            carrier = np.concatenate([carrier[survived_mask], parent_carrier])
            markers = np.vstack([markers[survived_mask], child_markers])
        else:
            row["births_c"] = 0.0
            row["births_n"] = 0.0
            source_net = net_energy[survived_mask].copy()
            traits = survivor_traits.copy()
            locations = survivor_locations.copy()
            carrier = carrier[survived_mask]
            markers = markers[survived_mask]

        if len(traits) == 0:
            break

        if len(traits) > config.max_population:
            weights = np.exp(np.clip(config.selection_strength * (source_net - np.max(source_net)), -30, 0))
            probs = weights / np.sum(weights)
            keep = rng.choice(len(traits), size=config.max_population, replace=False, p=probs)
            traits, locations, carrier, markers = traits[keep], locations[keep], carrier[keep], markers[keep]

    return pd.DataFrame(rows), snaps


PUBLISHED_COLUMNS = [
    "scenario_key", "scenario", "replicate", "generation", "population", "mean_gross_energy_units",
    "mean_maintenance_units", "mean_net_energy_units", "net_energy_p10", "net_energy_p50", "net_energy_p90",
    "gross_energy_gini", "top10_gross_energy_share", "mean_survival_probability", "birth_rate_per_entity",
    "occupied_patch_fraction", "mean_entities_per_occupied_patch", "total_biotic_harvest_units",
    "potential_biotic_resource_units", "biotic_capture_fraction_of_photo_pool", "biotic_power_harnessed_W",
    "biotic_power_harnessed_TW", "biotic_power_per_entity_GW", "biotic_kardashev_equivalent",
    "biotic_power_as_fraction_of_absorbed", "potential_biotic_power_TW", "abiotic_absorbed_power_W",
    "biotic_absorbed_power_W", "extra_absorbed_power_vs_abiotic_W", "global_albedo_biotic",
    "global_albedo_abiotic", "radiative_entropy_production_biotic_W_K",
    "radiative_entropy_production_abiotic_W_K", "delta_radiative_entropy_production_W_K",
    "delta_radiative_entropy_percent", "mean_collector", "mean_sensing", "mean_processing", "mean_prediction",
    "mean_planning", "mean_action", "mean_agency_composite", "mean_cooperation", "mean_technology",
    "mean_infrastructure", "mean_local_cover", "mean_behaviour_gain", "mean_mobility_fraction",
]
