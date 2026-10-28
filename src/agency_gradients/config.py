"""World configuration.

Every knob that an experiment may ablate or that affects results lives here, so
that a run is fully described by (Config, seed).
"""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Config:
    # --- geometry / run length -------------------------------------------------
    size: int = 32                 # torus is size x size
    steps: int = 20000
    max_pop: int = 200
    init_pop: int = 60

    # --- agent energetics ------------------------------------------------------
    metabolism: float = 0.10       # energy burned per step just to exist
    move_cost: float = 0.03        # extra cost of a move action
    invest_cost: float = 0.15      # cost of an invest action
    init_energy: float = 8.0
    repro_thresh: float = 12.0     # energy needed to reproduce (persistence mode)
    repro_cost: float = 6.0        # parent pays this; child receives 80 % of it
    child_share: float = 0.8
    hazard: float = 0.003          # extrinsic per-step death probability (only if mortality)
    eat_rate: float = 0.5          # max commons energy one agent can take per step

    # --- tier 0: the commons (diffuse, renewable) -------------------------------
    commons_cap: float = 1.0
    commons_regrow: float = 0.008  # per cell per step (x patch field). FACTOR: scarcity
    commons_regrow_abundant: float = 0.08

    patchiness: float = 1.0        # 0 = uniform commons; 1 = strongly patchy
    n_patches: int = 18
    patch_sigma: float = 3.5

    # --- tier 1: locked reservoirs (one agent can open one) ---------------------
    n_tier1: int = 12
    stock1: float = 150.0
    regrow1: float = 0.30
    lock1: float = 3.0             # invest units needed
    decay1: float = 0.02           # progress decay per step while locked
    harvest1: float = 1.5

    # --- tier 2: big reservoirs (need several agents investing at once) ---------
    n_tier2: int = 4
    stock2: float = 800.0
    regrow2: float = 1.6
    lock2: float = 25.0
    decay2: float = 0.15
    harvest2: float = 6.0

    scent_sigma: float = 4.0       # range of the reservoir cue, in cells

    reservoir_leak: float = 0.002  # passive loss rate of reservoir stock (heat)
    depleted_at: float = 1.0       # tier-1 stock below this counts as drained

    # --- evolution --------------------------------------------------------------
    policy: str = "equivariant"   # equivariant | mlp  (see world.py)
    mut_sigma: float = 0.30
    mut_rate: float = 0.10         # fraction of genome entries perturbed per birth
    selection: str = "persistence"  # persistence | entropy | task | drift
    drift_restore: float = 0.05    # neutral-model birth rate per missing individual
    entropy_repro_spent: float = 12.0  # entropy mode: energy burned per child

    # --- accounting assumption (see docs/DESIGN.md) ------------------------------
    kappa: float = 3.0             # entropy per unit energy dissipated by an agent;
                                   # passive leakage counts 1.0

    # --- ABLATION FACTORS -------------------------------------------------------
    scarcity: bool = True          # False -> abundant commons
    heredity: bool = True          # False -> offspring get a fresh random genome
    mortality: bool = True         # False -> zero-energy agents are bailed out
    succession: bool = True        # True -> tier-2 sites form only where tier 1 is drained

    # --- derived helpers -----------------------------------------------------------
    @property
    def regrow(self) -> float:
        return self.commons_regrow if self.scarcity else self.commons_regrow_abundant

    def with_(self, **kw) -> "Config":
        return replace(self, **kw)


FACTORS = ("scarcity", "heredity", "mortality", "succession")
SELECTIONS = ("persistence", "entropy", "task", "drift")
