"""Hand-coded positive control.

``oracle_policy`` is a forager that follows the commons gradient, climbs the
reservoir scent, and invests when standing on a reservoir. It is NOT evolved and
carries no claim about agency. Its only job is to show how much headroom the
world offers: if even this policy cannot beat random walkers, the world cannot
test anything, and a null result from evolution would be uninformative.
"""
from __future__ import annotations

import numpy as np

# observation layout: obs[:, channel * 5 + pos]; pos 0..3 = N, E, S, W (== actions 0..3), pos 4 = here
HERE = 4
COMMONS, T1_LOCKED, T1_OPEN, T2_LOCKED, T2_OPEN, SCENT1, SCENT2 = range(7)


def _ch(obs: np.ndarray, c: int) -> np.ndarray:
    return obs[:, c * 5:(c + 1) * 5]


def oracle_policy(obs: np.ndarray, rng: np.random.Generator, eps: float = 0.1,
                  maintain_p: float = 0.15) -> np.ndarray:
    n = len(obs)
    score = (_ch(obs, COMMONS)
             + 2.0 * _ch(obs, SCENT1) + 2.0 * _ch(obs, SCENT2)
             + 4.0 * (_ch(obs, T1_LOCKED) + _ch(obs, T1_OPEN)
                      + _ch(obs, T2_LOCKED) + _ch(obs, T2_OPEN)))
    move = np.argmax(score[:, :4] + rng.random((n, 4)) * 0.05, axis=1)        # 0..3 = N,E,S,W
    stay = (score[:, HERE] >= score[:, :4].max(axis=1)) & (_ch(obs, COMMONS)[:, HERE] > 0.3)
    act = np.where(stay, 4, move)
    on_res = (_ch(obs, T1_LOCKED)[:, HERE] + _ch(obs, T1_OPEN)[:, HERE]
              + _ch(obs, T2_LOCKED)[:, HERE] + _ch(obs, T2_OPEN)[:, HERE]) > 0
    openness = _ch(obs, T1_OPEN)[:, HERE] + _ch(obs, T2_OPEN)[:, HERE]
    invest = on_res & ((openness < 0.999) | (rng.random(n) < maintain_p))
    act = np.where(invest, 5, act)
    rand = rng.random(n) < eps
    return np.where(rand, rng.integers(0, 6, n), act)
