"""Gates G1 to G6 of SPEC.md. If any fails, no result from this engine counts."""
import math

import numpy as np
import pytest

from locks import ARMS, Config, World, run, energy_error, fuel_error, g_fn

CLOSED = dict(dil=0.0, B=(0.0,), dt=0.01)


def relax(w, steps):
    led = None
    for _ in range(steps):
        led = w.step()
    return led


# G1. A closed box relaxes to its equilibrium and stops producing entropy.
def test_g1_closed_box_relaxes_to_equilibrium():
    w = World(Config(arm="N", **CLOSED), seed=1000)
    led = relax(w, 3000)
    ratio = w.W[0] / w.F[0]
    assert ratio == pytest.approx(math.exp(6.0), rel=1e-9)
    assert led["released"] < 1e-12
    assert w.F[0] + w.W[0] == pytest.approx(201.0, rel=1e-12)   # nothing in, nothing out


def test_g1_free_energy_never_rises_in_a_closed_box():
    w = World(Config(arm="N", dil=0.0, B=(4.0,)), seed=1000)
    g = g_fn(w.F, w.W, w.dmu0)[0]
    for _ in range(2000):
        w.step()
        g1 = g_fn(w.F, w.W, w.dmu0)[0]
        assert g1 <= g + 1e-9
        g = g1


# G2. Catalysis changes speed, never destination.
@pytest.mark.parametrize("arm", ["M", "U"])
def test_g2_catalysts_do_not_move_the_equilibrium(arm):
    base = World(Config(arm="N", dil=0.0, B=(6.0,)), seed=1003)
    cat = World(Config(arm=arm, dil=0.0, B=(6.0,), n_fixed=500), seed=1003)
    relax(base, 400_000 // 100)   # slow: may not be there yet
    relax(cat, 4000)
    # the catalysed box reaches the same composition as the analytic equilibrium
    T = 201.0
    em = math.exp(-6.0)
    assert cat.F[0] == pytest.approx(T * em / (1 + em), rel=1e-6)
    # and the uncatalysed box is heading to the same place, more slowly
    assert base.F[0] > cat.F[0]


def test_g2_catalysis_scales_forward_and_backward_alike():
    """Start a closed box at equilibrium. With or without catalysts, nothing moves."""
    em = math.exp(-6.0)
    for arm in ("N", "M", "U"):
        w = World(Config(arm=arm, dil=0.0, B=(2.0,), n_fixed=500), seed=1001)
        w.F[:] = 201.0 * em / (1 + em)
        w.W[:] = 201.0 - w.F
        led = relax(w, 500)
        assert led["released"] < 1e-12
        assert w.W[0] / w.F[0] == pytest.approx(1 / em, rel=1e-9)


# G3. Ledgers close every step, in every arm, with everything switched on.
@pytest.mark.parametrize("arm", ARMS)
def test_g3_ledgers_close_every_step(arm):
    cfg = Config(arm=arm, B=(10.0, 4.0), dmu0=(6.0, 4.0), f_in=(200.0, 50.0),
                 n_fixed=300, drift=0.5, mu=0.02)
    w = World(cfg, seed=1005)
    for _ in range(3000):
        led = w.step()
        scale = max(1.0, led["released"])
        assert abs(energy_error(led)) < 1e-9 * scale
        assert np.all(np.abs(fuel_error(led)) < 1e-9 * 250)


def test_g3_fixed_catalysts_store_nothing():
    for arm in ("M", "U"):
        w = World(Config(arm=arm, n_fixed=300), seed=1000)
        for _ in range(500):
            led = w.step()
            assert led["stored_after"] == 0.0
            assert led["heat"] == pytest.approx(led["released"], rel=1e-12)


# G4. Entropy production from the fluxes agrees with the free-energy books.
@pytest.mark.parametrize("arm,B", [("N", 0.0), ("N", 8.0), ("M", 8.0), ("U", 12.0), ("L", 8.0)])
def test_g4_flux_matches_books(arm, B):
    w = World(Config(arm=arm, B=(B,), n_fixed=300), seed=1002)
    for _ in range(300):
        led = w.step(check_flux=True)
        if led["released"] > 1e-9:
            assert led["sigma_flux"] == pytest.approx(led["released"], rel=1e-4)


# G5. No step produces negative entropy.
@pytest.mark.parametrize("arm", ARMS)
def test_g5_entropy_production_never_negative(arm):
    w = World(Config(arm=arm, B=(8.0,), n_fixed=300, drift=0.5, mu=0.02), seed=1004)
    for _ in range(3000):
        led = w.step()
        assert led["released"] >= -1e-12
        assert led["heat"] >= -1e-12


# G6. Controls.
def test_g6_perfect_key_is_held():
    cfg = Config(arm="L", B=(12.0,), init="perfect")
    r = run(cfg, seed=1000, t_end=200.0, t_late=150.0, rec_every=50.0)
    assert not r["extinct"]
    assert r["series"][-1]["key_dist"] < 1.0


def test_g6_life_without_mutation_is_the_fire():
    a = run(Config(arm="D", B=(10.0,)), seed=1009, t_end=60.0, t_late=40.0)
    b = run(Config(arm="L", B=(10.0,), mu=0.0), seed=1009, t_end=60.0, t_late=40.0)
    for key in ("sigma_late", "released_late", "n_late", "cum_heat", "stored_end"):
        assert a[key] == b[key]
    assert a["series"] == b["series"]


def test_g6_d_and_l_start_from_the_same_library():
    d = World(Config(arm="D"), seed=1011)
    l = World(Config(arm="L"), seed=1011)
    assert np.array_equal(d.key, l.key) and np.array_equal(d.lock, l.lock)


def test_an_empty_world_is_the_passive_world():
    """An extinct world must score the passive baseline, not zero."""
    n = World(Config(arm="N", B=(8.0,)), seed=1000)
    d = World(Config(arm="D", B=(8.0,)), seed=1000)
    d.key, d.mark, d.e = d.key[:0], d.mark[:0], d.e[:0]
    for _ in range(200):
        a, b = n.step(), d.step()
        assert a["released"] == pytest.approx(b["released"], rel=1e-12)
        assert a["released"] > 0.0


def test_deterministic_given_seed():
    cfg = Config(arm="L", B=(8.0,), drift=0.2)
    r1 = run(cfg, seed=1007, t_end=30.0, t_late=20.0)
    r2 = run(cfg, seed=1007, t_end=30.0, t_late=20.0)
    assert r1 == r2
    assert run(cfg, seed=1008, t_end=30.0, t_late=20.0) != r1


# G4b. In steady state, reaction plus mixing entropy equals free energy carried in minus carried out.
# Flow and reaction are split into substeps, which shifts the state the balance is read at by O(dt).
# So the gate asks two things: sigma is converged at the production step, and the balance error
# shrinks in proportion to dt (it is the splitting, not the books).
def _sigma_and_balance(cfg):
    r = run(cfg, seed=1003, t_end=40.0, t_late=30.0, rec_every=10.0)
    w = World(cfg, seed=1003)
    for _ in range(int(round(40.0 / cfg.dt))):
        w.step()
    g_in = g_fn(np.array(cfg.f_in), np.full(1, cfg.w_in), w.dmu0)[0]
    bal = cfg.dil * (g_in - g_fn(w.F, w.W, w.dmu0)[0])
    return r["sigma_late"], bal


@pytest.mark.parametrize("arm,B", [("N", 0.0), ("N", 4.0), ("U", 12.0), ("M", 8.0)])
def test_g4b_total_entropy_matches_the_free_energy_balance(arm, B):
    out = {dt: _sigma_and_balance(Config(arm=arm, B=(B,), n_fixed=300, dt=dt)) for dt in (0.01, 0.005, 0.0025)}
    s10, s25 = out[0.01][0], out[0.0025][0]
    assert s10 == pytest.approx(s25, rel=5e-4)                      # converged: bias under 0.05%
    err = {dt: abs(sg - bal) / bal for dt, (sg, bal) in out.items()}
    assert err[0.0025] < 1.5e-3
    if err[0.01] > 1e-5:                                            # first order: halves with dt
        assert err[0.005] == pytest.approx(err[0.01] / 2, rel=0.1)
        assert err[0.0025] == pytest.approx(err[0.01] / 4, rel=0.1)


def test_mixing_entropy_is_zero_when_nothing_reacts():
    w = World(Config(arm="N", B=(60.0,)), seed=1000)
    for _ in range(200):
        assert abs(w.step()["sigma_mix"]) < 1e-9
