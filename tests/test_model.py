import math
import unittest

from thermodynamic_emergence.model import (
    PlanetaryConfig,
    PlanetaryLedger,
    STEFAN_BOLTZMANN_W_M2_K4,
    _spectral_entropy_radiance_integral,
    calculate_earth_like_baseline,
)


class PlanetaryLedgerTests(unittest.TestCase):
    def test_blackbody_entropy_flux_reduces_to_four_thirds_sigma_t_cubed(self):
        temperature = 300.0
        radiance_entropy = _spectral_entropy_radiance_integral(
            temperature, 1.0, points=4001, x_max=40.0
        )
        calculated_flux = math.pi * radiance_entropy
        analytic_flux = (4.0 / 3.0) * STEFAN_BOLTZMANN_W_M2_K4 * temperature**3
        self.assertAlmostEqual(calculated_flux / analytic_flux, 1.0, places=7)

    def test_geometry_global_mean_is_one_quarter_direct_irradiance(self):
        result = calculate_earth_like_baseline()
        direct = result["geometry"]["direct_stellar_irradiance_normal_W_m2"]
        global_mean = result["energy"]["incoming_stellar_global_mean_W_m2"]
        self.assertAlmostEqual(global_mean, direct / 4.0, places=12)

    def test_energy_budget_closes_for_solved_radiative_equilibrium(self):
        result = calculate_earth_like_baseline()
        energy = result["energy"]
        self.assertAlmostEqual(
            energy["absorbed_shortwave_global_mean_W_m2"],
            energy["outgoing_thermal_global_mean_W_m2"],
            places=9,
        )
        self.assertLess(abs(energy["energy_balance_residual_W_m2"]), 1e-9)
        self.assertEqual(energy["radiative_energy_storage_rate_global_mean_W_m2"], 0.0)

    def test_energy_imbalance_is_reported_as_storage_not_entropy_production(self):
        result = PlanetaryLedger(
            PlanetaryConfig(emission_temperature_K=280.0)
        ).calculate()
        self.assertFalse(result["energy"]["radiative_equilibrium"])
        self.assertIsNone(
            result["radiative_entropy"]["conditional_internal_entropy_generation_if_entropy_steady_global_mean_W_m2K"]
        )
        self.assertIn(
            "Not inferred",
            result["radiative_entropy"]["entropy_generation_interpretation"],
        )
        self.assertNotEqual(result["energy"]["radiative_energy_storage_rate_global_mean_W_m2"], 0.0)

    def test_diffuse_reflection_entropy_is_zero_when_albedo_is_zero(self):
        result = calculate_earth_like_baseline(bond_albedo=0.0)
        self.assertAlmostEqual(
            result["radiative_entropy"]["reflected_shortwave_entropy_global_mean_W_m2K"],
            0.0,
            places=12,
        )

    def test_stefan_boltzmann_balance_has_expected_earth_like_scale(self):
        result = calculate_earth_like_baseline()
        energy = result["energy"]
        self.assertGreater(energy["incoming_stellar_global_mean_W_m2"], 330.0)
        self.assertLess(energy["incoming_stellar_global_mean_W_m2"], 350.0)
        self.assertGreater(energy["effective_emission_temperature_K"], 250.0)
        self.assertLess(energy["effective_emission_temperature_K"], 260.0)

    def test_planck_entropy_result_is_consistent_with_wu_liu_earth_range(self):
        result = calculate_earth_like_baseline()
        value = result["radiative_entropy"]["net_radiative_entropy_export_global_mean_W_m2K"]
        # Wu & Liu (2010) report 1.272–1.284 W m^-2 K^-1 for their stated
        # albedo/emissivity range. This is a rounded cross-check, not a fit target.
        self.assertGreater(value, 1.25)
        self.assertLess(value, 1.30)

    def test_invalid_config_is_rejected(self):
        with self.assertRaises(ValueError):
            PlanetaryConfig(bond_albedo=1.2).validate()


if __name__ == "__main__":
    unittest.main()
