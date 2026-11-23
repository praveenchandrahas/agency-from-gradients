import inspect
import numpy as np
import pytest

from ega.model import Config, _reaction_step, simulate


def test_zero_barrier_removes_catalytic_advantage():
    cfg = Config(barriers=(0.0,), steps=100, seed=7)
    values = [simulate(arm, cfg)["mean_throughput_late"]
              for arm in ("N", "M", "D", "L", "U", "A")]
    assert max(values) - min(values) < 1e-10


def test_catalysts_do_not_change_equilibrium_composition():
    cfg = Config(barriers=(8.0,), steps=10, seed=4)
    fuel_eq = 1.0 / (1.0 + np.exp(cfg.delta_mu))
    targets = np.zeros((1, cfg.key_bits), dtype=np.int8)
    catalysts = np.zeros((10, cfg.key_bits), dtype=np.int8)
    _, flux, sigma_rxn, sigma_exchange = _reaction_step(
        fuel_eq, catalysts, targets, np.array([8.0]), cfg
    )
    assert float(np.sum(flux)) < 1e-12
    assert sigma_rxn < 1e-10
    assert sigma_exchange < 1e-10


def test_entropy_production_is_nonnegative():
    cfg = Config(barriers=(2.0, 8.0), locks=2, steps=50, seed=2)
    result = simulate("L", cfg)
    for row in result["trajectory"]:
        assert row["sigma_reaction"] >= 0
        assert row["sigma_exchange"] >= -1e-12
        assert row["sigma_total"] >= -1e-12


def test_d_and_l_share_initial_targets_and_seed():
    cfg = Config(steps=2, seed=19)
    d = simulate("D", cfg)
    l = simulate("L", cfg)
    assert d["targets"] == l["targets"]
    assert d["config"]["seed"] == l["config"]["seed"]


def test_entropy_is_not_used_in_reproductive_rule():
    source = inspect.getsource(simulate)
    reproductive_section = source.split('if arm in ("D", "L")')[1].split('elif arm == "A"')[0]
    assert "sigma" not in reproductive_section.lower()


def test_reproducible_seed():
    cfg = Config(steps=20, seed=42)
    assert simulate("L", cfg)["cumulative_sigma"] == simulate("L", cfg)["cumulative_sigma"]


def test_invalid_configuration_rejected():
    with pytest.raises(ValueError):
        Config(barriers=(-1.0,)).validate()
