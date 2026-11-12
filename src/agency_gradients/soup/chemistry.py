"""S14 soup: species, reactions, free energies and catalysis tables.

A chemistry is a set of binary polymers (alphabet {a, b}, length 1..L), a fuel F and a waste W.
Every join x + y <-> xy exists twice: a plain channel and a fuel-coupled channel
(x + y + F <-> xy + W). Free energies are in units of kT. See PREREGISTRATION_S14.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from itertools import product

import numpy as np

BONDS = ("aa", "ab", "ba", "bb")


@dataclass(frozen=True)
class SoupParams:
    """Frozen parameters of S14 (PREREGISTRATION_S14.md, 'Parameters')."""
    L: int = 6                    # maximum polymer length
    eps_mean: float = 4.0         # mean bond free energy (uphill)
    eps_sd: float = 1.0
    min_cat_len: int = 3          # shortest polymer that can catalyse
    cat_per_polymer: float = 1.0  # expected catalysed reactions per polymer, per channel kind
    kappa0: float = 0.1           # base attempt rate of a plain join or cut, per residence time
    speedup: float = 1000.0       # catalytic speed-up S (per catalyst at the reference concentration)
    eta: float = 1e-3             # uncatalysed fuel-coupled join, relative to plain
    kappa_leak: float = 0.01      # F -> W leak, per residence time
    c0: float = 1000.0            # reference (standard-state) count
    n_mono: int = 1000            # inflow level of each monomer
    n_fuel: int = 2000            # inflow level of fuel
    dil: float = 1.0              # dilution rate; time is in residence times
    t_end: float = 400.0
    t_late: float = 300.0         # the late window is [t_late, t_end]
    eps_tau: float = 0.03         # tau-leap accuracy parameter
    tau_max: float = 0.05

    def with_(self, **kw) -> "SoupParams":
        return replace(self, **kw)


@dataclass
class Chemistry:
    species: list[str]                 # polymers, then "F", "W"
    lens: np.ndarray                   # polymer length (0 for F and W)
    na: np.ndarray                     # number of a's per species
    nb: np.ndarray
    g: np.ndarray                      # standard free energy of polymers (F and W set per run)
    x: np.ndarray                      # join sites: x + y <-> z
    y: np.ndarray
    z: np.ndarray
    eps_site: np.ndarray               # free energy of the bond made at each site
    eps_bond: dict
    cp_rxn: np.ndarray = field(default_factory=lambda: np.zeros(0, np.int64))   # plain-channel catalysis
    cp_spec: np.ndarray = field(default_factory=lambda: np.zeros(0, np.int64))
    cc_rxn: np.ndarray = field(default_factory=lambda: np.zeros(0, np.int64))   # fuel-coupled catalysis
    cc_spec: np.ndarray = field(default_factory=lambda: np.zeros(0, np.int64))
    ext_p: np.ndarray | None = None    # outside ("mineral") catalyst, count-equivalent per site
    ext_c: np.ndarray | None = None
    label: str = ""

    @property
    def n_species(self) -> int:
        return len(self.species)

    @property
    def n_sites(self) -> int:
        return len(self.x)

    @property
    def iF(self) -> int:
        return len(self.species) - 2

    @property
    def iW(self) -> int:
        return len(self.species) - 1

    def index(self, s: str) -> int:
        return self._idx[s]

    def site(self, x: str, y: str) -> int:
        return self._site[(x, y)]

    def without_catalysis(self) -> "Chemistry":
        e = np.zeros(0, np.int64)
        c = replace(self, cp_rxn=e, cp_spec=e, cc_rxn=e, cc_spec=e, ext_p=None, ext_c=None,
                    label=self.label + "-nocat")
        c._idx, c._site = self._idx, self._site
        return c


def _skeleton(L: int, eps_bond: dict) -> Chemistry:
    polys = ["".join(p) for n in range(1, L + 1) for p in product("ab", repeat=n)]
    species = polys + ["F", "W"]
    idx = {s: i for i, s in enumerate(species)}
    lens = np.array([len(s) for s in polys] + [0, 0], np.int64)
    na = np.array([s.count("a") for s in polys] + [0, 0], np.int64)
    nb = np.array([s.count("b") for s in polys] + [0, 0], np.int64)
    g = np.array([sum(eps_bond[s[i:i + 2]] for i in range(len(s) - 1)) for s in polys] + [0.0, 0.0])
    xs, ys, zs, es, site = [], [], [], [], {}
    for s in polys:
        for k in range(1, len(s)):
            site[(s[:k], s[k:])] = len(xs)
            xs.append(idx[s[:k]]); ys.append(idx[s[k:]]); zs.append(idx[s])
            es.append(eps_bond[s[k - 1:k + 1]])
    c = Chemistry(species=species, lens=lens, na=na, nb=nb, g=g, x=np.array(xs), y=np.array(ys),
                  z=np.array(zs), eps_site=np.array(es, float), eps_bond=dict(eps_bond))
    c._idx, c._site = idx, site
    return c


def random_chemistry(chem_id: int, prm: SoupParams) -> Chemistry:
    """Arm R: bond energies and catalysis tables drawn once from the chemistry's own seed."""
    rng = np.random.default_rng(np.random.SeedSequence([14, 1, int(chem_id)]))
    eps_bond = {b: float(rng.normal(prm.eps_mean, prm.eps_sd)) for b in BONDS}
    c = _skeleton(prm.L, eps_bond)
    cats = np.flatnonzero(c.lens >= prm.min_cat_len)
    p = min(1.0, prm.cat_per_polymer / c.n_sites)
    for kind in ("p", "c"):
        m = rng.random((len(cats), c.n_sites)) < p
        ci, ri = np.nonzero(m)
        setattr(c, f"c{kind}_rxn", ri.astype(np.int64))
        setattr(c, f"c{kind}_spec", cats[ci].astype(np.int64))
    c.label = f"R{chem_id}"
    return c


COPIER = "aabb"
COPIER_STEPS = (("a", "a"), ("aa", "b"), ("aab", "b"))
COPIER_SEED = 20
MINERAL_LEVEL = 200.0


def designed_chemistry(kind: str, prm: SoupParams) -> Chemistry:
    """Arm P (a designed self-copier) and arm M (the same reactions, catalysed from outside)."""
    c = _skeleton(prm.L, {b: prm.eps_mean for b in BONDS})
    sites = np.array([c.site(x, y) for x, y in COPIER_STEPS], np.int64)
    if kind == "P":
        c.cc_rxn = sites
        c.cc_spec = np.full(len(sites), c.index(COPIER), np.int64)
    elif kind == "M":
        c.ext_c = np.zeros(c.n_sites)
        c.ext_c[sites] = MINERAL_LEVEL
    else:
        raise ValueError(kind)
    c.label = kind
    return c


def equilibrium_counts(chem: Chemistry, a_tot: float, b_tot: float, c0: float) -> np.ndarray:
    """Closed-box equilibrium polymer counts for given totals of a-units and b-units.

    At equilibrium the count of polymer s is c0 * A**na * B**nb * exp(-g_s), with A, B the
    monomer counts over c0. Solved for A, B by Newton's method in log space.
    """
    P = chem.lens > 0
    na, nb, g = chem.na[P].astype(float), chem.nb[P].astype(float), chem.g[P]
    u = np.log(max(a_tot, 1e-9) / c0) - 1.0
    v = np.log(max(b_tot, 1e-9) / c0) - 1.0
    for _ in range(200):
        w = c0 * np.exp(na * u + nb * v - g)
        fa, fb = (na * w).sum(), (nb * w).sum()
        r = np.array([np.log(fa / a_tot), np.log(fb / b_tot)])
        if np.abs(r).max() < 1e-12:
            break
        J = np.array([[(na * na * w).sum() / fa, (na * nb * w).sum() / fa],
                      [(na * nb * w).sum() / fb, (nb * nb * w).sum() / fb]])
        du, dv = np.linalg.solve(J, -r)
        step = min(1.0, 2.0 / max(abs(du), abs(dv), 1e-12))
        u, v = u + step * du, v + step * dv
    out = np.zeros(chem.n_species)
    out[P] = c0 * np.exp(na * u + nb * v - g)
    return out
