import numpy as np
import pytest

from starlight import Config, World, run, ledger_error

FULL = Config(speed=0.3, ramp_steps=50, furnace_band=True, c_furnace=0.01,
              mutable=("a", "m", "g", "f"), m0=0.3, g0=0.5, f0=0.4, n0=200)


def test_ledger_closes_every_step_with_everything_on():
    w = World(FULL, seed=1)
    for _ in range(600):
        led = w.step()
        assert abs(ledger_error(led)) < 1e-9 * max(1.0, led["emitted"])
        assert 0.0 <= led["captured"] <= led["emitted"] + 1e-12
        assert 0.0 <= led["captured_b"] <= led["emitted_b"] + 1e-12
    assert w.n > 0


def test_deterministic_given_seed():
    r1 = run(FULL, seed=7, steps=400, rec_every=100)
    r2 = run(FULL, seed=7, steps=400, rec_every=100)
    assert r1 == r2
    r3 = run(FULL, seed=8, steps=400, rec_every=100)
    assert r1 != r3


def test_darkness_means_extinction_and_all_stored_energy_becomes_heat():
    cfg = Config(patch_peak=0.0, n0=50)
    # patch_peak 0 gives no light at all, so seed positions by hand
    w = World.__new__(World)
    w.cfg, w.rng, w.t = cfg, np.random.default_rng(0), 0
    w.x = np.arange(cfg.n_sites, dtype=float)
    w.centres = np.array([10.0])
    w.light = np.zeros(cfg.n_sites)
    w.pos = np.zeros(50, dtype=int)
    w.e = np.full(50, 1.0)
    w.a = np.full(50, 0.3); w.m = np.zeros(50); w.g = np.zeros(50); w.f = np.zeros(50)
    w.extinct = False
    start, heat = w.stored(), 0.0
    for _ in range(500):
        heat += w.step()["heat"]
    assert w.n == 0 and w.extinct
    assert heat == pytest.approx(start, rel=1e-12)


def test_only_mutable_traits_change_and_all_stay_in_bounds():
    cfg = Config(mutable=("a",), m0=0.2, g0=0.3, f0=0.1, mut_sd=0.3)
    w = World(cfg, seed=3)
    for _ in range(400):
        w.step()
    assert w.n > 0
    assert np.all(w.m == 0.2) and np.all(w.g == 0.3) and np.all(w.f == 0.1)
    assert w.a.min() >= 0.0 and w.a.max() <= cfg.a_max
    assert w.a.std() > 0.0


def test_single_organism_intake_matches_beer_lambert():
    cfg = Config(hazard=0.0, n0=1, a0=0.7, e_rep=1e9)
    w = World(cfg, seed=0)
    site = int(w.pos[0])
    led = w.step()
    expect = w.light[site] * (1.0 - np.exp(-cfg.k_ext * 0.7))
    assert led["captured"] == pytest.approx(expect, rel=1e-12)


def test_shading_shares_light_in_proportion_to_absorber():
    cfg = Config(hazard=0.0, n0=2, e_rep=1e9, c_base=0.0, c_abs=0.0)
    w = World(cfg, seed=0)
    w.pos[:] = int(np.argmax(w.light))
    w.a[:] = [0.2, 0.6]
    w.e[:] = 1.0            # e_rep is huge here; keep energies small so the float maths is exact
    e0 = w.e.copy()
    w.step()
    gain = w.e - e0
    assert gain[1] / gain[0] == pytest.approx(3.0, rel=1e-12)


def test_division_conserves_energy_and_copies_traits():
    cfg = Config(hazard=0.0, n0=1, c_base=0.0, c_abs=0.0, patch_peak=0.0, mutable=())
    w = World.__new__(World)
    w.cfg, w.rng, w.t = cfg, np.random.default_rng(0), 0
    w.x = np.arange(cfg.n_sites, dtype=float)
    w.centres = np.array([10.0]); w.light = np.zeros(cfg.n_sites)
    w.pos = np.array([5]); w.e = np.array([3.0])
    w.a = np.array([0.4]); w.m = np.zeros(1); w.g = np.zeros(1); w.f = np.zeros(1)
    w.extinct = False
    led = w.step()
    assert w.n == 2 and led["births"] == 1
    assert w.e.tolist() == [1.5, 1.5]
    assert w.a.tolist() == [0.4, 0.4]
    assert abs(int(w.pos[1]) - 5) <= 1


def test_sensing_movers_go_up_the_gradient():
    cfg = Config(hazard=0.0, n0=200, m0=1.0, g0=1.0, e_rep=1e9, n_patches=1, patch_width=10.0)
    w = World(cfg, seed=0)
    centre = int(round(w.centres[0]))
    w.pos[:] = centre - 12                      # all on the left slope
    w.step()
    assert np.all(w.pos == centre - 11)
    w.pos[:] = centre + 12                      # all on the right slope
    w.step()
    assert np.all(w.pos == centre + 11)


def test_blind_movers_have_no_net_direction():
    cfg = Config(hazard=0.0, n0=4000, m0=1.0, g0=0.0, e_rep=1e9, n_patches=1, patch_width=10.0)
    w = World(cfg, seed=0)
    centre = int(round(w.centres[0]))
    w.pos[:] = centre - 12
    w.step()
    assert abs(float((w.pos - (centre - 12)).mean())) < 0.06


def test_furnace_does_not_touch_the_usable_band():
    base = Config(hazard=0.0, n0=300, e_rep=1e9)
    hot = Config(hazard=0.0, n0=300, e_rep=1e9, furnace_band=True, f0=0.8)
    a, b = World(base, seed=5), World(hot, seed=5)
    la, lb = a.step(), b.step()
    assert la["captured"] == pytest.approx(lb["captured"], rel=1e-12)
    assert np.allclose(a.e, b.e)
    assert lb["captured_b"] > 0.0 and la["captured_b"] == 0.0


def test_light_field_wraps_and_ramp_reaches_final_speed():
    cfg = Config(speed=0.5, ramp_steps=100, n_patches=2)
    w = World(cfg, seed=0)
    total0 = w.light.sum()
    for _ in range(100):
        w.step()
    assert w.current_speed() == pytest.approx(0.5)
    for _ in range(2000):
        w.step()
    assert w.light.sum() == pytest.approx(total0, rel=0.02)   # nothing lost at the wrap
