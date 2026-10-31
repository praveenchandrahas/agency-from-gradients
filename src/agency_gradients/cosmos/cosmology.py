"""Flat LambdaCDM background: a(t), comoving light-travel distances, reach cone."""
from __future__ import annotations

import numpy as np

from .constants import CHI_OBS_GLY, C, GLY_M, H0_YR, OL, OM, T_CMB0, T_DS, YR

_K = 1.5 * np.sqrt(OL) * H0_YR


def log_a_of_t(t_yr):
    x = _K * np.asarray(t_yr, float)
    xs = np.minimum(x, 20.0)
    small = np.log((OM / OL) ** (1 / 3)) + (2 / 3) * np.log(np.sinh(xs))
    big = np.log((OM / OL) ** (1 / 3)) + (2 / 3) * (x - np.log(2.0))
    return np.where(x > 20, big, small)


def a_of_t(t_yr):
    """Scale factor, a=1 at t0 (matter + Lambda only; radiation neglected)."""
    with np.errstate(over="ignore"):
        return np.exp(log_a_of_t(t_yr))


T0_YR = float(np.arcsinh(np.sqrt(OL / OM)) / _K)   # age at a=1, ~13.4 Gyr (no radiation)


def hubble(t_yr):
    """H(t) in 1/yr."""
    x = _K * np.asarray(t_yr, float)
    return (2 / 3) * _K / np.tanh(np.minimum(x, 50.0))


def time_grid(horizon_yr: float, per_decade: int = 30):
    n = int(np.ceil((np.log10(horizon_yr) - np.log10(T0_YR)) * per_decade))
    return np.logspace(np.log10(T0_YR), np.log10(horizon_yr), n + 1)


def comoving_integral(t_from, t_to, n=20001):
    """c * int dt / a, in Gly of comoving distance (log-spaced quadrature)."""
    t = np.logspace(np.log10(max(t_from, 1.0)), np.log10(t_to), n)
    f = np.exp(-log_a_of_t(t)) * t    # dt = t dln t
    return float(np.trapezoid(f, np.log(t))) * C * YR / GLY_M


def event_horizon_gly():
    """Comoving radius of the region a signal sent now can ever reach (expect ~16.5 Gly)."""
    return comoving_integral(T0_YR, 1e13)


def particle_horizon_gly():
    return comoving_integral(1.0, T0_YR)


def reach_fractions(grid, v_frac: float, chi0_gly: float = 0.1):
    """Reached volume fraction F(t) on the grid for probes of speed v_frac*c launched at t0."""
    inv = np.exp(-log_a_of_t(grid))
    dchi = np.zeros(len(grid))
    # trapezoid on log t
    lt = np.log(grid)
    seg = 0.5 * (inv[1:] * grid[1:] + inv[:-1] * grid[:-1]) * np.diff(lt)
    dchi[1:] = np.cumsum(seg) * v_frac * C * YR / GLY_M
    chi = chi0_gly + dchi
    return np.minimum(1.0, (chi / CHI_OBS_GLY) ** 3)


def t_env(grid):
    """Floor temperature for radiating waste heat: max(CMB, de Sitter)."""
    la = log_a_of_t(grid)
    return np.maximum(T_CMB0 * np.exp(-la), T_DS)
