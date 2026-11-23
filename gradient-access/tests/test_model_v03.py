import numpy as np
import pytest

from ega.model_v03 import (
    ConfigV03,
    evaluate_state,
    free_energy_balance,
    mutation_kernel,
    simulate_v03,
)


def small_config(**overrides):
    values = {
        "barrier": 8.0,
        "duration": 20.0,
        "steps": 200,
        "initial_genotype_concentrations": (0.05, 0.05, 0.05, 1e-6),
    }
    values.update(overrides)
    return ConfigV03(**values)


def test_mutation_kernel_is_symmetric_and_row_stochastic():
    k = mutation_kernel(2, 0.1)
    assert np.allclose(k, k.T, atol=1e-14)
    assert np.allclose(k.sum(axis=1), 1.0, atol=1e-14)


def test_genotype_match_changes_energy_capture_but_not_replication_kinetics():
    cfg = small_config()
    n = cfg.genotype_count
    low = np.array([0.03, 0.02, 0.01, 0.004])
    high = np.array([0.01, 0.02, 0.03, 0.002])
    state = np.r_[0.98, 0.45, low, high]
    k = mutation_kernel(2, 0.1)
    _, target0 = evaluate_state(state, cfg, 0, k, True, "L")
    _, target3 = evaluate_state(state, cfg, 3, k, True, "L")
    assert not np.allclose(target0["j1"], target3["j1"])
    assert np.allclose(target0["j2"], target3["j2"], atol=1e-14)
    assert np.allclose(target0["k1"], target3["k1"]) is False


def test_pointwise_free_energy_balance_closes():
    cfg = small_config()
    low = np.array([0.03, 0.02, 0.01, 0.004])
    high = np.array([0.01, 0.02, 0.03, 0.002])
    state = np.r_[0.98, 0.45, low, high]
    k = mutation_kernel(2, 0.1)
    residual, _, _, _ = free_energy_balance(state, cfg, 3, k, True, "L")
    assert abs(residual) < 1e-10


def test_entropy_production_is_nonnegative_for_reaction_and_flow_channels():
    cfg = small_config()
    low = np.array([0.03, 0.02, 0.01, 0.004])
    high = np.array([0.01, 0.02, 0.03, 0.002])
    state = np.r_[0.98, 0.45, low, high]
    k = mutation_kernel(2, 0.1)
    _, diag = evaluate_state(state, cfg, 3, k, True, "L")
    for name in ("sigma1", "sigma2", "sigma3", "sigma_flow", "sigma_total"):
        assert diag[name] >= -1e-12


def test_zero_barrier_removes_genotype_match_advantage():
    cfg = small_config(
        barrier=0.0,
        initial_genotype_concentrations=(0.05, 0.05, 0.05, 0.05),
    )
    d = simulate_v03("D", cfg)
    l = simulate_v03("L", cfg)
    assert abs(d["late_throughput"] - l["late_throughput"]) < 1e-10
    assert abs(d["cumulative_fuel_extent"] - l["cumulative_fuel_extent"]) < 1e-10


def test_fixed_library_does_not_change_total_genotype_abundance():
    cfg = small_config()
    result = simulate_v03("M", cfg)
    assert abs(result["final_total_replicator"] - result["initial_total_replicator"]) < 1e-9


def test_replication_extent_matches_total_population_change():
    cfg = small_config()
    result = simulate_v03("D", cfg)
    observed = result["final_total_replicator"] - result["initial_total_replicator"]
    assert abs(observed - result["cumulative_replication_extent"]) < 1e-6


def test_d_and_l_share_identical_initial_state_and_target_history():
    cfg = small_config()
    schedule = ((0.0, 0), (10.0, 3))
    d = simulate_v03("D", cfg, schedule)
    l = simulate_v03("L", cfg, schedule)
    assert d["initial_state"] == l["initial_state"]
    assert d["target_schedule"] == l["target_schedule"]


def test_target_switch_changes_environment_without_state_clipping():
    cfg = small_config()
    result = simulate_v03("L", cfg, ((0.0, 0), (10.0, 3)))
    assert result["target_changes"] == 1
    assert min(result["final_state"]) > 0
    assert max(result["final_state"][:2]) < 1
    assert result["max_pointwise_free_energy_balance_residual"] < 1e-9
    assert abs(result["cumulative_free_energy_balance_residual"]) < 1e-5


def test_invalid_arm_rejected():
    with pytest.raises(ValueError):
        simulate_v03("X", small_config())
