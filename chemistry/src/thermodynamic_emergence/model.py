"""Zero-dimensional stellar–planetary energy, exergy and radiation-entropy ledger.

The model is intentionally limited to a blackbody star, a spherical planet,
constant Bond albedo, diffuse (Lambertian) shortwave reflection, and a uniform
graybody effective thermal emitter. It is an accounting model, not a climate,
chemistry, origin-of-life, or evolutionary model.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

import numpy as np

# 2022 CODATA values / SI defining constants.
STEFAN_BOLTZMANN_W_M2_K4 = 5.670374419e-8
PLANCK_J_S = 6.62607015e-34
BOLTZMANN_J_K = 1.380649e-23
SPEED_OF_LIGHT_M_S = 299_792_458.0


@dataclass(frozen=True)
class PlanetaryConfig:
    """Parameters for the idealized star–planet system.

    Defaults are rounded Earth–Sun-like reference values, not a claim that
    Earth is a perfect blackbody or that its albedo/emissivity are constant.

    If emission_temperature_K is None, it is solved from radiative
    equilibrium. If supplied explicitly, the model reports net energy
    storage/release instead.
    """

    stellar_temperature_K: float = 5772.0
    stellar_radius_m: float = 6.957e8
    orbital_distance_m: float = 1.495978707e11
    planet_radius_m: float = 6.371e6
    bond_albedo: float = 0.30
    thermal_emissivity: float = 1.0
    reference_environment_temperature_K: float = 288.15
    emission_temperature_K: float | None = None
    frequency_grid_points: int = 4001
    angular_grid_points: int = 401
    spectral_x_max: float = 40.0
    steady_state_tolerance_W_m2: float = 1e-7

    def validate(self) -> None:
        positive = {
            "stellar_temperature_K": self.stellar_temperature_K,
            "stellar_radius_m": self.stellar_radius_m,
            "orbital_distance_m": self.orbital_distance_m,
            "planet_radius_m": self.planet_radius_m,
            "reference_environment_temperature_K": self.reference_environment_temperature_K,
            "spectral_x_max": self.spectral_x_max,
        }
        for name, value in positive.items():
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a finite positive number")
        if self.orbital_distance_m <= self.stellar_radius_m:
            raise ValueError("orbital_distance_m must exceed stellar_radius_m")
        if not 0.0 <= self.bond_albedo <= 1.0:
            raise ValueError("bond_albedo must be between 0 and 1")
        if not 0.0 < self.thermal_emissivity <= 1.0:
            raise ValueError("thermal_emissivity must be in (0, 1]")
        if self.reference_environment_temperature_K >= self.stellar_temperature_K:
            raise ValueError("reference environment must be cooler than the star")
        if self.emission_temperature_K is not None:
            if not math.isfinite(self.emission_temperature_K) or self.emission_temperature_K < 0:
                raise ValueError("emission_temperature_K must be finite and non-negative")
        # Composite Simpson integration requires an odd number of samples.
        if self.frequency_grid_points < 101 or self.frequency_grid_points % 2 == 0:
            raise ValueError("frequency_grid_points must be odd and at least 101")
        if self.angular_grid_points < 3 or self.angular_grid_points % 2 == 0:
            raise ValueError("angular_grid_points must be odd and at least 3")
        if not math.isfinite(self.steady_state_tolerance_W_m2) or self.steady_state_tolerance_W_m2 <= 0:
            raise ValueError("steady_state_tolerance_W_m2 must be finite and positive")


def _simpson_last_axis(values: np.ndarray, spacing: float) -> np.ndarray:
    """Composite Simpson integral along the last axis (odd sample count)."""
    if values.shape[-1] < 3 or values.shape[-1] % 2 == 0:
        raise ValueError("Simpson integration requires an odd number of samples")
    return (spacing / 3.0) * (
        values[..., 0]
        + values[..., -1]
        + 4.0 * np.sum(values[..., 1:-1:2], axis=-1)
        + 2.0 * np.sum(values[..., 2:-1:2], axis=-1)
    )


def _spectral_entropy_radiance_integral(
    temperature_K: float,
    occupation_scale: float | np.ndarray,
    *,
    points: int,
    x_max: float,
) -> float | np.ndarray:
    """Integrate Planck-mode entropy radiance over frequency.

    For x = h*nu/(k_B*T), Planck occupation is n_P = 1/(exp(x)-1).
    The supplied scale q gives n = q*n_P. Mode entropy is
    k_B*((1+n)*ln(1+n)-n*ln(n)); the two-polarization spectral radiance
    expression is integrated over frequency.

    Returns entropy radiance integrated over frequency, in
    W m^-2 sr^-1 K^-1. q=1 is a blackbody; q<1 is an idealized spectrally
    neutral dilution/emissivity scaling of radiance.
    """
    if temperature_K == 0:
        q_arr = np.asarray(occupation_scale, dtype=float)
        zeros = np.zeros_like(q_arr, dtype=float)
        return float(zeros) if zeros.ndim == 0 else zeros
    if temperature_K < 0:
        raise ValueError("temperature_K cannot be negative")

    q = np.asarray(occupation_scale, dtype=float)
    if np.any(~np.isfinite(q)) or np.any(q < 0):
        raise ValueError("occupation_scale must contain finite, non-negative values")

    x = np.linspace(1.0e-8, x_max, points, dtype=float)
    dx = x[1] - x[0]
    planck_occupation = 1.0 / np.expm1(x)
    n = q[..., np.newaxis] * planck_occupation
    n_safe = np.maximum(n, np.finfo(float).tiny)
    mode_entropy_over_k = (1.0 + n) * np.log1p(n) - n * np.log(n_safe)
    integrand = (x * x) * mode_entropy_over_k
    integral = _simpson_last_axis(integrand, dx)
    coefficient = (
        2.0
        * BOLTZMANN_J_K**4
        * temperature_K**3
        / (PLANCK_J_S**3 * SPEED_OF_LIGHT_M_S**2)
    )
    result = coefficient * integral
    return float(result) if np.ndim(result) == 0 else result


class PlanetaryLedger:
    """Calculate an idealized planetary energy and radiative-entropy ledger."""

    def __init__(self, config: PlanetaryConfig | None = None) -> None:
        self.config = config or PlanetaryConfig()
        self.config.validate()

    def calculate(self) -> dict[str, Any]:
        """Calculate and return all model outputs in explicit SI units."""
        cfg = self.config
        sigma = STEFAN_BOLTZMANN_W_M2_K4

        # Exact solid angle subtended by a spherical star at the planet.
        radius_ratio = cfg.stellar_radius_m / cfg.orbital_distance_m
        stellar_solid_angle_sr = 2.0 * math.pi * (1.0 - math.sqrt(1.0 - radius_ratio**2))
        stellar_radiance_bolometric_W_m2_sr = sigma * cfg.stellar_temperature_K**4 / math.pi
        direct_stellar_irradiance_W_m2 = (
            stellar_radiance_bolometric_W_m2_sr * stellar_solid_angle_sr
        )

        planet_area_m2 = 4.0 * math.pi * cfg.planet_radius_m**2
        intercepted_power_W = direct_stellar_irradiance_W_m2 * math.pi * cfg.planet_radius_m**2
        incoming_global_mean_W_m2 = direct_stellar_irradiance_W_m2 / 4.0
        reflected_shortwave_W_m2 = cfg.bond_albedo * incoming_global_mean_W_m2
        absorbed_shortwave_W_m2 = (1.0 - cfg.bond_albedo) * incoming_global_mean_W_m2

        if cfg.emission_temperature_K is None:
            if absorbed_shortwave_W_m2 == 0.0:
                emission_temperature_K = 0.0
            else:
                emission_temperature_K = (
                    absorbed_shortwave_W_m2 / (cfg.thermal_emissivity * sigma)
                ) ** 0.25
        else:
            emission_temperature_K = cfg.emission_temperature_K

        outgoing_thermal_W_m2 = (
            cfg.thermal_emissivity * sigma * emission_temperature_K**4
        )
        energy_balance_residual_W_m2 = absorbed_shortwave_W_m2 - outgoing_thermal_W_m2
        energy_steady_state = abs(energy_balance_residual_W_m2) <= cfg.steady_state_tolerance_W_m2
        # Do not amplify sub-tolerance floating-point residuals by multiplying
        # them by the entire planetary area. Preserve the raw residual separately.
        storage_rate_W_m2 = 0.0 if energy_steady_state else energy_balance_residual_W_m2
        storage_rate_W = storage_rate_W_m2 * planet_area_m2

        # Idealized Petela source-temperature factor. It does not resolve the
        # finite angular dilution of sunlight or the actual environmental field.
        t_ratio = cfg.reference_environment_temperature_K / cfg.stellar_temperature_K
        petela_factor = 1.0 - (4.0 / 3.0) * t_ratio + (1.0 / 3.0) * t_ratio**4
        incident_exergy_approx_W_m2 = incoming_global_mean_W_m2 * petela_factor
        absorbed_exergy_approx_W_m2 = absorbed_shortwave_W_m2 * petela_factor

        # Incident stellar entropy: blackbody radiance fills the apparent stellar
        # disk; the global mean projected-area factor over a sphere is 1/4.
        stellar_entropy_radiance = _spectral_entropy_radiance_integral(
            cfg.stellar_temperature_K,
            1.0,
            points=cfg.frequency_grid_points,
            x_max=cfg.spectral_x_max,
        )
        incoming_stellar_entropy_W_m2K = (
            stellar_solid_angle_sr * stellar_entropy_radiance / 4.0
        )

        # Lambertian reflection: at solar zenith cosine mu, spectrally neutral
        # reflected radiance is q*B_nu(T_star), q=alpha*Omega_star*mu/pi.
        # The local outgoing hemispheric entropy flux is pi times entropy
        # radiance; global area average is (1/2)*integral_0^1 dmu.
        mu = np.linspace(0.0, 1.0, cfg.angular_grid_points, dtype=float)
        reflected_radiance_scale = cfg.bond_albedo * stellar_solid_angle_sr * mu / math.pi
        reflected_entropy_radiance = _spectral_entropy_radiance_integral(
            cfg.stellar_temperature_K,
            reflected_radiance_scale,
            points=cfg.frequency_grid_points,
            x_max=cfg.spectral_x_max,
        )
        reflected_shortwave_entropy_W_m2K = 0.5 * math.pi * _simpson_last_axis(
            np.asarray(reflected_entropy_radiance),
            1.0 / (cfg.angular_grid_points - 1),
        )

        # Uniform graybody TOA emitter: radiance = emissivity * Planck radiance.
        thermal_entropy_radiance = _spectral_entropy_radiance_integral(
            emission_temperature_K,
            cfg.thermal_emissivity,
            points=cfg.frequency_grid_points,
            x_max=cfg.spectral_x_max,
        )
        outgoing_thermal_entropy_W_m2K = math.pi * float(thermal_entropy_radiance)

        net_radiative_entropy_export_W_m2K = (
            reflected_shortwave_entropy_W_m2K
            + outgoing_thermal_entropy_W_m2K
            - incoming_stellar_entropy_W_m2K
        )
        # This is only a conditional interpretation: energy balance is necessary,
        # but no secular entropy storage and no other entropy boundary transfers
        # must also be assumed. This zero-D model cannot test those assumptions.
        conditional_entropy_generation_W_m2K = (
            net_radiative_entropy_export_W_m2K if energy_steady_state else None
        )

        return {
            "configuration": asdict(cfg),
            "geometry": {
                "stellar_solid_angle_sr": stellar_solid_angle_sr,
                "direct_stellar_irradiance_normal_W_m2": direct_stellar_irradiance_W_m2,
                "planetary_surface_area_m2": planet_area_m2,
                "intercepted_stellar_power_W": intercepted_power_W,
            },
            "energy": {
                "incoming_stellar_global_mean_W_m2": incoming_global_mean_W_m2,
                "reflected_shortwave_global_mean_W_m2": reflected_shortwave_W_m2,
                "absorbed_shortwave_global_mean_W_m2": absorbed_shortwave_W_m2,
                "outgoing_thermal_global_mean_W_m2": outgoing_thermal_W_m2,
                "radiative_energy_storage_rate_global_mean_W_m2": storage_rate_W_m2,
                "radiative_energy_storage_rate_total_W": storage_rate_W,
                "radiative_equilibrium": energy_steady_state,
                "effective_emission_temperature_K": emission_temperature_K,
                "energy_balance_residual_W_m2": energy_balance_residual_W_m2,
            },
            "exergy_approximation": {
                "reference_environment_temperature_K": cfg.reference_environment_temperature_K,
                "petela_source_temperature_factor": petela_factor,
                "incoming_solar_exergy_global_mean_approx_W_m2": incident_exergy_approx_W_m2,
                "absorbed_solar_exergy_global_mean_approx_W_m2": absorbed_exergy_approx_W_m2,
                "warning": (
                    "Source-temperature Petela estimate only. It does not fully resolve "
                    "the finite angular dilution and actual spectral/angular radiation field."
                ),
            },
            "radiative_entropy": {
                "incoming_stellar_entropy_global_mean_W_m2K": incoming_stellar_entropy_W_m2K,
                "reflected_shortwave_entropy_global_mean_W_m2K": reflected_shortwave_entropy_W_m2K,
                "outgoing_thermal_entropy_global_mean_W_m2K": outgoing_thermal_entropy_W_m2K,
                "net_radiative_entropy_export_global_mean_W_m2K": net_radiative_entropy_export_W_m2K,
                "conditional_internal_entropy_generation_if_entropy_steady_global_mean_W_m2K": conditional_entropy_generation_W_m2K,
                "entropy_generation_interpretation": (
                    "Conditional interpretation only: in addition to energy balance, assume no secular "
                    "entropy storage and no matter or other non-radiative entropy transfers "
                    "across the model boundary. This model cannot test the entropy-storage assumption."
                    if energy_steady_state
                    else "Not inferred: the energy balance has a non-zero storage term, "
                    "and energy storage alone does not determine entropy storage rate."
                ),
            },
            "assumptions": [
                "Star is a uniform blackbody with the configured effective temperature and radius.",
                "Planet is spherical; stellar radiation is geometrically diluted in vacuum.",
                "Bond albedo is spectrally neutral and constant over the planet.",
                "Reflected shortwave radiation is Lambertian (diffuse) at each surface element.",
                "Planetary outgoing thermal radiation is a uniform graybody with constant emissivity.",
                "Atmospheric radiative transfer, clouds, spectral windows and spatial temperature structure are not resolved.",
                "Matter exchange, internal heat, tidal heating and non-radiative boundary fluxes are omitted.",
                "The exergy result is an explicitly approximate Petela source-temperature estimate.",
            ],
            "limitations": [
                "This is not a climate model and does not calculate surface temperature or habitability.",
                "The model does not represent chemistry, self-maintenance, replication, life, agency or evolution.",
                "Entropy results depend on the Lambertian-reflection and graybody-emission assumptions.",
                "A zero-dimensional global mean cannot resolve local gradients, transport or intermittency.",
            ],
        }


def earth_like_config(**overrides: Any) -> PlanetaryConfig:
    """Return the rounded Earth–Sun-like reference configuration."""
    values: dict[str, Any] = {
        "stellar_temperature_K": 5772.0,
        "stellar_radius_m": 6.957e8,
        "orbital_distance_m": 1.495978707e11,
        "planet_radius_m": 6.371e6,
        "bond_albedo": 0.30,
        "thermal_emissivity": 1.0,
        "reference_environment_temperature_K": 288.15,
    }
    values.update(overrides)
    return PlanetaryConfig(**values)


def calculate_earth_like_baseline(**overrides: Any) -> dict[str, Any]:
    """Convenience function for the default Earth-like accounting case."""
    return PlanetaryLedger(earth_like_config(**overrides)).calculate()
