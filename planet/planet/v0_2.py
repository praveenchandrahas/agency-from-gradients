#!/usr/bin/env python3
"""Simulation v0.2: spatial energy landscapes and the evolution of dissipative agency.

This is an exploratory, explicitly stylized eco-evolutionary model. It is not a
validated model of Earth's biosphere or a proof of maximum entropy production.

Run:
    python3 entropy_agency_sim_v0_2.py --output-dir results_v0_2

Dependencies: numpy, pandas, matplotlib

Key modelling safeguards:
- Unharvested sunlight is not treated as energy that disappears. The abiotic
  planet absorbs and re-radiates it.
- Biological energy throughput is reported separately from total planetary
  absorbed solar power and radiative entropy production.
- Life can change planetary albedo in this model, creating a genuine difference
  in absorbed power. That is an explicit, contestable ecological assumption.
- Selection acts on survival and reproduction through individual net energy,
  not on an entropy-production objective.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SIGMA = 5.670374419e-8  # W m^-2 K^-4
STEFAN_BOLTZMANN = SIGMA
EARTH_RADIUS_M = 6.371e6
EARTH_AREA_M2 = 4.0 * math.pi * EARTH_RADIUS_M**2
SUN_TEMPERATURE_K = 5778.0
SUN_RADIUS_M = 6.957e8
ORBIT_M = 1.495978707e11
YEAR_S = 365.2425 * 24.0 * 3600.0
SOLAR_CONSTANT_W_M2 = SIGMA * SUN_TEMPERATURE_K**4 * (SUN_RADIUS_M / ORBIT_M)**2
MEAN_TOA_W_M2 = SOLAR_CONSTANT_W_M2 / 4.0
JOULES_PER_MODEL_UNIT = 1.0e18
PHOTO_CHEMICAL_EFFICIENCY = 1.0e-3  # stylized planet-wide fraction of absorbed solar energy

TRAIT_NAMES = [
    "collector",
    "sensing",
    "processing",
    "prediction",
    "planning",
    "action",
    "cooperation",
    "technology",
]
TRAIT_INDEX = {name: i for i, name in enumerate(TRAIT_NAMES)}


@dataclass(frozen=True)
class Config:
    # World / time
    n_lat: int = 16
    n_lon: int = 24
    generations: int = 220
    replicates: int = 6
    initial_population: int = 260
    max_population: int = 20000
    seed: int = 20261116

    # Evolution
    mutation_sd: float = 0.035
    tech_innovation_probability: float = 0.004
    tech_innovation_step: float = 0.10
    selection_strength: float = 8.0  # softmax strength for parent choice by net energy
    baseline_metabolic_cost: float = 0.105
    trait_costs: tuple[float, ...] = (0.17, 0.055, 0.060, 0.050, 0.055, 0.045, 0.055, 0.080)
    survival_base: float = 0.40
    survival_gain: float = 0.58
    survival_slope: float = 12.0
    survival_threshold: float = 0.05
    birth_rate_base: float = 0.04
    birth_rate_gain: float = 0.16
    birth_rate_slope: float = 4.0
    birth_energy_threshold: float = 0.05
    dispersal_base: float = 0.035
    dispersal_action_gain: float = 0.25

    # Harvesting / collective infrastructure
    capture_sensitivity: float = 0.115
    cover_sensitivity: float = 0.085
    max_biotic_albedo_reduction: float = 0.085
    technology_capacity_gain: float = 1.35
    cooperation_capacity_gain: float = 0.85
    infrastructure_capacity_gain: float = 0.22
    infrastructure_build_rate: float = 0.020
    infrastructure_decay: float = 0.018
    max_infrastructure: float = 4.0

    # Behaviour / imperfect information
    sensing_noise: float = 0.42
    prediction_noise: float = 0.48
    planning_horizon_weight: float = 0.70
    baseline_move_probability: float = 0.025

    # Radiative / resource assumptions
    base_albedo_mean: float = 0.30
    albedo_spatial_sd: float = 0.055
    stellar_flux_multiplier: float = 1.0
    baseline_resource_efficiency: float = PHOTO_CHEMICAL_EFFICIENCY
    generation_seconds: float = YEAR_S
    resource_unit_joules: float = JOULES_PER_MODEL_UNIT


SCENARIOS: dict[str, dict[str, Any]] = {
    "weakly_variable": {
        "label": "Weakly variable",
        "spatial_contrast": 0.05,
        "seasonal_amplitude": 0.06,
        "weather_sigma": 0.035,
        "weather_persistence": 0.88,
        "cognition_enabled": True,
    },
    "predictable_seasonal": {
        "label": "Predictable seasonal shifts",
        "spatial_contrast": 0.18,
        "seasonal_amplitude": 0.32,
        "weather_sigma": 0.055,
        "weather_persistence": 0.88,
        "cognition_enabled": True,
    },
    "volatile_shifting": {
        "label": "Volatile shifting hotspots",
        "spatial_contrast": 0.24,
        "seasonal_amplitude": 0.27,
        "weather_sigma": 0.21,
        "weather_persistence": 0.42,
        "cognition_enabled": True,
    },
    "volatile_no_cognition": {
        "label": "Volatile / cognitive traits disabled",
        "spatial_contrast": 0.24,
        "seasonal_amplitude": 0.27,
        "weather_sigma": 0.21,
        "weather_persistence": 0.42,
        "cognition_enabled": False,
    },
    "strong_predictable_hotspots": {
        "label": "Strong, predictable hotspots",
        "spatial_contrast": 0.55,
        "seasonal_amplitude": 0.55,
        "weather_sigma": 0.08,
        "weather_persistence": 0.95,
        "cognition_enabled": True,
    },
    "strong_predictable_no_cognition": {
        "label": "Strong hotspots / cognitive traits disabled",
        "spatial_contrast": 0.55,
        "seasonal_amplitude": 0.55,
        "weather_sigma": 0.08,
        "weather_persistence": 0.95,
        "cognition_enabled": False,
    },
}


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def build_world(config: Config) -> dict[str, Any]:
    """Create an equal-area latitude/longitude grid and fixed geographic fields."""
    nlat, nlon = config.n_lat, config.n_lon
    mu = np.linspace(-1.0 + 1.0 / nlat, 1.0 - 1.0 / nlat, nlat)
    lat = np.arcsin(mu)
    lon = np.linspace(0.0, 2.0 * np.pi, nlon, endpoint=False)
    lat2, lon2 = np.meshgrid(lat, lon, indexing="ij")

    # Fixed geography: a weak longitudinal pattern and a polar reflectivity bias.
    geography = (
        0.55 * np.sin(2.0 * lon2 + 0.7)
        + 0.30 * np.cos(3.0 * lon2 - 0.4)
        + 0.20 * np.sin(2.0 * lat2 + lon2)
    )
    polar = np.abs(np.sin(lat2)) ** 1.7
    raw_albedo = (
        config.base_albedo_mean
        + config.albedo_spatial_sd * geography
        + 0.075 * (polar - float(np.mean(polar)))
    )
    base_albedo = np.clip(raw_albedo, 0.08, 0.78)
    # Normalize the global arithmetic mean to the configured albedo.
    base_albedo += config.base_albedo_mean - float(np.mean(base_albedo))
    base_albedo = np.clip(base_albedo, 0.05, 0.85)

    # Equal-area grid: all cells have the same area.
    cells = nlat * nlon
    patch_area = EARTH_AREA_M2 / cells

    # Moore neighbourhood on a torus. This is a convenience, not literal geography.
    neighbours = np.empty((cells, 9), dtype=np.int32)
    for i in range(nlat):
        for j in range(nlon):
            p = i * nlon + j
            k = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    ii = (i + di) % nlat
                    jj = (j + dj) % nlon
                    neighbours[p, k] = ii * nlon + jj
                    k += 1

    return {
        "lat": lat2,
        "lon": lon2,
        "base_albedo": base_albedo.ravel(),
        "patch_area": patch_area,
        "neighbours": neighbours,
        "shape": (nlat, nlon),
        "cells": cells,
    }


def smooth_field(field: np.ndarray) -> np.ndarray:
    """Cheap periodic local smoothing for correlated weather noise."""
    return (
        4.0 * field
        + np.roll(field, 1, 0)
        + np.roll(field, -1, 0)
        + np.roll(field, 1, 1)
        + np.roll(field, -1, 1)
    ) / 8.0


def seasonal_irradiance(
    generation: int,
    weather: np.ndarray,
    scenario: dict[str, Any],
    world: dict[str, Any],
    stellar_flux_multiplier: float = 1.0,
) -> np.ndarray:
    """Create local TOA irradiance with a configurable global stellar-flux multiplier."""
    lat = world["lat"]
    lon = world["lon"]
    phase = 2.0 * np.pi * generation / 36.0
    declination = scenario["seasonal_amplitude"] * np.sin(phase)
    lat_shift = np.maximum(np.cos(lat - declination), 0.04)
    longitude_pattern = 1.0 + scenario["spatial_contrast"] * (
        0.55 * np.sin(2.0 * lon + phase)
        + 0.30 * np.cos(3.0 * lon - 0.6 * phase)
    )
    raw = lat_shift * longitude_pattern * np.exp(weather)
    raw = np.maximum(raw, 1e-6)
    # Normalize spatial distribution, then scale the total stellar energy supply.
    if stellar_flux_multiplier <= 0:
        raise ValueError("stellar_flux_multiplier must be positive")
    raw *= (MEAN_TOA_W_M2 * stellar_flux_multiplier) / float(np.mean(raw))
    return raw.ravel()


def radiative_entropy_production(
    global_albedo: float,
    stellar_flux_multiplier: float = 1.0,
) -> dict[str, float]:
    """Global-mean, blackbody radiative entropy balance at steady state.

    Uses the common planetary approximation: uniform day/night redistribution,
    blackbody star and planet, and absorbed stellar entropy scaled by (1-A).
    It omits entropy generated by detailed reflection/scattering, atmospheric
    transport, clouds, spectral windows, and internal heat flows.
    """
    A = float(np.clip(global_albedo, 0.0, 0.95))
    if stellar_flux_multiplier <= 0:
        raise ValueError("stellar_flux_multiplier must be positive")
    absorbed_flux = (1.0 - A) * SOLAR_CONSTANT_W_M2 * stellar_flux_multiplier / 4.0
    t_eq = (absorbed_flux / SIGMA) ** 0.25
    incoming_entropy_flux = (
        0.25
        * (1.0 - A)
        * stellar_flux_multiplier
        * (SUN_RADIUS_M / ORBIT_M) ** 2
        * (4.0 / 3.0)
        * SIGMA
        * SUN_TEMPERATURE_K**3
    )
    outgoing_entropy_flux = (4.0 / 3.0) * SIGMA * t_eq**3
    entropy_production = max(0.0, outgoing_entropy_flux - incoming_entropy_flux) * EARTH_AREA_M2
    absorbed_power = absorbed_flux * EARTH_AREA_M2
    return {
        "global_albedo": A,
        "effective_radiating_temperature_K": float(t_eq),
        "absorbed_solar_power_W": float(absorbed_power),
        "incoming_radiative_entropy_flux_W_m2_K": float(incoming_entropy_flux),
        "outgoing_radiative_entropy_flux_W_m2_K": float(outgoing_entropy_flux),
        "radiative_entropy_production_W_K": float(entropy_production),
    }


def initialize_population(rng: np.random.Generator, config: Config, world: dict[str, Any], cognition: bool) -> tuple[np.ndarray, np.ndarray]:
    n = config.initial_population
    means = np.array([0.22, 0.08, 0.07, 0.06, 0.05, 0.08, 0.08, 0.015], dtype=float)
    traits = np.clip(rng.normal(means, 0.045, size=(n, len(TRAIT_NAMES))), 0.0, 1.0)
    if not cognition:
        traits[:, 1:6] = 0.0
    loc = rng.integers(0, world["cells"], size=n, dtype=np.int32)
    return traits, loc


def mutate_offspring(
    parent_traits: np.ndarray,
    rng: np.random.Generator,
    config: Config,
    cognition: bool,
) -> np.ndarray:
    if parent_traits.size == 0:
        return parent_traits.copy()
    child = parent_traits + rng.normal(0.0, config.mutation_sd, size=parent_traits.shape)
    child = np.clip(child, 0.0, 1.0)
    # Rare larger innovations let technology occasionally cross a valley of small changes.
    innovation = rng.random(len(child)) < config.tech_innovation_probability
    if np.any(innovation):
        child[innovation, TRAIT_INDEX["technology"]] = np.clip(
            child[innovation, TRAIT_INDEX["technology"]] + config.tech_innovation_step,
            0.0,
            1.0,
        )
    if not cognition:
        child[:, 1:6] = 0.0
    return child


def gini_coefficient(values: np.ndarray) -> float:
    """Gini coefficient for a non-negative vector; 0 is equal, 1 is concentrated."""
    x = np.asarray(values, dtype=float)
    x = np.clip(x, 0.0, None)
    total = float(np.sum(x))
    if len(x) == 0 or total <= 0:
        return 0.0
    ordered = np.sort(x)
    n = len(ordered)
    ranks = np.arange(1, n + 1, dtype=float)
    return float((2.0 * np.sum(ranks * ordered) / (n * total)) - (n + 1.0) / n)


def run_one(
    scenario_key: str,
    replicate: int,
    config: Config,
    world: dict[str, Any],
    keep_snapshot: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any] | None]:
    scenario = SCENARIOS[scenario_key]
    cognition = bool(scenario["cognition_enabled"])
    scenario_index = list(SCENARIOS).index(scenario_key)
    paired_environment_group = {
        "weakly_variable": 0,
        "predictable_seasonal": 1,
        "volatile_shifting": 2,
        "volatile_no_cognition": 2,
        "strong_predictable_hotspots": 3,
        "strong_predictable_no_cognition": 3,
    }[scenario_key]
    # Separate random streams ensure that a cognition-enabled run and its
    # disabled control receive the same weather/irradiance history.
    env_rng = np.random.default_rng(config.seed + 100_003 * replicate + 7_919 * paired_environment_group)
    rng = np.random.default_rng(config.seed + 100_003 * replicate + 1_009 * scenario_index)
    traits, locations = initialize_population(rng, config, world, cognition)
    n_cells = world["cells"]
    base_albedo = world["base_albedo"]
    neighbours = world["neighbours"]
    infrastructure = np.zeros(n_cells, dtype=float)
    weather = np.zeros(world["shape"], dtype=float)
    rows: list[dict[str, Any]] = []
    snapshot: dict[str, Any] | None = None

    for generation in range(config.generations + 1):
        start_locations = locations.copy()
        # Weather evolves as a correlated field; the future map is forecastable
        # only to the degree that persistence and seasonal regularity permit.
        fresh = env_rng.normal(0.0, scenario["weather_sigma"], size=world["shape"])
        fresh = smooth_field(fresh)
        weather = scenario["weather_persistence"] * weather + math.sqrt(
            max(0.0, 1.0 - scenario["weather_persistence"] ** 2)
        ) * fresh
        next_fresh = env_rng.normal(0.0, scenario["weather_sigma"], size=world["shape"])
        next_fresh = smooth_field(next_fresh)
        weather_next = scenario["weather_persistence"] * weather + math.sqrt(
            max(0.0, 1.0 - scenario["weather_persistence"] ** 2)
        ) * next_fresh
        flux_now = seasonal_irradiance(generation, weather, scenario, world, config.stellar_flux_multiplier)
        flux_next = seasonal_irradiance(generation + 1, weather_next, scenario, world, config.stellar_flux_multiplier)
        forecast_weather = scenario["weather_persistence"] * weather
        flux_forecast = seasonal_irradiance(generation + 1, forecast_weather, scenario, world, config.stellar_flux_multiplier)

        # Behavioural choice: evaluate the current patch and its eight neighbours.
        # Sensing improves current observations; processing extracts useful signals;
        # prediction improves forecasts; planning weights the forecast; action executes movement.
        if cognition and len(traits):
            cand = neighbours[locations]  # (n_agents, 9)
            sensing = traits[:, TRAIT_INDEX["sensing"]]
            processing = traits[:, TRAIT_INDEX["processing"]]
            prediction = traits[:, TRAIT_INDEX["prediction"]]
            planning = traits[:, TRAIT_INDEX["planning"]]
            action = traits[:, TRAIT_INDEX["action"]]
            current_field = flux_now * (1.0 - base_albedo)
            forecast_field = flux_forecast * (1.0 - base_albedo)
            obs_sigma = config.sensing_noise * (1.0 - sensing * processing) + 0.012
            pred_sigma = config.prediction_noise * (1.0 - prediction * processing) + 0.012
            current_obs = current_field[cand] + rng.normal(0.0, obs_sigma[:, None], size=cand.shape)
            future_obs = forecast_field[cand] + rng.normal(0.0, pred_sigma[:, None], size=cand.shape)
            future_weight = config.planning_horizon_weight * planning * prediction
            scores = (1.0 - future_weight[:, None]) * current_obs + future_weight[:, None] * future_obs
            best = np.argmax(scores, axis=1)
            proposed = cand[np.arange(len(locations)), best]
            move_probability = np.clip(config.baseline_move_probability + 0.92 * action, 0.0, 0.95)
            move = rng.random(len(locations)) < move_probability
            locations = np.where(move, proposed, locations)
        else:
            # Non-cognitive structures do not sense, predict, plan, or deliberately move.
            # A small baseline dispersal keeps the spatial population from being frozen.
            move = rng.random(len(locations)) < config.baseline_move_probability
            if np.any(move):
                choices = rng.integers(0, 9, size=int(np.sum(move)))
                locations[move] = neighbours[locations[move], choices]

        if len(traits) == 0:
            break

        # Local cooperation and technology build shared harvesting capacity.
        coop = traits[:, TRAIT_INDEX["cooperation"]]
        tech = traits[:, TRAIT_INDEX["technology"]]
        collector = traits[:, TRAIT_INDEX["collector"]]
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

        # An explicit, bounded payoff pathway for behavioural sophistication:
        # sensing/processing improve spatial targeting; prediction/planning help
        # exploit forecastable temporal opportunities; action enables active control.
        spatial_opportunity = float(np.std(flux_now) / max(np.mean(flux_now), 1e-12))
        temporal_opportunity = float(
            scenario["seasonal_amplitude"] + 1.5 * scenario["weather_sigma"]
        )
        forecastability = 0.30 + 0.70 * scenario["weather_persistence"]
        behaviour_gain = (
            0.35 * spatial_opportunity * 0.5 * (traits[:, 1] + traits[:, 2])
            + 0.30 * temporal_opportunity * forecastability * 0.5 * (traits[:, 3] + traits[:, 4])
            + 0.22 * (spatial_opportunity + temporal_opportunity) * traits[:, 5]
        )
        behaviour_multiplier = 1.0 + behaviour_gain
        capacity = collector_area * tech_multiplier * coop_multiplier * infra_multiplier * behaviour_multiplier
        capacity = np.clip(capacity, 0.02, 8.0)
        capacity_by_patch = np.bincount(locations, weights=capacity, minlength=n_cells)
        area_by_patch = np.bincount(locations, weights=collector_area, minlength=n_cells)

        # Living collectors can darken their occupied patch. This is a deliberate
        # ecological feedback; it is not a universal property of life.
        cover = 1.0 - np.exp(-config.cover_sensitivity * area_by_patch)
        albedo = np.clip(
            base_albedo - config.max_biotic_albedo_reduction * cover,
            0.035,
            0.90,
        )
        albedo_abiotic = base_albedo
        patch_area = world["patch_area"]
        absorbed_power_cell = flux_now * patch_area * (1.0 - albedo)
        absorbed_power_abiotic_cell = flux_now * patch_area * (1.0 - albedo_abiotic)
        absorbed_power = float(np.sum(absorbed_power_cell))
        absorbed_power_abiotic = float(np.sum(absorbed_power_abiotic_cell))

        # Convert absorbed stellar energy into a finite photosynthetic-like chemical
        # resource pool. Only a small fraction is available to the modeled agents.
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

        # Separate metabolic and capability-specific maintenance costs.
        costs = np.asarray(config.trait_costs, dtype=float)
        maintenance = config.baseline_metabolic_cost + np.sum((traits**2) * costs[None, :], axis=1)
        maintenance += 0.012 * np.maximum(0.0, action if cognition else 0.0)  # movement wear
        net_energy = gross_energy - maintenance

        # Shared infrastructure is built from a fraction of local net surplus.
        invest_weight = np.maximum(net_energy, 0.0) * coop * tech
        investment_by_patch = np.bincount(locations, weights=invest_weight, minlength=n_cells)
        infrastructure = np.clip(
            (1.0 - config.infrastructure_decay) * infrastructure
            + config.infrastructure_build_rate * investment_by_patch,
            0.0,
            config.max_infrastructure,
        )

        # Differential survival and reproduction depend only on organism-level
        # energy economics. No global entropy term enters the fitness calculation.
        survival_probability = config.survival_base + config.survival_gain * sigmoid(
            config.survival_slope * (net_energy - config.survival_threshold)
        )
        survival_probability = np.clip(survival_probability, 0.02, 0.995)
        survived_mask = rng.random(len(traits)) < survival_probability
        mean_net_energy = float(np.mean(net_energy))
        birth_rate_per_entity = config.birth_rate_base + config.birth_rate_gain * float(
            sigmoid(config.birth_rate_slope * (mean_net_energy - config.birth_energy_threshold))
        )
        n_births = int(rng.poisson(len(traits) * birth_rate_per_entity))

        # Store metrics before replacing the population.
        rad_biotic = radiative_entropy_production(
            float(np.average(albedo, weights=flux_now)), config.stellar_flux_multiplier
        )
        rad_abiotic = radiative_entropy_production(
            float(np.average(albedo_abiotic, weights=flux_now)), config.stellar_flux_multiplier
        )
        bio_power = total_harvested_units * config.resource_unit_joules / config.generation_seconds
        potential_bio_power = float(np.sum(resource_units)) * config.resource_unit_joules / config.generation_seconds
        moved_fraction = float(np.mean(locations != start_locations)) if generation > 0 else 0.0
        cognitive_mean = float(np.mean(np.mean(traits[:, 1:6], axis=1))) if cognition else 0.0
        gross_sorted = np.sort(np.maximum(gross_energy, 0.0))
        top_n = max(1, int(math.ceil(0.10 * len(gross_sorted))))
        top10_energy_share = float(np.sum(gross_sorted[-top_n:]) / max(np.sum(gross_sorted), 1e-12))
        survival_mean = float(np.mean(survival_probability))
        occupied_patches = int(np.count_nonzero(local_count))
        row: dict[str, Any] = {
            "scenario_key": scenario_key,
            "scenario": scenario["label"],
            "replicate": replicate,
            "generation": generation,
            "population": len(traits),
            "mean_gross_energy_units": float(np.mean(gross_energy)),
            "mean_maintenance_units": float(np.mean(maintenance)),
            "mean_net_energy_units": float(np.mean(net_energy)),
            "net_energy_p10": float(np.percentile(net_energy, 10)),
            "net_energy_p50": float(np.percentile(net_energy, 50)),
            "net_energy_p90": float(np.percentile(net_energy, 90)),
            "gross_energy_gini": gini_coefficient(gross_energy),
            "top10_gross_energy_share": top10_energy_share,
            "mean_survival_probability": survival_mean,
            "birth_rate_per_entity": float(birth_rate_per_entity),
            "occupied_patch_fraction": float(occupied_patches / n_cells),
            "mean_entities_per_occupied_patch": float(len(traits) / max(occupied_patches, 1)),
            "total_biotic_harvest_units": total_harvested_units,
            "potential_biotic_resource_units": float(np.sum(resource_units)),
            "biotic_capture_fraction_of_photo_pool": float(total_harvested_units / max(float(np.sum(resource_units)), 1e-12)),
            "biotic_power_harnessed_W": float(bio_power),
            "biotic_power_harnessed_TW": float(bio_power / 1e12),
            "biotic_power_per_entity_GW": float(bio_power / max(len(traits), 1) / 1e9),
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
                rad_biotic["radiative_entropy_production_W_K"]
                - rad_abiotic["radiative_entropy_production_W_K"]
            ),
            "delta_radiative_entropy_percent": 100.0 * (
                rad_biotic["radiative_entropy_production_W_K"]
                / max(rad_abiotic["radiative_entropy_production_W_K"], 1e-12) - 1.0
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
        rows.append(row)

        if keep_snapshot and generation in (0, config.generations // 2, config.generations):
            snapshot = {
                "generation": generation,
                "irradiance_W_m2": flux_now.reshape(world["shape"]).copy(),
                "base_albedo": base_albedo.reshape(world["shape"]).copy(),
                "biotic_albedo": albedo.reshape(world["shape"]).copy(),
                "population_density": local_count.reshape(world["shape"]).copy(),
                "cover": cover.reshape(world["shape"]).copy(),
            }

        if generation == config.generations:
            break

        # Reproduction: surviving adults plus offspring carrying mutated traits.
        survivor_traits = traits[survived_mask]
        survivor_locations = locations[survived_mask]
        # Birth count depends on population-level energetic conditions, while
        # parentage is selected by each entity's relative net energy payoff.
        if n_births:
            log_weights = config.selection_strength * (net_energy - float(np.mean(net_energy)))
            log_weights -= float(np.max(log_weights))
            parent_weights = np.exp(np.clip(log_weights, -40.0, 0.0))
            parent_weights /= np.sum(parent_weights)
            parent_ids = rng.choice(len(traits), size=n_births, replace=True, p=parent_weights)
            child_traits = mutate_offspring(traits[parent_ids], rng, config, cognition)
            child_locations = locations[parent_ids].copy()
            disperse_prob = np.clip(
                config.dispersal_base
                + config.dispersal_action_gain * traits[parent_ids, TRAIT_INDEX["action"]],
                0.0,
                0.60,
            )
            disperse = rng.random(len(parent_ids)) < disperse_prob
            if np.any(disperse):
                move_choice = rng.integers(0, 9, size=int(np.sum(disperse)))
                child_locations[disperse] = neighbours[
                    child_locations[disperse], move_choice
                ]
            traits = np.vstack([survivor_traits, child_traits])
            locations = np.concatenate([survivor_locations, child_locations]).astype(np.int32)
            source_net = np.concatenate([net_energy[survived_mask], net_energy[parent_ids]])
        else:
            traits = survivor_traits.copy()
            locations = survivor_locations.copy()
            source_net = net_energy[survived_mask].copy()

        if len(traits) == 0:
            break

        # Carrying capacity emerges from finite resource supply. This ceiling only
        # protects runtime; if reached, sample by energy-mediated reproductive value.
        if len(traits) > config.max_population:
            weights = np.exp(np.clip(config.selection_strength * (source_net - np.max(source_net)), -30, 0))
            probs = weights / np.sum(weights)
            keep = rng.choice(len(traits), size=config.max_population, replace=False, p=probs)
            traits = traits[keep]
            locations = locations[keep]

    df = pd.DataFrame(rows)
    return df, snapshot


def run_experiment(config: Config, output_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    world = build_world(config)
    all_runs: list[pd.DataFrame] = []
    snapshots: dict[str, Any] = {}
    for scenario_key in SCENARIOS:
        for replicate in range(config.replicates):
            print(f"Running {scenario_key}, replicate {replicate + 1}/{config.replicates} ...", flush=True)
            keep_snapshot = scenario_key == "volatile_shifting" and replicate == 0
            run_df, snapshot = run_one(scenario_key, replicate, config, world, keep_snapshot)
            all_runs.append(run_df)
            if snapshot is not None:
                snapshots[scenario_key] = snapshot
    results = pd.concat(all_runs, ignore_index=True)
    results.to_csv(output_dir / "entropy_agency_v0_2_timeseries.csv", index=False)
    final = results.sort_values("generation").groupby(["scenario_key", "replicate"], as_index=False).tail(1)
    summary = (
        final.groupby(["scenario_key", "scenario"])
        .agg(
            replicates=("replicate", "nunique"),
            final_population_mean=("population", "mean"),
            final_population_sd=("population", "std"),
            final_generation_mean=("generation", "mean"),
            collector_mean=("mean_collector", "mean"),
            collector_sd=("mean_collector", "std"),
            agency_mean=("mean_agency_composite", "mean"),
            agency_sd=("mean_agency_composite", "std"),
            behaviour_gain_mean=("mean_behaviour_gain", "mean"),
            gross_energy_gini_mean=("gross_energy_gini", "mean"),
            top10_energy_share_mean=("top10_gross_energy_share", "mean"),
            occupied_patch_fraction_mean=("occupied_patch_fraction", "mean"),
            sensing_mean=("mean_sensing", "mean"),
            processing_mean=("mean_processing", "mean"),
            prediction_mean=("mean_prediction", "mean"),
            planning_mean=("mean_planning", "mean"),
            action_mean=("mean_action", "mean"),
            cooperation_mean=("mean_cooperation", "mean"),
            technology_mean=("mean_technology", "mean"),
            infrastructure_mean=("mean_infrastructure", "mean"),
            biotic_power_TW_mean=("biotic_power_harnessed_TW", "mean"),
            biotic_power_TW_sd=("biotic_power_harnessed_TW", "std"),
            biotic_power_per_entity_GW_mean=("biotic_power_per_entity_GW", "mean"),
            biotic_kardashev_equivalent_mean=("biotic_kardashev_equivalent", "mean"),
            biotic_power_as_fraction_of_absorbed_mean=("biotic_power_as_fraction_of_absorbed", "mean"),
            biotic_capture_fraction_mean=("biotic_capture_fraction_of_photo_pool", "mean"),
            albedo_biotic_mean=("global_albedo_biotic", "mean"),
            albedo_abiotic_mean=("global_albedo_abiotic", "mean"),
            entropy_biotic_W_K_mean=("radiative_entropy_production_biotic_W_K", "mean"),
            entropy_abiotic_W_K_mean=("radiative_entropy_production_abiotic_W_K", "mean"),
            entropy_delta_percent_mean=("delta_radiative_entropy_percent", "mean"),
            extra_absorbed_power_TW_mean=("extra_absorbed_power_vs_abiotic_W", lambda x: float(np.mean(x) / 1e12)),
        )
        .reset_index()
    )
    summary.to_csv(output_dir / "entropy_agency_v0_2_final_summary.csv", index=False)

    # Within-environment cognitive ablations. These pairs share identical
    # irradiance/weather trajectories by construction.
    comparison_rows: list[dict[str, Any]] = []
    for enabled_key, disabled_key, label in [
        ("volatile_shifting", "volatile_no_cognition", "Volatile shifting hotspots"),
        ("strong_predictable_hotspots", "strong_predictable_no_cognition", "Strong predictable hotspots"),
    ]:
        enabled = final[final.scenario_key == enabled_key].set_index("replicate")
        disabled = final[final.scenario_key == disabled_key].set_index("replicate")
        for rep in sorted(set(enabled.index).intersection(disabled.index)):
            e = enabled.loc[rep]
            d = disabled.loc[rep]
            comparison_rows.append({
                "environment": label,
                "replicate": int(rep),
                "biotic_power_TW_cognition": float(e["biotic_power_harnessed_TW"]),
                "biotic_power_TW_no_cognitive_traits": float(d["biotic_power_harnessed_TW"]),
                "power_difference_TW": float(e["biotic_power_harnessed_TW"] - d["biotic_power_harnessed_TW"]),
                "power_per_entity_GW_cognition": float(e["biotic_power_per_entity_GW"]),
                "power_per_entity_GW_no_cognitive_traits": float(d["biotic_power_per_entity_GW"]),
                "population_cognition": int(e["population"]),
                "population_no_cognitive_traits": int(d["population"]),
                "agency_composite_cognition": float(e["mean_agency_composite"]),
                "gross_energy_gini_cognition": float(e["gross_energy_gini"]),
                "gross_energy_gini_no_cognitive_traits": float(d["gross_energy_gini"]),
                "occupied_patch_fraction_cognition": float(e["occupied_patch_fraction"]),
                "occupied_patch_fraction_no_cognitive_traits": float(d["occupied_patch_fraction"]),
                "entropy_delta_percent_cognition": float(e["delta_radiative_entropy_percent"]),
                "entropy_delta_percent_no_cognitive_traits": float(d["delta_radiative_entropy_percent"]),
                "same_environment_seed_group": True,
            })
    pd.DataFrame(comparison_rows).to_csv(output_dir / "entropy_agency_v0_2_cognitive_ablation.csv", index=False)

    make_plots(results, summary, world, snapshots, output_dir)
    config_blob = asdict(config)
    config_blob["trait_costs"] = list(config_blob["trait_costs"])
    metadata = {
        "version": "0.2",
        "config": config_blob,
        "scenarios": SCENARIOS,
        "planet": {
            "radius_m": EARTH_RADIUS_M,
            "surface_area_m2": EARTH_AREA_M2,
            "solar_constant_W_m2": SOLAR_CONSTANT_W_M2,
            "mean_TOA_W_m2": MEAN_TOA_W_M2,
            "star_temperature_K": SUN_TEMPERATURE_K,
            "photo_chemical_efficiency": config.baseline_resource_efficiency,
            "year_seconds": config.generation_seconds,
        },
        "notes": [
            "Agents are coarse-grained ecological entities/lineages, not individual cells or organisms.",
            "A generation is one model year for physical power conversion; biological generation time is abstract.",
            "Biotic energy throughput is a chemical-energy capture proxy, not additional energy beyond absorbed sunlight.",
            "The only modeled route to higher total planetary absorbed power is life-induced darkening (lower albedo).",
            "Radiative entropy production uses a global-mean blackbody equilibrium approximation.",
            "Cognition-disabled scenario freezes sensing, processing, prediction, planning, and action at zero; cooperation and technology remain evolvable.",
            "Matched cognition ablations share the same exogenous weather and irradiance time series.",
        ],
    }
    (output_dir / "entropy_agency_v0_2_metadata.json").write_text(json.dumps(metadata, indent=2))
    return results, metadata


def make_plots(
    results: pd.DataFrame,
    summary: pd.DataFrame,
    world: dict[str, Any],
    snapshots: dict[str, Any],
    output_dir: Path,
) -> None:
    labels = {k: v["label"] for k, v in SCENARIOS.items()}
    scenario_order = list(SCENARIOS.keys())
    def plot_one(metric: str, title: str, ylabel: str, filename: str, scenario_keys: list[str] | None = None) -> None:
        fig, ax = plt.subplots(figsize=(10.5, 5.6))
        keys = scenario_keys if scenario_keys is not None else scenario_order
        for scenario_key in keys:
            sub = results[results.scenario_key == scenario_key]
            agg = sub.groupby("generation")[metric].agg(["mean", "std"])
            ax.plot(agg.index, agg["mean"], linewidth=2.0, label=labels[scenario_key])
            spread = agg["std"].fillna(0).to_numpy()
            ax.fill_between(agg.index, agg["mean"].to_numpy() - spread,
                            agg["mean"].to_numpy() + spread, alpha=0.12)
        ax.set_title(title)
        ax.set_xlabel("Generation (model year)")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.22)
        ax.legend(fontsize=8, frameon=False, ncol=2)
        fig.tight_layout()
        fig.savefig(output_dir / filename, dpi=180, bbox_inches="tight")
        plt.close(fig)

    plot_one("mean_collector", "Evolution of physical harvesting capacity",
             "Collector trait (0–1)", "v0_2_collector_trajectories.png")
    plot_one("mean_agency_composite", "Evolution of behavioural agency",
             "Mean of sensing, processing, prediction, planning and action (0–1)",
             "v0_2_agency_trajectories.png")
    plot_one("mean_cooperation", "Evolution of cooperation",
             "Cooperation trait (0–1)", "v0_2_cooperation_trajectories.png")
    plot_one("mean_technology", "Evolution of technological investment",
             "Technology trait (0–1)", "v0_2_technology_trajectories.png")

    # Show the five cognitive capabilities separately in one interpretable,
    # high-opportunity environment, averaged over the independent replicates.
    focused = results[results.scenario_key == "strong_predictable_hotspots"]
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    cognitive_metrics = [
        ("mean_sensing", "Sensing"),
        ("mean_processing", "Information processing"),
        ("mean_prediction", "Prediction"),
        ("mean_planning", "Planning"),
        ("mean_action", "Action"),
    ]
    for metric, label in cognitive_metrics:
        agg = focused.groupby("generation")[metric].agg(["mean", "std"])
        ax.plot(agg.index, agg["mean"], linewidth=2.0, label=label)
        spread = agg["std"].fillna(0).to_numpy()
        ax.fill_between(agg.index, agg["mean"].to_numpy() - spread,
                        agg["mean"].to_numpy() + spread, alpha=0.12)
    ax.set_title("Separate agency components under strong, predictable energy gradients")
    ax.set_xlabel("Generation (model year)")
    ax.set_ylabel("Trait value (0–1)")
    ax.set_ylim(bottom=0, top=1.02)
    ax.grid(alpha=0.22)
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(output_dir / "v0_2_agency_components_strong_predictable.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Population and energy/thermodynamic outcomes.
    fig, axes = plt.subplots(2, 3, figsize=(14.2, 8.2))
    plot_specs = [
        ("population", "Population size", "Coarse-grained entities"),
        ("biotic_power_harnessed_TW", "Biotic chemical-energy throughput", "TW"),
        ("biotic_power_per_entity_GW", "Power captured per entity", "GW / entity"),
        ("gross_energy_gini", "Inequality in energy intake", "Gini coefficient"),
        ("global_albedo_biotic", "Global albedo (biotic planet)", "Albedo"),
        ("delta_radiative_entropy_percent", "Radiative entropy production difference", "% vs matched abiotic"),
    ]
    for ax, (metric, title, ylabel) in zip(axes.flat, plot_specs):
        for scenario_key in scenario_order:
            sub = results[results.scenario_key == scenario_key]
            agg = sub.groupby("generation")[metric].agg(["mean", "std"])
            ax.plot(agg.index, agg["mean"], linewidth=1.8, label=labels[scenario_key])
            spread = agg["std"].fillna(0).to_numpy()
            ax.fill_between(agg.index, agg["mean"].to_numpy() - spread, agg["mean"].to_numpy() + spread, alpha=0.10)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Generation")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.22)
    axes[0, 0].legend(fontsize=7.1, frameon=False)
    fig.suptitle("Population, energy throughput, and planetary thermodynamics", y=1.01, fontsize=13)
    fig.tight_layout()
    fig.savefig(output_dir / "v0_2_planetary_and_population_metrics.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # A direct paired comparison of final biological/planetary outcomes.
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.8))
    metrics = [
        ("biotic_power_TW_mean", "Total biotic energy throughput", "TW"),
        ("biotic_power_per_entity_GW_mean", "Power captured per entity", "GW / entity"),
        ("entropy_delta_percent_mean", "Change in planetary radiative entropy", "%"),
    ]
    for ax, (metric, title, ylabel) in zip(axes, metrics):
        vals = summary.set_index("scenario_key").loc[scenario_order, metric].to_numpy()
        ax.bar([labels[x] for x in scenario_order], vals)
        ax.set_title(title, fontsize=10)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", labelrotation=28, labelsize=7.5)
        ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_dir / "v0_2_final_scenario_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Last snapshot: energy landscape, albedo response, and population density.
    if snapshots:
        snap = snapshots.get("volatile_shifting") or next(iter(snapshots.values()))
        fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.0))
        im0 = axes[0].imshow(snap["irradiance_W_m2"], origin="lower", aspect="auto")
        axes[0].set_title("Incoming stellar irradiance (W/m²)")
        fig.colorbar(im0, ax=axes[0], fraction=0.046)
        im1 = axes[1].imshow(snap["biotic_albedo"], origin="lower", aspect="auto", vmin=0.05, vmax=0.8)
        axes[1].set_title("Albedo after biological cover")
        fig.colorbar(im1, ax=axes[1], fraction=0.046)
        im2 = axes[2].imshow(snap["population_density"], origin="lower", aspect="auto")
        axes[2].set_title("Population density by patch")
        fig.colorbar(im2, ax=axes[2], fraction=0.046)
        for ax in axes:
            ax.set_xlabel("Longitude cell")
            ax.set_ylabel("Latitude cell")
        fig.suptitle(f"Example spatial state, volatile environment, generation {snap['generation']}", y=1.02)
        fig.tight_layout()
        fig.savefig(output_dir / "v0_2_spatial_landscape_example.png", dpi=180, bbox_inches="tight")
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="entropy_agency_v0_2_outputs")
    parser.add_argument("--generations", type=int, default=None)
    parser.add_argument("--replicates", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    config = Config(
        generations=args.generations if args.generations is not None else Config.generations,
        replicates=args.replicates if args.replicates is not None else Config.replicates,
        seed=args.seed if args.seed is not None else Config.seed,
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results, metadata = run_experiment(config, output_dir)
    print("\nFinal summary:")
    print(pd.read_csv(output_dir / "entropy_agency_v0_2_final_summary.csv").to_string(index=False))
    print(f"\nOutputs written to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()