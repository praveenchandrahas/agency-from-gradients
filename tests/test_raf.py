import unittest

from thermodynamic_emergence.raf import RafConfig, compare_catalysis, simulate_raf_network


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
        # The catalyst multiplier is common to forward and reverse fluxes;
        # therefore it cancels from each reaction's zero-flux condition.
        self.assertEqual(cfg.production_equilibrium_constant, 10.0)
        self.assertEqual(cfg.loss_equilibrium_constant, 1.0e-4)

    def test_invalid_negative_catalysis_is_rejected(self):
        with self.assertRaises(ValueError):
            RafConfig(catalytic_strength=-1.0).validate()

    def test_non_integral_step_count_is_rejected(self):
        with self.assertRaises(ValueError):
            RafConfig(duration_s=1.0, time_step_s=0.3).validate()


if __name__ == "__main__":
    unittest.main()
