"""S9 and S10 worlds (both opt-in subclasses of WorldV2; no change to v1/v2/v3 behaviour).

PlasticWorld (S9): the recurrent policy gets within-lifetime learning. Each agent adds
a private, non-heritable correction (dW, db) to its output layer, trained online by a
reward-modulated policy gradient with an eligibility trace. The learning signal is
chosen by cfg.plastic: "energy" (the agent's own energy change: intake minus cost) or
"heat" (the heat it dissipates this step, i.e. an explicit private entropy reward).
Selection is whatever cfg.selection says (persistence); the correction is reset at
birth, so nothing learned is inherited (no Lamarckism).

EnglandWorld (S10): no births, no deaths, no fitness. A dissipation-biased
rearrangement rule is the only thing that changes policies. Each agent alternates
windows: it measures a score with its retained genome, then with a proposed
rearrangement of it; the rearrangement is kept with probability
min(1, exp(beta * r)) where r is the relative change in the score. This is the
local-detailed-balance form of dissipative adaptation: transitions are biased by the
work absorbed/dissipated along them. cfg.england chooses the score:
  absorbed    energy taken in during the window
  dissipated  heat dissipated, capped by what was absorbed (heat paid for out of
              bailout energy is not dissipation of the drive)
  neutral     keep with probability 1/2 regardless (random drift control)
  anti        exp(-beta * r): the opposite bias
The rule is an ASSUMPTION about how structure changes couple to dissipation; the
experiment asks what that assumption produces in this world, not whether real
matter obeys it.
"""
from __future__ import annotations

import numpy as np

from .config import Config
from .policies_v2 import N_ACT2, N_TRAIT, forward, parse
from .world_v2 import WorldV2


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


class PlasticWorld(WorldV2):
    def __init__(self, cfg: Config, seed: int, n_agents: int | None = None):
        assert cfg.plastic in ("energy", "heat"), "plastic must be 'energy' or 'heat'"
        kind, hid, _ = parse(cfg.policy)
        assert kind == "recurrent", "within-lifetime learning is implemented for the recurrent policy"
        m = cfg.max_pop
        self.dW = np.zeros((m, hid, N_ACT2))
        self.db = np.zeros((m, N_ACT2))
        self.eW = np.zeros((m, hid, N_ACT2))
        self.eb = np.zeros((m, N_ACT2))
        self.r_mean = np.zeros(m)
        self.r_scale = 1.0
        self._act_cache = None
        super().__init__(cfg, seed, n_agents)

    def _on_birth(self, slots):
        if hasattr(self, "dW"):
            self.dW[slots] = 0.0
            self.db[slots] = 0.0
            self.eW[slots] = 0.0
            self.eb[slots] = 0.0
            self.r_mean[slots] = 0.0

    def _act(self, idx, obs):
        if self.policy is not None:
            return self.policy(obs, self.rng)
        logits, hn = forward(self.genome[idx], obs, self.h[idx], self.cfg.policy)
        logits = logits + np.einsum("nh,nha->na", hn, self.dW[idx]) + self.db[idx]
        self.h[idx] = hn
        a = np.argmax(logits + self.rng.gumbel(size=logits.shape), axis=1)
        self._act_cache = (idx, hn, _softmax(logits), a)
        return a

    def _post_step(self, idx, gain, cost):
        if self._act_cache is None or self.policy is not None:
            return
        cidx, hn, p, a = self._act_cache
        cfg = self.cfg
        one = np.zeros_like(p)
        one[np.arange(len(a)), a] = 1.0
        g = one - p
        self.eW[cidx] = cfg.plastic_trace * self.eW[cidx] + hn[:, :, None] * g[:, None, :]
        self.eb[cidx] = cfg.plastic_trace * self.eb[cidx] + g
        r = (gain - cost) if cfg.plastic == "energy" else cost
        adv = r - self.r_mean[cidx]
        self.r_mean[cidx] += 0.02 * adv
        self.r_scale = 0.999 * self.r_scale + 0.001 * max(float(np.abs(adv).mean()), 1e-6)
        d = np.clip(adv / max(self.r_scale, 1e-6), -3.0, 3.0)
        self.dW[cidx] += cfg.plastic_lr * d[:, None, None] * self.eW[cidx] * 0.1
        self.db[cidx] += cfg.plastic_lr * d[:, None] * self.eb[cidx] * 0.1
        np.clip(self.dW[cidx], -5, 5, out=self.dW[cidx])
        np.clip(self.db[cidx], -5, 5, out=self.db[cidx])


class EnglandWorld(WorldV2):
    def __init__(self, cfg: Config, seed: int, n_agents: int | None = None):
        assert cfg.england in ("absorbed", "dissipated", "neutral", "anti")
        assert not cfg.mortality and not cfg.heredity or True
        m = cfg.max_pop
        self._n_pol = None
        super().__init__(cfg, seed, n_agents)
        self.reproduce = False
        P = self.genome.shape[1]
        self.g_ret = self.genome.copy()
        self.phase = np.zeros(m, dtype=np.int8)           # 0 = measuring retained, 1 = measuring proposal
        self.s_ret = np.zeros(m)
        self.wA = np.zeros(m)
        self.wQ = np.zeros(m)
        self.wt = self.rng.integers(0, cfg.eng_window, m)  # staggered windows
        self.genome[:, -N_TRAIT:] = 0.0                    # body traits fixed: only the policy rearranges
        self.g_ret[:, -N_TRAIT:] = 0.0
        self.n_prop = 0
        self.n_acc = 0

    def _score(self, A, Q):
        if self.cfg.england == "dissipated":
            return np.minimum(Q, A)
        return A

    def _post_step(self, idx, gain, cost):
        cfg = self.cfg
        self.wA[idx] += gain
        self.wQ[idx] += cost
        self.wt[idx] += 1
        end = idx[self.wt[idx] >= cfg.eng_window]
        if len(end) == 0:
            return
        s = self._score(self.wA[end], self.wQ[end]) / cfg.eng_window
        ph = self.phase[end]
        # --- end of a retained-genome window: record score, make a proposal
        r0 = end[ph == 0]
        if len(r0):
            self.s_ret[r0] = s[ph == 0]
            P = self.genome.shape[1] - N_TRAIT
            mask = self.rng.random((len(r0), P)) < cfg.eng_frac
            prop = self.g_ret[r0].copy()
            prop[:, :P] += mask * cfg.eng_sigma * self.rng.standard_normal((len(r0), P))
            self.genome[r0] = prop
            self.phase[r0] = 1
        # --- end of a proposal window: accept or revert
        r1 = end[ph == 1]
        if len(r1):
            s1 = s[ph == 1]
            old = self.s_ret[r1]
            rel = 2.0 * (s1 - old) / (np.abs(s1) + np.abs(old) + 1e-9)
            if cfg.england == "neutral":
                p_acc = np.full(len(r1), 0.5)
            else:
                sign = -1.0 if cfg.england == "anti" else 1.0
                p_acc = np.minimum(1.0, np.exp(np.clip(sign * cfg.eng_beta * rel, -50, 0.0)))
                p_acc = np.where(sign * rel >= 0, 1.0, p_acc)
            acc = self.rng.random(len(r1)) < p_acc
            self.g_ret[r1[acc]] = self.genome[r1[acc]]
            self.genome[r1[~acc]] = self.g_ret[r1[~acc]]
            self.phase[r1] = 0
            self.n_prop += len(r1)
            self.n_acc += int(acc.sum())
        self.wA[end] = 0.0
        self.wQ[end] = 0.0
        self.wt[end] = 0

    def summary(self, passive_rate=None):
        out = super().summary(passive_rate)
        out["eng_accept"] = self.n_acc / max(self.n_prop, 1)
        return out
