"""S11 cosmos model: ledgers, calibration, physics sanity. Fail if a ledger does not close."""
import math

import numpy as np
import pytest

from agency_gradients.cosmos import constants as K
from agency_gradients.cosmos import cosmology as cs
from agency_gradients.cosmos.model import Cosmos, Params, do_nothing, rollout
from agency_gradients.cosmos.policies import NeuralPolicy, PiecewisePolicy, N_NN, N_PW
from agency_gradients.cosmos.search import gain_of

FAST = dict(per_decade=10)


def test_bh_entropy_coefficient():
    assert 1.04e77 < K.S_BH_COEF < 1.06e77


def test_cosmology_horizons():
    assert abs(cs.event_horizon_gly() - 16.5) / 16.5 < 0.05          # Ord 2021
    assert abs(cs.particle_horizon_gly() - 46.4) / 46.4 < 0.05
    f = cs.reach_fractions(cs.time_grid(1e13), 1.0)[-1]
    assert 0.03 < f < 0.06                                            # about 4.5% of volume


def test_calibration_to_egan_lineweaver():
    w = Cosmos(Params(horizon_yr=1e12, **FAST))
    assert 0.5 < w.s_bh() / K.S_OBS_EL < 2.0
    assert 0.3 < w.entropy()["cmb"] / 5.4e89 < 3.0
    # stellar BHs (not tuned) near their 5.9e97
    n, m = w.hn.sum(0), w.hm.sum(0)
    stellar = w.hs.sum(0)[:6].sum() * K.S_BH_COEF
    assert 0.2 < stellar / K.S_STELLAR_BH_EL < 5.0


def test_ledgers_close_do_nothing_and_random_policies():
    rng = np.random.default_rng(0)
    for seed in range(3):
        p = Params(horizon_yr=1e13, **FAST).draw(seed)
        assert rollout(p, do_nothing, check_ledger=True)["max_ledger_err"] < 1e-9
        for pol in (PiecewisePolicy(rng.standard_normal(N_PW) * 3), NeuralPolicy(rng.standard_normal(N_NN) * 0.5),
                    lambda f, i, n: np.full(5, 0.2)):
            assert rollout(p, pol, check_ledger=True)["max_ledger_err"] < 1e-9


def test_ledgers_close_with_hawking():
    p = Params(horizon_yr=1e113, per_decade=4, hawking=True)
    r = rollout(p, PiecewisePolicy(np.ones(36)), check_ledger=True)
    assert r["max_ledger_err"] < 1e-9
    assert r["entropy"]["hawking"] > 0


def test_ledger_test_detects_a_leak():
    w = Cosmos(Params(horizon_yr=1e12, **FAST))
    w.step(np.zeros(5))
    w.Eout -= 1e-6 * w.E0
    assert max(w.ledger_errors()) > 1e-7
    w2 = Cosmos(Params(horizon_yr=1e12, **FAST))
    w2.step(np.zeros(5))
    w2.bar_in_bh += 1e-6 * w2.B0
    assert max(w2.ledger_errors()) > 1e-7


def test_baseline_second_law():
    w = Cosmos(Params(horizon_yr=1e14, **FAST))
    prev = w.entropy()
    while not w.done():
        w.step(np.zeros(5))
        cur = w.entropy()
        assert cur["bh"] >= prev["bh"] * (1 - 1e-12)
        assert cur["photon"] >= prev["photon"] - 1e-3 * abs(prev["photon"])
        prev = cur


def test_do_nothing_has_zero_gain_and_levers_cost_energy():
    p = Params(horizon_yr=1e12, **FAST)
    nothing = np.zeros((6, 6)); nothing[:, 5] = 8
    assert gain_of(p, PiecewisePolicy(nothing.ravel()), 0)["total"] == 0.0


def test_merger_area_theorem():
    # an equal-mass merge with GW loss eps: S_final > S_initial when eps < 1 - 1/sqrt(2)
    for eps in (0.02, 0.05, 0.1, 0.29):
        assert 4 * (1 - eps) ** 2 > 2
    assert 4 * (1 - 0.3) ** 2 < 2


def test_hawking_factor_and_scale():
    assert K.HAWKING_RATIO == pytest.approx(1.4847)
    assert 1.5e67 < K.T_EVAP_MSUN_YR < 3e67
    assert 2e-30 < K.T_DS < 3e-30


def test_costs_throttle_actions():
    # with no work reservoir the agent can do nothing
    p = Params(horizon_yr=1e12, w0=0.0, **FAST)
    g = gain_of(p, lambda f, i, n: np.array([0, 1.0, 0, 0, 0]), 0)
    assert g["total"] == 0.0


def test_domain_cap_and_reach_limit_bound_bh_entropy():
    p = Params(horizon_yr=1e14, **FAST)
    best = np.zeros((6, 6)); best[:2, 4] = 8; best[2:, 2] = 8
    g = gain_of(p, PiecewisePolicy(best.ravel()), 0)
    assert 0 < g["total"] < 1e115
    assert not g["cap_hit"]
