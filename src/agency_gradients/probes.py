"""Agency probes.

``viability_probe`` is the operational form of "agency" used in this repo: can an
agent that has been displaced and depleted get itself back to a viable energy
state? The same test is run on (a) agents sampled from the evolved population and
(b) freshly initialised random-genome agents, in a copy of the same environment.
The difference between the two is the evidence; either number alone is not.

Limits (also in the README): this measures goal-less *viability restoration*. It
does not measure prediction or world-modelling. Predictive information is on the
roadmap, not implemented.
"""
from __future__ import annotations

import numpy as np

from .world import World, random_genomes


def viability_probe(world: World, n: int = 64, horizon: int = 150, seed: int = 0) -> dict:
    donors = np.flatnonzero(world.alive)
    if len(donors) == 0:
        return dict(evolved_recovered=np.nan, random_recovered=np.nan,
                    evolved_survived=np.nan, random_survived=np.nan, delta_recovered=np.nan)
    cfg = world.cfg
    rng = np.random.default_rng(seed)
    e0 = 0.5 * cfg.repro_thresh
    res = {}
    for label in ("evolved", "random"):
        w = world.clone_environment()
        w.reproduce = False
        w.rng = np.random.default_rng(rng.integers(2**63))
        if label == "evolved":
            g = world.genome[rng.choice(donors, n, replace=True)].copy()
        else:
            g = random_genomes(rng, n, cfg.policy)
        k = w.spawn(g, rng.integers(0, cfg.size, (n, 2)), np.full(n, e0))
        for _ in range(horizon):
            w.step()
        a = w.alive
        res[f"{label}_survived"] = float(a.sum()) / k
        res[f"{label}_recovered"] = float((a & (w.energy >= e0)).sum()) / k
    res["delta_recovered"] = res["evolved_recovered"] - res["random_recovered"]
    return res
