"""S14 soup: the emergence detector.

Criterion (i), closure: the reactions active in the late window contain a self-sustaining
autocatalytic set (a RAF set, Hordijk and Steel 2004) that includes a fuel-coupled join.
Criterion (ii), history: a sterilised twin stays below half the intact polymer fraction for at
least 10 residence times. Plus the shuffle null of H14d.
"""
from __future__ import annotations

import numpy as np

from .chemistry import Chemistry, SoupParams
from .reactor import Reactor


def max_raf(reactions: list[tuple], food: set[int]) -> list[int]:
    """Largest RAF subset. `reactions` is a list of (reactants, products, catalysts), each a
    tuple of species indices. Returns the indices of the reactions kept.

    Repeat until nothing changes: compute what can be built from food using the current
    reactions (ignoring catalysis), then drop every reaction that lacks a reactant or has no
    catalyst among the buildable species.
    """
    keep = list(range(len(reactions)))
    while True:
        avail = set(food)
        grew = True
        while grew:
            grew = False
            for i in keep:
                rs, ps, _ = reactions[i]
                if all(r in avail for r in rs) and not all(p in avail for p in ps):
                    avail.update(ps)
                    grew = True
        new = [i for i in keep if all(r in avail for r in reactions[i][0])
               and any(c in avail for c in reactions[i][2])]
        if len(new) == len(keep):
            return keep
        keep = new


def _catalysts_by_site(chem: Chemistry) -> tuple[dict, dict]:
    cp, cc = {}, {}
    for r, s in zip(chem.cp_rxn.tolist(), chem.cp_spec.tolist()):
        cp.setdefault(r, []).append(s)
    for r, s in zip(chem.cc_rxn.tolist(), chem.cc_spec.tolist()):
        cc.setdefault(r, []).append(s)
    return cp, cc


def _food(chem: Chemistry) -> set[int]:
    # W is waste, always present through the leak; it is not what closure is about.
    return {chem.index("a"), chem.index("b"), chem.iF, chem.iW}


def realised_raf(rx: Reactor, n_min: float = 1.0, j_min: float = 1.0) -> dict:
    """Criterion (i) on the late window of a finished run.

    A site-channel is active if its net flux is at least `j_min` events per residence time. It
    is taken in its net direction. Its catalysts are the assigned polymers whose late mean
    count is at least `n_min`. Uncatalysed and outside-catalysed reactions cannot be in the set.
    """
    chem = rx.chem
    cp, cc = _catalysts_by_site(chem)
    mean_n = rx.mean_late_counts()
    T = max(rx.late_dt, 1e-12)
    reactions, is_fuel_fwd = [], []
    for kind, knet, cmap in (("p", rx.kp_net, cp), ("c", rx.kc_net, cc)):
        for r in np.flatnonzero(np.abs(knet) / T >= j_min).tolist():
            cats = tuple(s for s in cmap.get(r, ()) if mean_n[s] >= n_min)
            if not cats:
                continue
            left = (int(chem.x[r]), int(chem.y[r])) + ((chem.iF,) if kind == "c" else ())
            right = (int(chem.z[r]),) + ((chem.iW,) if kind == "c" else ())
            fwd = knet[r] > 0
            reactions.append((left, right, cats) if fwd else (right, left, cats))
            is_fuel_fwd.append(kind == "c" and fwd)
    keep = max_raf(reactions, _food(chem))
    members = {p for i in keep for p in reactions[i][1]} - _food(chem)
    n_fuel = sum(is_fuel_fwd[i] for i in keep)
    return dict(raf=bool(keep) and n_fuel > 0, raf_size=len(keep), raf_fuel=int(n_fuel), raf_species=len(members))


def potential_raf(chem: Chemistry) -> dict:
    """Structural only: could this chemistry hold a closed set at all? Uses every join in the
    forward direction with every assigned catalyst, whatever its count. Descriptive."""
    cp, cc = _catalysts_by_site(chem)
    reactions, fuel = [], []
    for kind, cmap in (("p", cp), ("c", cc)):
        for r, cats in cmap.items():
            left = (int(chem.x[r]), int(chem.y[r])) + ((chem.iF,) if kind == "c" else ())
            right = (int(chem.z[r]),) + ((chem.iW,) if kind == "c" else ())
            reactions.append((left, right, tuple(cats)))
            fuel.append(kind == "c")
    keep = max_raf(reactions, _food(chem))
    return dict(pot_raf=bool(keep), pot_raf_size=len(keep), pot_raf_fuel=int(sum(fuel[i] for i in keep)))


def sterilised_twin(rx: Reactor, seed) -> Reactor:
    """Criterion (ii): copy the run at the start of the late window, delete every polymer of
    length 2 or more, keep the food and the waste, and run on with a fresh random stream."""
    n0 = rx.snapshot.copy()
    n0[rx.chem.lens >= 2] = 0
    tw = Reactor(rx.chem, rx.prm, rx.dmu, seed, flow=rx.flow, n0=n0, t0=rx.prm.t_late, t_end=rx.t_end,
                 day_night=rx.day_night)
    tw.late_from = 0
    return tw.run()


def twin_lag(intact: Reactor, twin: Reactor, frac: float = 0.5) -> float:
    """Residence times until the twin's polymer fraction first reaches `frac` of the intact
    run's late-window value. Returns the window length if it never does (censored)."""
    target = frac * intact.late()["poly_frac"]
    f = twin.poly_frac_series()
    hit = np.flatnonzero(f >= target)
    return float(hit[0]) if len(hit) and target > 0 else float(len(f))


def fuel_rate(rx: Reactor, n: np.ndarray) -> float:
    """Instantaneous net fuel-spending rate through the coupled channels at counts `n`
    (mass action, real-valued counts)."""
    c0 = rx.prm.c0
    _, pc = rx._prefactors(n)
    hf = n[rx.x] * n[rx.y]
    return float((pc * (rx.fc * hf * n[rx.iF] / (c0 * c0) - rx.bc * n[rx.z] * n[rx.iW] / c0)).sum())


def shuffle_percentile(rx: Reactor, seed, n_shuffle: int = 1000) -> float:
    """H14d. Percentile of the real late-window state's fuel-spending rate among states with
    the counts shuffled between polymers of the same length."""
    rng = np.random.default_rng(seed)
    n = rx.mean_late_counts()
    real = fuel_rate(rx, n)
    groups = [np.flatnonzero(rx.chem.lens == k) for k in range(1, int(rx.chem.lens.max()) + 1)]
    below = ties = 0
    for _ in range(n_shuffle):
        m = n.copy()
        for gidx in groups:
            m[gidx] = n[rng.permutation(gidx)]
        v = fuel_rate(rx, m)
        below += v < real
        ties += v == real
    return float((below + 0.5 * ties) / n_shuffle)
