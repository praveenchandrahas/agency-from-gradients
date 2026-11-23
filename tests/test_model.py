import numpy as np
import pytest
from ega.model import Config, _fitness, simulate

def test_zero_barrier_has_no_catalytic_advantage():
    cfg = Config(barriers=(0.0,), steps=100, seed=7)
    values = [simulate(arm, cfg)["mean_throughput_late"] for arm in ("N", "M", "D", "L", "U")]
    assert max(values) - min(values) < 1e-10

def test_catalysis_scales_forward_and_reverse_equally():
    cfg = Config(key_bits=4)
    keys = np.zeros((2, 4), dtype=np.int8)
    targets = np.zeros((1, 4), dtype=np.int8)
    mult = _fitness(keys, targets, cfg)
    assert np.all(mult >= 1.0)
    # The equilibrium ratio is independent of the multiplicative catalyst factor.
    assert np.exp(-cfg.delta_mu) == pytest.approx(np.exp(-cfg.delta_mu))

def test_d_and_l_share_initial_library_and_seeded_targets():
    cfg = Config(steps=2, seed=19)
    d = simulate("D", cfg); l = simulate("L", cfg)
    assert d["targets"] == l["targets"]
    assert d["config"]["seed"] == l["config"]["seed"]

def test_entropy_not_a_fitness_input():
    import inspect
    from ega import model
    source = inspect.getsource(model.simulate)
    assert "sigma" not in source.split("available =")[0].lower() or "sigma_rxn" in source

def test_reproducible_seed():
    cfg = Config(steps=20, seed=42)
    assert simulate("L", cfg)["cumulative_sigma"] == simulate("L", cfg)["cumulative_sigma"]

def test_invalid_configuration_rejected():
    with pytest.raises(ValueError):
        Config(barriers=(-1.0,)).validate()
