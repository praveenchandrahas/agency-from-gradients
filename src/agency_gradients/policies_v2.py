"""Policies for world v2: a richer observation, a signal action, memory, and two
heritable body traits appended to the genome.

Observation layout (n, 54): [0:35] the seven v1 channels x (N,E,S,W,here), [35] own
energy, [36] bias (identical to v1, so the v1 hand-coded forager still works),
then [37:42] wall, [42:47] danger, [47:52] pheromone signal, [52:54] season sin/cos.
Actions: N, E, S, W, stay, invest, signal.

Genome = policy weights followed by two trait genes (body size, reproduction threshold).
"""
from __future__ import annotations

import numpy as np

from .world import N_CH, P_EQ, policy_logits

N_OBS2 = N_CH * 5 + 2 + 15 + 2     # 54
H2 = 24
N_ACT2 = 7
N_TRAIT = 2
P_REC = N_OBS2 * H2 + H2 * H2 + H2 + H2 * N_ACT2 + N_ACT2
P_MLP2 = N_OBS2 * H2 + H2 + H2 * N_ACT2 + N_ACT2


N_OBS3 = N_OBS2 + 2                 # + day/night phase sin/cos


def parse(policy: str):
    """'recurrent' -> ('recurrent', 24, 54);  'recurrent:48' -> ('recurrent', 48, 56)."""
    kind, _, h = policy.partition(":")
    return kind, (int(h) if h else H2), (N_OBS3 if h else N_OBS2)


def _policy_len(policy: str) -> int:
    kind, H, NO = parse(policy)
    if kind == "equivariant2":
        return P_EQ
    n = NO * H + H + H * N_ACT2 + N_ACT2
    return n + (H * H if kind == "recurrent" else 0)


def n_params_v2(policy: str) -> int:
    return _policy_len(policy) + N_TRAIT


def random_genomes_v2(rng: np.random.Generator, n: int, policy: str) -> np.ndarray:
    g = np.zeros((n, n_params_v2(policy)))
    kind, H2, N_OBS2 = parse(policy)
    if kind == "equivariant2":
        g[:, :P_EQ] = rng.normal(0.0, 1.0, (n, P_EQ))
    else:
        i = 0
        g[:, i:i + N_OBS2 * H2] = rng.normal(0, 1 / np.sqrt(N_OBS2), (n, N_OBS2 * H2)); i += N_OBS2 * H2
        if kind == "recurrent":
            g[:, i:i + H2 * H2] = rng.normal(0, 0.5 / np.sqrt(H2), (n, H2 * H2)); i += H2 * H2
        i += H2                                    # hidden bias = 0
        g[:, i:i + H2 * N_ACT2] = rng.normal(0, 1 / np.sqrt(H2), (n, H2 * N_ACT2))
    g[:, -N_TRAIT:] = rng.normal(0.0, 1.0, (n, N_TRAIT))
    return g


def traits(genomes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(size, repro_threshold_multiplier), each in [0.5, 1.5], mean 1 at gene = 0."""
    sig = 1.0 / (1.0 + np.exp(-genomes[:, -N_TRAIT:]))
    return 0.5 + sig[:, 0], 0.5 + sig[:, 1]


def forward(genomes: np.ndarray, obs: np.ndarray, h: np.ndarray, policy: str):
    """-> (logits (n, 7), new hidden state (n, H2))."""
    n = len(genomes)
    kind, H2, N_OBS2 = parse(policy)
    if kind == "equivariant2":
        lg = policy_logits(genomes[:, :P_EQ], obs[:, :N_CH * 5 + 2], "equivariant")
        return np.concatenate([lg, np.full((n, 1), -1e9)], axis=1), h
    i = 0
    w1 = genomes[:, i:i + N_OBS2 * H2].reshape(n, N_OBS2, H2); i += N_OBS2 * H2
    pre = np.einsum("ni,nih->nh", obs, w1)
    if kind == "recurrent":
        wh = genomes[:, i:i + H2 * H2].reshape(n, H2, H2); i += H2 * H2
        pre = pre + np.einsum("nh,nhk->nk", h, wh)
    b1 = genomes[:, i:i + H2]; i += H2
    w2 = genomes[:, i:i + H2 * N_ACT2].reshape(n, H2, N_ACT2); i += H2 * N_ACT2
    b2 = genomes[:, i:i + N_ACT2]
    hn = np.tanh(pre + b1)
    return np.einsum("nh,nha->na", hn, w2) + b2, (hn if kind == "recurrent" else h)
