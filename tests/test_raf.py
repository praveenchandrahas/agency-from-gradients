import unittest

from thermodynamic_emergence.raf import (
    RafConfig,
    compare_catalysis,
    run_perturbation_sweep,
    simulate_perturbation,
    simulate_raf_network,
)


class RafNetworkTests(unittest.TestCase):
    def test_declared_network_has_mutual_catalyst_closure(self):
        result = simulate_raf_network()
        self.assertTrue(result["raf_closure"]["food_generated"])
        self.assertTrue(result["raf_closure"]["reflexively_autocatalytic"])
        self.assertEqual(result["food_set"], ["A", "B"])

    def test_finite_resource_moiety_balances_are_conserved(self):
        result = simulate_raf_network()
        for error in result["diagnostics"]["moiety_balance_errors"].values():
            self.assertAlmostEqual(error, 0.0, delta=1.0e-8)

    def test_reaction_entropy_production_is_nonnegative(self):
        result = simulate_raf_network()
        self.assertGreaterEqual(
            result["diagnostics"]["minimum_reaction_entropy_production_rate_J_L_K_s"],
            -1.0e-10,
        )

    def test_mutual_catalysis_accelerates_finite_time_conversion(self):
        result = compare_catalysis()
        self.assertGreater(result["finite_time_amplification_ratio"], 1.5)
        self.assertGreater(
            result["catalytic_final"]["X"] + result["catalytic_final"]["Y"],
            result["uncatalysed_null_final"]["X"] + result["uncatalysed_null_final"]["Y"],
        )

    def test_catalysis_does_not_change_equilibrium_constants(self):
        cfg = RafConfig()
        self.assertEqual(cfg.production_equilibrium_constant, 10.0)
        self.assertEqual(cfg.loss_equilibrium_constant, 1.0e-4)

    def test_invalid_negative_catalysis_is_rejected(self):
        with self.assertRaises(ValueError):
            RafConfig(catalytic_strength=-1.0).validate()

    def test_non_integral_step_count_is_rejected(self):
        with self.assertRaises(ValueError):
            RafConfig(duration_s=1.0, time_step_s=0.3).validate()

    def test_perturbation_removes_declared_fraction_of_catalysts(self):
        result = simulate_perturbation(removal_fraction=0.99)
        d = result["diagnostics"]
        self.assertAlmostEqual(d["X_plus_Y_immediately_after"] / d["X_plus_Y_before"], 0.01)
        self.assertAlmostEqual(d["fraction_of_preperturbation_XY_restored"],
                               d["X_plus_Y_final"] / d["X_plus_Y_before"])

    def test_post_perturbation_material_balances_use_remaining_inventory(self):
        result = simulate_perturbation(removal_fraction=0.99)
        for error in result["diagnostics"]["post_perturbation_moiety_balance_errors"].values():
            self.assertAlmostEqual(error, 0.0, delta=1.0e-8)

    def test_perturbation_time_must_align_with_integration_step(self):
        with self.assertRaises(ValueError):
            simulate_perturbation(perturbation_time_s=5.0005)

    def test_background_rate_factor_is_validated(self):
        with self.assertRaises(ValueError):
            RafConfig(background_rate_factor=-0.1).validate()

    def test_perturbation_sweep_covers_removal_and_background_factors(self):
        rows = run_perturbation_sweep(
            RafConfig(duration_s=2.0, time_step_s=0.001),
            removal_fractions=(0.9, 0.99),
            background_factors=(1.0, 0.1),
            perturbation_time_s=1.0,
        )
        self.assertEqual(len(rows), 4)


if __name__ == "__main__":
    unittest.main()
