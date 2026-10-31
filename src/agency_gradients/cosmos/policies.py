"""Controllers for the S11 world: piecewise log-time allocation (Phase A) and a small neural policy (Phase B)."""
from __future__ import annotations

import numpy as np

from .model import LEVERS

K_SEG = 6
NF = 10
HID = 16
NA = 6                                  # five levers + "do nothing"


def softmax(z):
    z = np.asarray(z, float)
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


class PiecewisePolicy:
    """theta shape (K_SEG, NA) logits; segment chosen by position on the log-time grid."""

    def __init__(self, theta, mask=(1, 1, 1, 1, 1)):
        self.u = []
        th = np.asarray(theta, float).reshape(K_SEG, NA).copy()
        for k in range(K_SEG):
            z = th[k].copy()
            z[:5][np.asarray(mask) == 0] = -1e9
            self.u.append(softmax(z)[:5])

    def __call__(self, feat, i, n):
        return self.u[min(K_SEG - 1, int(K_SEG * i / max(n, 1)))]


N_PW = K_SEG * NA
N_NN = NF * HID + HID + HID * NA + NA


class NeuralPolicy:
    def __init__(self, theta, mask=(1, 1, 1, 1, 1)):
        t = np.asarray(theta, float)
        a = NF * HID
        self.W1 = t[:a].reshape(NF, HID); self.b1 = t[a:a + HID]
        c = a + HID
        self.W2 = t[c:c + HID * NA].reshape(HID, NA); self.b2 = t[c + HID * NA:]
        self.mask = np.asarray(mask) == 0

    def __call__(self, feat, i, n):
        h = np.tanh(feat @ self.W1 + self.b1)
        z = h @ self.W2 + self.b2
        z[:5][self.mask] = -1e9
        return softmax(z)[:5]


def const_policy(u):
    u = np.asarray(u, float)
    return lambda f, i, n: u


def pure_theta(lever_idx, strength=6.0):
    th = np.zeros((K_SEG, NA))
    th[:, lever_idx] = strength
    return th.ravel()


def mix_theta(weights, strength=6.0):
    th = np.zeros((K_SEG, NA))
    for j, w in enumerate(weights):
        th[:, j] = strength * w
    return th.ravel()


def staged_theta(first, then, n_first=2, strength=6.0):
    """lever `first` for the first n_first segments, then lever `then`."""
    th = np.zeros((K_SEG, NA))
    th[:n_first, first] = strength
    th[n_first:, then] = strength
    return th.ravel()
