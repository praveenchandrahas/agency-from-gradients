import unittest

from thermodynamic_emergence.chemistry import (
    ChemicalConfig,
    equilibrium_catalyst_activity,
    run_feed_sweep,
    simulate_chemical_network,
)


class ChemicalNetworkTests(unittest.TestCase):
    def test_autocatalytic_feed_maintains_enriched_catalyst(self):
        result = simulate_chemical_network()
        self.assertGreater(result["final"]["catalyst_activity"], 1.0)
        self.assertTrue(result["persistence_diagnostics"]["enriched_over_background_10x"])

    def test_low_feed_control_does_not_show_large_enrichment(self):
        result = simulate_chemical_network(ChemicalConfig(feed_activity=1.0e-6))
        self.assertLess(result["final"]["catalyst_enrichment_over_background"], 10.0)

    def test_reaction_entropy_production_is_nonnegative(self):
        result = simulate_chemical_network()
        series = result["time_series"]
        for key in (
            "growth_entropy_production_rate_J_L_K_s",
            "decay_entropy_production_rate_J_L_K_s",
            "entropy_production_rate_J_L_K_s",
        ):
            self.assertGreaterEqual(min(series[key]), -1.0e-12)

    def test_feed_sweep_increases_catalyst_abundance_above_threshold(self):
        rows = run_feed_sweep([1.0e-6, 0.05, 0.2, 1.0])
        activities = [row["final_catalyst_activity"] for row in rows]
        self.assertLess(activities[0], activities[1])
        self.assertLess(activities[1], activities[2])
        self.assertLess(activities[2], activities[3])

    def test_numerical_integration_matches_analytic_fixed_point(self):
        result = simulate_chemical_network()
        self.assertLess(result["final"]["relative_error_from_analytic_equilibrium"], 1.0e-8)

    def test_feed_sweep_outputs_analytic_equilibria(self):
        rows = run_feed_sweep([1.0e-6, 0.05, 0.2, 0.5, 1.0])
        self.assertTrue(all(row["relative_equilibrium_error"] < 1.0e-7 for row in rows))
        self.assertTrue(all(row["analytic_equilibrium_catalyst_activity"] > 0 for row in rows))

    def test_low_concentration_linear_invasion_threshold(self):
        config = ChemicalConfig()
        threshold = config.decay_forward_rate_s / config.growth_forward_rate_s
        self.assertAlmostEqual(threshold, 0.1)
        below = equilibrium_catalyst_activity(ChemicalConfig(feed_activity=0.05))
        above = equilibrium_catalyst_activity(ChemicalConfig(feed_activity=0.2))
        self.assertLess(below, above)

    def test_invalid_zero_chemostat_is_rejected(self):
        with self.assertRaises(ValueError):
            ChemicalConfig(feed_activity=0.0).validate()

    def test_incompatible_time_step_is_rejected(self):
        with self.assertRaises(ValueError):
            ChemicalConfig(duration_s=10.0, time_step_s=3.0).validate()


if __name__ == "__main__":
    unittest.main()
