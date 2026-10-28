"""Small, dependency-free statistics helpers (numpy only)."""
from __future__ import annotations

from collections import defaultdict

import numpy as np


def bootstrap_mean_ci(x, n_boot: int = 4000, alpha: float = 0.05, seed: int = 0):
    x = np.asarray([v for v in x if not _isnan(v)], dtype=float)
    if len(x) == 0:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    b = x[rng.integers(0, len(x), (n_boot, len(x)))].mean(axis=1)
    return float(x.mean()), float(np.quantile(b, alpha / 2)), float(np.quantile(b, 1 - alpha / 2))


def bootstrap_diff_ci(a, b, n_boot: int = 4000, alpha: float = 0.05, seed: int = 0):
    """Mean(a) - mean(b) with a percentile bootstrap CI (independent samples)."""
    a = np.asarray([v for v in a if not _isnan(v)], dtype=float)
    b = np.asarray([v for v in b if not _isnan(v)], dtype=float)
    if len(a) == 0 or len(b) == 0:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    ba = a[rng.integers(0, len(a), (n_boot, len(a)))].mean(axis=1)
    bb = b[rng.integers(0, len(b), (n_boot, len(b)))].mean(axis=1)
    d = ba - bb
    return float(a.mean() - b.mean()), float(np.quantile(d, alpha / 2)), float(np.quantile(d, 1 - alpha / 2))


def factor_effect(rows, factor: str, metric: str, strata: tuple[str, ...],
                  n_boot: int = 4000, alpha: float = 0.05, seed: int = 0):
    """Main effect of a binary factor in a balanced factorial design.

    Effect = mean(metric | factor=1) - mean(metric | factor=0), averaged over the
    other cells. The CI resamples runs *within* each full condition (stratum), so
    the design stays balanced in every bootstrap replicate.
    """
    groups = defaultdict(list)
    for r in rows:
        v = r[metric]
        if _isnan(v):
            continue
        groups[tuple(r[k] for k in strata)].append(float(v))
    keys = list(groups)
    fi = strata.index(factor)

    def eff(samples):
        on = [np.mean(samples[k]) for k in keys if k[fi]]
        off = [np.mean(samples[k]) for k in keys if not k[fi]]
        return float(np.mean(on) - np.mean(off))

    point = eff({k: np.asarray(groups[k]) for k in keys})
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        s = {k: np.asarray(groups[k])[rng.integers(0, len(groups[k]), len(groups[k]))] for k in keys}
        boots[i] = eff(s)
    return point, float(np.quantile(boots, alpha / 2)), float(np.quantile(boots, 1 - alpha / 2))


def _isnan(v) -> bool:
    try:
        return bool(np.isnan(v))
    except TypeError:
        return False
