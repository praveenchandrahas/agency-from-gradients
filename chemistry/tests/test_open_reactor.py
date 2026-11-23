import math
import unittest

from thermodynamic_emergence.open_reactor import (
    OpenReactorConfig,
    compare_open_reactor,
    run_open_reactor_sweep,
    simulate_open_reactor,
)


class OpenReactorTests(unittest.TestCase):
    def short_config(self, **overrides):
        values = {
            "duration_s": 2.0,
            "time_step_s": 0.001,
            "flow_rate_s": 0.05,
            "catalytic_strength": 5.0,
        }
        values.update(overrides)
        return OpenReactorConfig(**values)

    def test_open_reactor_has_explicit_finite_reservoir_activities(self):
        result = simulate_open_reactor(self.short_config())
        self.assertEqual(result["feed_activities"]["A"], 1.0)
        self.assertEqual(result["feed_activities"]["B"], 1.0)
        self.assertGreater(result["feed_activities"]["X"], 0.0)
        self.assertGreater(result["feed_activities"]["Y"], 0.0)

    def test_reaction_and_exchange_entropy_production_are_nonnegative(self):
        result = simulate_open_reactor(self.short_config())
        d = result["diagnostics"]
        self.assertGreaterEqual(d["minimum_reaction_entropy_production_contribution"], -1.0e-8)
        self.assertGreaterEqual(d["minimum_exchange_entropy_production_contribution"], -1.0e-8)
        self.assertGreaterEqual(d["final_total_entropy_production_J_L_K_s"], -1.0e-8)

    def test_open_system_reports_flow_and_separates_entropy_terms(self):
        result = simulate_open_reactor(self.short_config())
        d = result["diagnostics"]
        self.assertGreater(d["cumulative_feed_activity"]["A"], 0.0)
        self.assertGreater(d["cumulative_outflow_activity"]["A"], 0.0)
        self.assertIn("integrated_reaction_entropy_production_J_L_K", d)
        self.assertIn("integrated_reservoir_exchange_entropy_production_J_L_K", d)
        self.assertIn("Mechanical pumping and mixing work.", result["accounting"]["not_included"])

    def test_ness_diagnostic_is_explicit_and_finite(self):
        result = simulate_open_reactor(self.short_config())
        d = result["diagnostics"]
        self.assertIsInstance(d["ness_detected"], bool)
        self.assertTrue(math.isfinite(d["ness_relative_endpoint_drift"]))
        self.assertTrue(math.isfinite(d["ness_max_species_coefficient_of_variation"]))

    def test_catalytic_comparison_uses_matched_flow_and_feed(self):
        result = compare_open_reactor(self.short_config())
        self.assertEqual(
            result["catalytic"]["feed_activities"],
            result["uncatalysed_null"]["feed_activities"],
        )
        self.assertEqual(
            result["catalytic"]["configuration"]["flow_rate_s"],
            result["uncatalysed_null"]["configuration"]["flow_rate_s"],
        )
        self.assertGreater(result["comparison"]["X_plus_Y_ratio"], 0.0)

    def test_invalid_flow_and_nonintegral_steps_are_rejected(self):
        with self.assertRaises(ValueError):
            OpenReactorConfig(flow_rate_s=0.0).validate()
        with self.assertRaises(ValueError):
            OpenReactorConfig(duration_s=1.0, time_step_s=0.3).validate()

    def test_sweep_covers_catalysis_and_flow_conditions(self):
        rows = run_open_reactor_sweep(
            self.short_config(),
            catalytic_strengths=(0.0, 2.0),
            flow_rates_s=(0.02, 0.05),
        )
        self.assertEqual(len(rows), 4)
        self.assertEqual({row["flow_rate_s"] for row in rows}, {0.02, 0.05})
        self.assertEqual({row["catalytic_strength"] for row in rows}, {0.0, 2.0})


if __name__ == "__main__":
    unittest.main()
