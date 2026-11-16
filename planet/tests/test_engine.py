from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from planet import Config, Options, PUBLISHED_COLUMNS, SCENARIOS, build_world, run, v0_2

CFG = Config()
WORLD = build_world(CFG)
SHORT = replace(CFG, generations=25)


def published(df):
    return df[PUBLISHED_COLUMNS].reset_index(drop=True)


@pytest.mark.parametrize("key", list(SCENARIOS))
@pytest.mark.parametrize("rep", [0, 3])
def test_engine_equals_published_model_bit_for_bit(key, rep):
    ref, _ = v0_2.run_one(key, rep, SHORT, WORLD)
    got, _ = run(key, rep, SHORT, WORLD)
    pd.testing.assert_frame_equal(published(got), ref.reset_index(drop=True), check_exact=True)


@pytest.mark.parametrize("key", ["volatile_shifting", "strong_predictable_no_cognition"])
def test_engine_equals_published_model_over_the_full_220_generations(key):
    ref, _ = v0_2.run_one(key, 1, CFG, WORLD)
    got, _ = run(key, 1, CFG, WORLD)
    pd.testing.assert_frame_equal(published(got), ref.reset_index(drop=True), check_exact=True)


def test_a_longer_run_repeats_the_shorter_one_exactly():
    short, _ = run("strong_predictable_hotspots", 2, SHORT, WORLD)
    longer, _ = run("strong_predictable_hotspots", 2, replace(CFG, generations=40), WORLD)
    cols = [c for c in short.columns if not c.startswith("births_")]   # births of the last row are not realised
    pd.testing.assert_frame_equal(longer.iloc[:26][cols].reset_index(drop=True), short[cols], check_exact=True)


def test_reproduces_numbers_recorded_in_the_paper_repository():
    # results/entropy_agency_v0_2_cognitive_ablation.csv, volatile environment, replicate 0
    cog, _ = run("volatile_shifting", 0, CFG, WORLD)
    ctl, _ = run("volatile_no_cognition", 0, CFG, WORLD)
    assert int(cog.population.iloc[-1]) == 1440
    assert cog.biotic_power_harnessed_TW.iloc[-1] == pytest.approx(57.67283614605741, rel=1e-9)
    assert ctl.biotic_power_harnessed_TW.iloc[-1] == pytest.approx(135.51413137529374, rel=1e-9)
    assert cog.biotic_power_per_entity_GW.iloc[-1] == pytest.approx(40.050580656984316, rel=1e-9)


def test_same_seed_same_run_and_other_seed_other_run():
    opt = Options(carrier_fraction=0.5)
    a, _ = run("volatile_shifting", 0, SHORT, WORLD, opt)
    b, _ = run("volatile_shifting", 0, SHORT, WORLD, opt)
    c, _ = run("volatile_shifting", 1, SHORT, WORLD, opt)
    pd.testing.assert_frame_equal(a, b, check_exact=True)
    assert not a.population.equals(c.population)


def test_population_bookkeeping_closes_every_generation():
    df, _ = run("strong_predictable_hotspots", 0, replace(CFG, generations=60), WORLD, Options(carrier_fraction=0.5))
    nxt = df.population.to_numpy()[1:]
    assert np.array_equal(nxt, (df.survivors + df.births).to_numpy()[:-1])
    assert np.array_equal(df.n_carriers.to_numpy()[1:], (df.survivors_c + df.births_c).to_numpy()[:-1].astype(int))
    assert np.allclose((df.births_c + df.births_n).to_numpy()[:-1], df.births.to_numpy()[:-1])
    assert np.allclose(df.harvest_units_c + df.harvest_units_n, df.total_biotic_harvest_units)


def test_mixed_start_has_the_requested_carriers_and_the_flag_never_mutates():
    for f, n in ((0.1, 26), (0.5, 130), (0.9, 234)):
        df, _ = run("weakly_variable", 0, replace(CFG, generations=3), WORLD, Options(carrier_fraction=f))
        assert df.n_carriers.iloc[0] == n and df.population.iloc[0] == 260
    none, _ = run("weakly_variable", 0, SHORT, WORLD, Options(carrier_fraction=0.0))
    assert (none.n_carriers == 0).all() and (none.mean_action == 0).all() and (none.mean_sensing == 0).all()
    allc, _ = run("weakly_variable", 0, SHORT, WORLD, Options(carrier_fraction=1.0))
    assert (allc.n_carriers == allc.population).all()


def test_non_carriers_keep_agency_at_zero_in_a_mixed_world():
    df, _ = run("volatile_shifting", 0, SHORT, WORLD, Options(carrier_fraction=0.5))
    # population mean of a trait = carrier share x carrier mean, if non-carriers are exactly zero
    assert np.allclose(df.mean_action, df.carrier_fraction * df.action_c)


def test_switches_do_what_they_say():
    off, _ = run("strong_predictable_hotspots", 0, SHORT, WORLD, Options(carrier_fraction=0.5, eq4_bonus=False))
    assert (off.mean_behaviour_gain == 0).all()
    still, _ = run("strong_predictable_hotspots", 0, SHORT, WORLD,
                   Options(carrier_fraction=0.5, directed_movement=False))
    assert still.choice_true_best.isna().all() and (still.mean_behaviour_gain > 0).all()
    on, _ = run("strong_predictable_hotspots", 0, SHORT, WORLD, Options(carrier_fraction=0.5))
    assert on.choice_true_best.notna().all()


def test_markers_stay_in_bounds_and_start_like_the_agency_traits():
    df, _ = run("weakly_variable", 0, SHORT, WORLD)
    cols = [f"marker_{k}" for k in range(1, 6)]
    assert df[cols].to_numpy().min() >= 0 and df[cols].to_numpy().max() <= 1
    assert df.marker_composite.iloc[0] == pytest.approx(0.068, abs=0.01)
    assert df.mean_agency_composite.iloc[0] == pytest.approx(0.068, abs=0.01)


def test_mixed_runs_see_the_same_weather_as_the_published_runs():
    pure, _ = run("strong_predictable_hotspots", 4, SHORT, WORLD)
    mixed, _ = run("strong_predictable_hotspots", 4, SHORT, WORLD, Options(carrier_fraction=0.5))
    # the abiotic planet depends on the weather only
    assert np.array_equal(pure.abiotic_absorbed_power_W, mixed.abiotic_absorbed_power_W)
    assert np.array_equal(pure.spatial_opportunity_cv, mixed.spatial_opportunity_cv)


def test_snapshots_count_every_entity():
    df, snaps = run("volatile_shifting", 0, SHORT, WORLD, Options(snapshot_generations=(10, 25)))
    assert [s["generation"] for s in snaps] == [10, 25]
    for s in snaps:
        pop = int(df.population[df.generation == s["generation"]].iloc[0])
        assert s["net_hist"].sum() == pop and s["patch_count"].sum() == pop
