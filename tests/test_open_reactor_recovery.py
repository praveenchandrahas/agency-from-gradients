import unittest

from thermodynamic_emergence.open_reactor import (
    OpenReactorConfig,
    run_open_reactor_recovery_sweep,
    simulate_open_reactor_perturbation,
    run_open_reactor_seed_sweep,
    run_open_reactor_washout_sweep,
    run_open_reactor_horizon_sweep,
)


class OpenReactorRecoveryTests(unittest.TestCase):
    def short_config(self, **overrides):
        values = {
            "duration_s": 2.0,
            "time_step_s": 0.001,
            "flow_rate_s": 0.05,
            "catalytic_strength": 5.0,
        }
        values.update(overrides)
        return OpenReactorConfig(**values)

    def test_perturbation_removes_declared_fraction(self):
        result = simulate_open_reactor_perturbation(
            self.short_config(),
            perturbation_time_s=1.0,
            removal_fraction=0.99,
        )
        d = result["diagnostics"]
        self.assertAlmostEqual(d["X_plus_Y_immediately_after"] / d["X_plus_Y_before"], 0.01)
        self.assertAlmostEqual(
            d["fraction_of_preperturbation_XY_restored"],
            d["X_plus_Y_final"] / d["X_plus_Y_before"],
        )

    def test_post_event_seed_feed_does_not_change_pre_event_history(self):
        cfg = self.short_config()
        low = simulate_open_reactor_perturbation(
            cfg, perturbation_time_s=1.0, removal_fraction=0.99,
            post_perturbation_catalyst_feed_activity=1.0e-8,
        )
        high = simulate_open_reactor_perturbation(
            cfg, perturbation_time_s=1.0, removal_fraction=0.99,
            post_perturbation_catalyst_feed_activity=1.0e-4,
        )
        self.assertEqual(low["pre_perturbation"], high["pre_perturbation"])
        self.assertEqual(low["immediately_post_perturbation"], high["immediately_post_perturbation"])
        self.assertNotEqual(
            low["post_perturbation_catalyst_feed_activity"],
            high["post_perturbation_catalyst_feed_activity"],
        )

    def test_recovery_metrics_and_ness_diagnostic_are_reported(self):
        result = simulate_open_reactor_perturbation(
            self.short_config(), perturbation_time_s=1.0, removal_fraction=0.9
        )
        d = result["diagnostics"]
        self.assertIn("fraction_of_removed_XY_recovered", d)
        self.assertIn("final_XY_relative_to_unperturbed", d)
        self.assertIsInstance(d["post_perturbation_operational_ness_detected"], bool)

    def test_recovery_sweep_covers_removal_and_post_event_seed(self):
        rows = run_open_reactor_recovery_sweep(
            self.short_config(),
            removal_fractions=(0.9, 0.99),
            post_catalyst_feed_activities=(1.0e-8, 1.0e-5),
            perturbation_time_s=1.0,
        )
        self.assertEqual(len(rows), 4)
        self.assertEqual({row["removal_fraction"] for row in rows}, {0.9, 0.99})
        self.assertEqual(
            {row["post_perturbation_catalyst_feed_activity"] for row in rows},
            {1.0e-8, 1.0e-5},
        )

    def test_invalid_perturbation_settings_are_rejected(self):
        with self.assertRaises(ValueError):
            simulate_open_reactor_perturbation(
                self.short_config(), perturbation_time_s=1.0, removal_fraction=1.0
            )
        with self.assertRaises(ValueError):
            simulate_open_reactor_perturbation(
                self.short_config(), perturbation_time_s=1.0,
                post_perturbation_catalyst_feed_activity=0.0,
            )


    def test_seed_sweep_uses_positive_feed_values_and_reports_seed_dependence(self):
        rows = run_open_reactor_seed_sweep(
            self.short_config(),
            catalyst_feed_activities=(1.0e-8, 1.0e-10),
            perturbation_time_s=1.0,
            removal_fraction=0.99,
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            {row["post_perturbation_catalyst_feed_activity"] for row in rows},
            {1.0e-8, 1.0e-10},
        )
        self.assertTrue(all(row["post_perturbation_catalyst_feed_activity"] > 0 for row in rows))

    def test_washout_sweep_covers_flow_and_removal(self):
        rows = run_open_reactor_washout_sweep(
            self.short_config(),
            flow_rates_s=(0.02, 0.05),
            removal_fractions=(0.9, 0.99),
            perturbation_time_s=1.0,
        )
        self.assertEqual(len(rows), 4)
        self.assertEqual({row["flow_rate_s"] for row in rows}, {0.02, 0.05})
        self.assertEqual({row["removal_fraction"] for row in rows}, {0.9, 0.99})

    def test_horizon_sweep_reports_post_event_steadiness(self):
        rows = run_open_reactor_horizon_sweep(
            self.short_config(),
            durations_s=(2.0, 3.0),
            perturbation_time_s=1.0,
            removal_fraction=0.99,
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            {row["post_perturbation_observation_s"] for row in rows},
            {1.0, 2.0},
        )
        self.assertTrue(all("post_perturbation_operational_ness_detected" in row for row in rows))


if __name__ == "__main__":
    unittest.main()
