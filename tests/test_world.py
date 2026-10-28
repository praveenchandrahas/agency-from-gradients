import numpy as np
import pytest

from agency_gradients import Config, World, viability_probe
from agency_gradients.controls import oracle_policy
from agency_gradients.world import n_params, policy_logits, random_genomes

FAST = dict(steps=300)


@pytest.mark.parametrize("kw", [
    {}, dict(mortality=False), dict(succession=False), dict(scarcity=False),
    dict(heredity=False), dict(selection="entropy"), dict(selection="task"),
    dict(selection="drift"), dict(policy="mlp"), dict(patchiness=0.0),
])
def test_energy_ledger_closes(kw):
    w = World(Config(**FAST, **kw), seed=3)
    for _ in range(300):
        w.step()
    assert abs(w.ledger_residual()) < 1e-6


def test_ledger_closes_through_succession_conversion():
    # force fast drainage so conversions actually happen inside the test
    cfg = Config(steps=600, stock1=5.0, harvest1=3.0, succession=True)
    w = World(cfg, seed=1)
    w.policy = oracle_policy
    w.run()
    assert w.converted > 0
    assert abs(w.ledger_residual()) < 1e-6


def test_deterministic_given_seed():
    a = World(Config(**FAST), 7).run().summary()
    b = World(Config(**FAST), 7).run().summary()
    c = World(Config(**FAST), 8).run().summary()
    assert a == b or all((a[k] == b[k]) or (a[k] != a[k] and b[k] != b[k]) for k in a)
    assert a["entropy_rate"] != c["entropy_rate"]


def test_mortality_off_means_no_deaths():
    w = World(Config(**FAST, mortality=False), 2).run()
    assert sum(w.log["deaths"]) == 0
    assert w.alive.sum() > 0


def test_mortality_on_has_deaths():
    w = World(Config(steps=600), 2).run()
    assert sum(w.log["deaths"]) > 0


def test_succession_controls_when_tier2_exists():
    off = World(Config(succession=False), 5)
    on = World(Config(succession=True), 5)
    assert (off.ttype == 2).sum() == off.cfg.n_tier2
    assert (on.ttype == 2).sum() == 0 and on.t2_budget == on.cfg.n_tier2


def test_heredity_off_gives_unrelated_children():
    cfg_on = Config(steps=1, selection="persistence", heredity=True)
    cfg_off = cfg_on.with_(heredity=False)
    dists = {}
    for name, cfg in (("on", cfg_on), ("off", cfg_off)):
        w = World(cfg, 4)
        w.energy[w.alive] = cfg.repro_thresh + 5          # everyone can reproduce
        parents = np.flatnonzero(w.alive).copy()
        pg = w.genome[parents].copy()
        k = w._reproduce()
        assert k > 0
        kids = np.flatnonzero(w.alive & ~np.isin(np.arange(cfg.max_pop), parents))
        # compare each child to its (position-matched) parent genome set
        d = np.mean([np.min(np.linalg.norm(pg - w.genome[c], axis=1)) for c in kids])
        dists[name] = d
    assert dists["on"] < dists["off"]


def test_scarcity_off_supports_more_people():
    a = World(Config(steps=800), 1).run().summary()
    b = World(Config(steps=800, scarcity=False), 1).run().summary()
    assert b["pop_mean_late"] > a["pop_mean_late"]


def test_policy_shapes_and_sampling():
    rng = np.random.default_rng(0)
    for pol in ("equivariant", "mlp"):
        g = random_genomes(rng, 5, pol)
        assert g.shape == (5, n_params(pol))
        obs = rng.random((5, 37))
        assert policy_logits(g, obs, pol).shape == (5, 6)


def test_oracle_beats_random_walkers():
    cfg = Config(steps=2500, selection="drift")
    base = World(cfg, 11).run().summary()
    w = World(cfg, 11)
    w.policy = oracle_policy
    orc = w.run().summary()
    assert orc["entropy_rate"] > base["entropy_rate"]
    assert orc["t2_reached"] == 1


def test_viability_probe_runs_and_is_bounded():
    w = World(Config(steps=400), 3).run()
    r = viability_probe(w, n=16, horizon=40)
    for k in ("evolved_recovered", "random_recovered", "delta_recovered"):
        assert k in r
    assert 0 <= r["evolved_survived"] <= 1


def test_probe_does_not_mutate_source_world():
    w = World(Config(steps=200), 3).run()
    before = (w.alive.copy(), w.energy.copy(), w.commons.copy(), w.t)
    viability_probe(w, n=8, horizon=20)
    assert np.array_equal(before[0], w.alive) and np.array_equal(before[1], w.energy)
    assert np.array_equal(before[2], w.commons) and before[3] == w.t


def test_passive_world_has_no_agents_and_positive_leak():
    from agency_gradients import passive_entropy_rate
    assert passive_entropy_rate(Config()) > 0


def test_kappa_one_collapses_capture_ratio_towards_one():
    # accounting sanity: with equal entropy per unit energy, agents cannot manufacture CR >> 1
    from agency_gradients.runner import _passive
    cfg = Config(steps=3000, kappa=1.0)
    s = World(cfg, 2).run().summary(passive_rate=_passive(cfg))
    assert 0.7 < s["capture_ratio"] < 1.15


def test_contributor_sharing_closes_ledger_and_rewards_investors():
    import numpy as np
    from agency_gradients.config import Config
    from agency_gradients.world import World

    cfg = Config(steps=600, deposit_share="contributor")
    w = World(cfg, seed=3)
    for _ in range(600):
        w.step()
    assert abs(w.ledger_residual()) < 1e-6
    assert np.all(w.contrib[~w.alive] >= 0)


V2 = dict(world_v2=True, steps=500)


def test_v1_default_unchanged_by_v2_code():
    # pinned from the confirmatory run (seed 0, 20000 steps would be slow; short run pinned here)
    a = World(Config(steps=300), 0).run().summary()
    b = World(Config(steps=300, world_v2=False), 0).run().summary()
    assert a == b


import pytest


@pytest.mark.parametrize("policy", ["recurrent", "mlp2", "equivariant2"])
@pytest.mark.parametrize("kw", [{}, dict(mortality=False), dict(deposit_share="contributor"), dict(succession=False)])
def test_v2_ledger_closes(policy, kw):
    from agency_gradients.world import make_world
    w = make_world(Config(policy=policy, **V2, **kw), 3)
    for _ in range(500):
        w.step()
        assert abs(w.ledger_residual()) < 1e-6


def test_v2_walls_block_and_params_large():
    import numpy as np
    from agency_gradients.world import make_world, n_params
    w = make_world(Config(policy="recurrent", **V2), 1)
    assert n_params("recurrent") > 1500
    w.run(300)
    assert not w.wall[w.pos[w.alive, 0], w.pos[w.alive, 1]].any()


def test_v2_oracle_runs_and_deterministic():
    from agency_gradients.controls import oracle_policy
    from agency_gradients.world import make_world
    def go():
        w = make_world(Config(policy="equivariant2", **V2), 5)
        w.policy = oracle_policy
        return w.run().summary()
    assert go() == go()


def test_v2_config_many_genes_and_generations():
    from agency_gradients.config import v2_config
    from agency_gradients.world import make_world
    w = make_world(v2_config(steps=3000), 2).run()
    s = w.summary()
    assert s["n_genes"] > 2000
    assert s["gen_mean"] > 10          # many generations of descent
    assert abs(w.ledger_residual()) < 1e-6
