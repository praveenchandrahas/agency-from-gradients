import json

import numpy as np

from agency_gradients.experiments import s0_reanalysis
from agency_gradients.stats import bootstrap_diff_ci, bootstrap_mean_ci, factor_effect


def test_bootstrap_mean_covers_truth():
    rng = np.random.default_rng(0)
    m, lo, hi = bootstrap_mean_ci(rng.normal(5, 1, 200))
    assert lo < 5 < hi


def test_diff_ci_excludes_zero_for_real_gap():
    rng = np.random.default_rng(1)
    d, lo, hi = bootstrap_diff_ci(rng.normal(1, 1, 100), rng.normal(0, 1, 100))
    assert lo > 0


def test_diff_ci_includes_zero_for_null():
    rng = np.random.default_rng(2)
    d, lo, hi = bootstrap_diff_ci(rng.normal(0, 1, 60), rng.normal(0, 1, 60))
    assert lo < 0 < hi


def test_factor_effect_recovers_planted_effect():
    rng = np.random.default_rng(3)
    rows = []
    for a in (0, 1):
        for b in (0, 1):
            for _ in range(40):
                rows.append(dict(a=a, b=b, y=2.0 * a + 0.0 * b + rng.normal(0, 0.5)))
    e_a, lo_a, hi_a = factor_effect(rows, "a", "y", ("a", "b"), n_boot=300)
    e_b, lo_b, hi_b = factor_effect(rows, "b", "y", ("a", "b"), n_boot=300)
    assert lo_a < 2.0 < hi_a
    assert lo_b < 0.0 < hi_b


def _fake_run(path, cond, forage_mean, n_gen=8, n_agents=20, seed=0):
    rng = np.random.default_rng(seed)
    gens = [rng.normal([forage_mean, 0.4, 0.5, 0.5, 0.5], 0.05, (n_agents, 5)).tolist() for _ in range(n_gen)]
    path.write_text(json.dumps({"meta": {"cond": cond}, "history": {"genomes": gens}}))


def test_s0_finds_trajectory_and_separates_conditions(tmp_path):
    _fake_run(tmp_path / "evo_entropy_s0.json", "entropy", 0.8, seed=1)
    _fake_run(tmp_path / "evo_survival_s0.json", "survival", 0.3, seed=2)
    files = sorted(str(p) for p in tmp_path.glob("evo_*.json"))
    rows, summary = s0_reanalysis.analyse(files, tier2_threshold=0.6)
    assert summary["entropy"]["forage"][0] > summary["survival"]["forage"][0]
    assert summary["entropy"]["inelig"][0] > 0.9 and summary["survival"]["inelig"][0] < 0.1
    assert len(rows) == 16


def test_s0_fails_loudly_on_unknown_schema(tmp_path):
    p = tmp_path / "evo_entropy_x.json"
    p.write_text(json.dumps({"nothing": [1, 2, 3]}))
    try:
        s0_reanalysis.analyse([str(p)])
    except SystemExit as e:
        assert "No genome trajectory" in str(e)
    else:
        raise AssertionError("expected SystemExit")
