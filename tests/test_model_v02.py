import math

import numpy as np

from ega.model_v02 import (
    ConfigV02,
    evaluate_state,
    free_energy_balance,
    mutation_kernel,
    simulate_v02,
)


def small_config(**overrides):
    values = dict(
        key_bits=2,
        barrier=8.0,
        duration=20.0,
        steps=200,
        k0=0.8,
        krep=0.001,
        kmaint=0.0001,
        q_fuel=0.35,
        q_monomer=0.2,
        initial_concentrations=(0.05, 0.05, 0.05, 1e-6),
    )
    values.update(overrides)
    return ConfigV02(**values)


def test_standard_affinities_derive_from_one_potential_ledger():
    cfg = small_config()
    assert cfg.mu1 == 6.0
    assert cfg.mu2 == -1.0
    assert cfg.mu3 == 6.0


def test_mutation_kernel_is_symmetric_and_stochastic():
    kernel = mutation_kernel(3, 0.07)
    assert np.allclose(kernel, kernel.T)
    assert np.allclose(kernel.sum(axis=1), 1.0)
    assert np.all(kernel >= 0.0)


def test_all_reactions_relax_to_a_common_equilibrium():
    cfg = small_config(
        fuel_feed=math.exp(-12.0) / (1.0 + math.exp(-12.0)),
        monomer_feed=0.5,
    )
    t_eq = 1.0 / (1.0 + math.exp(cfg.mu3))
    c_eq = math.exp(cfg.mu2) * (0.5 / 0.5) ** cfg.monomers_per_catalyst * (
        t_eq / (1.0 - t_eq)
    ) ** cfg.atp_per_birth
    state = np.asarray([cfg.fuel_feed, t_eq, 0.5, c_eq, c_eq, c_eq, c_eq])
    kernel = mutation_kernel(2, 0.1)
    dy, diag = evaluate_state(state, cfg, target=0, kernel=kernel, replication=True)
    assert np.max(np.abs(dy)) < 1e-12
    assert abs(diag["sigma_total"]) < 1e-10
    assert abs(diag["affinity1"]) < 1e-10
    assert np.max(np.abs(diag["affinity2"])) < 1e-10
    assert abs(diag["affinity3"]) < 1e-10


def test_catalysts_change_rates_but_not_reaction_equilibrium():
    cfg = small_config(
        fuel_feed=math.exp(-12.0) / (1.0 + math.exp(-12.0)),
    )
    t_eq = 1.0 / (1.0 + math.exp(cfg.mu3))
    c_eq = math.exp(cfg.mu2) * (t_eq / (1.0 - t_eq))
    state = np.asarray([cfg.fuel_feed, t_eq, 0.5, c_eq, c_eq, c_eq, c_eq])
    kernel = mutation_kernel(2, 0.1)
    for barrier in (0.0, 4.0, 8.0, 12.0):
        local = ConfigV02(**{**cfg.__dict__, "barrier": barrier, "gain": 80.0})
        dy, diag = evaluate_state(state, local, 0, kernel, replication=True)
        assert np.max(np.abs(dy)) < 1e-10
        assert abs(diag["sigma_total"]) < 1e-9


def test_entropy_production_is_nonnegative_for_positive_states():
    cfg = small_config()
    kernel = mutation_kernel(2, 0.1)
    rng = np.random.default_rng(4)
    for _ in range(50):
        state = np.concatenate((
            rng.uniform(0.05, 0.95, size=3),
            rng.uniform(1e-5, 0.2, size=4),
        ))
        _, diag = evaluate_state(state, cfg, target=2, kernel=kernel, replication=True)
        for key in (
            "sigma_reaction1", "sigma_replication", "sigma_maintenance",
            "sigma_flow_fuel", "sigma_flow_monomer", "sigma_total",
        ):
            assert diag[key] >= -1e-10


def test_complete_declared_free_energy_balance_closes():
    cfg = small_config()
    kernel = mutation_kernel(2, 0.1)
    state = np.asarray([0.73, 0.61, 0.42, 0.08, 0.03, 0.02, 1e-5])
    balance = free_energy_balance(state, cfg, target=3, kernel=kernel)
    assert abs(balance["residual"]) < 1e-10


def test_zero_barrier_removes_genotype_specific_catalytic_advantage():
    cfg = small_config(barrier=0.0)
    kernel = mutation_kernel(2, 0.1)
    state = np.asarray([0.8, 0.6, 0.5, 0.05, 0.03, 0.02, 1e-5])
    _, diag = evaluate_state(state, cfg, target=0, kernel=kernel, replication=True)
    assert np.max(np.abs(diag["j1_catalysed_by_genotype"])) < 1e-15
    assert np.ptp(diag["replication_rate_constants"]) < 1e-15


def test_nonreplicating_controls_have_no_hidden_population_change():
    cfg = small_config()
    result = simulate_v02("M", cfg)
    assert result["initial_catalyst_concentration"] == result["final_catalyst_concentration"]
    assert result["max_free_energy_balance_residual"] < 1e-9


def test_drifting_target_can_be_simulated_without_clipping():
    cfg = small_config(mutation_rate=0.1)
    result = simulate_v02("L", cfg, target_schedule=[(0.0, 0), (10.0, 3)])
    assert min(row["fuel"] for row in result["trajectory"]) > 0
    assert min(row["atp"] for row in result["trajectory"]) > 0
    assert min(row["monomer"] for row in result["trajectory"]) > 0
    assert result["max_free_energy_balance_residual"] < 1e-8
    assert abs(result["work_balance_residual"]) < 1e-5
    assert abs(result["cumulative_free_energy_balance_residual"]) < 1e-5
