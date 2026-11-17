import unittest

from thermodynamic_emergence.open_reactor import (
    OpenReactorConfig,
    run_open_reactor_recovery_sweep,
    simulate_open_reactor_perturbation,
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


if __name__ == "__main__":
    unittest.main()
