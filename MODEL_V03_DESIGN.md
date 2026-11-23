# v0.3 design: lineage-associated energy harvesting

## Purpose

v0.2 showed that its evolutionary signal depended on an explicit pleiotropic assumption: genotype-dependent catalytic match also increased the replication rate constant. v0.3 removes that direct link.

The new model makes the replicator itself an energy carrier. A genotype-specific reaction converts a low-energy replicator into a high-energy state using the fuel gradient. Replication consumes that high-energy state. Replication kinetics are identical across genotypes; selection can emerge only because some genotypes harvest more usable energy.

This remains an abstract reaction-network model, not a chemically identified prebiotic system.

## Chemical species

- (F,W): fuel and waste, with (F+W=1)
- (M,P): monomer and polymer, with (M+P=1)
- (C_i^L): low-energy replicator of genotype (i)
- (C_i^H): high-energy replicator of genotype (i)

The total abundance of genotype (i) is (c_i=C_i^L+C_i^H).

## Reactions

### R1 — genotype-dependent energy capture

[
F+C_i^L ightleftharpoons W+C_i^H
]

The rate is

[
J_{1,i}=k_{1,i}left(f,c_i^L-e^{-Deltamu_1}w,c_i^Hight)
]

where (k_{1,i}) is multiplied by a genotype-match factor. The same multiplier applies to forward and reverse rates, so it changes kinetics without changing the equilibrium constant.

### R2 — replication

[
C_i^H+M ightleftharpoons C_i^L+C_j^L+P
]

The rate is

[
J_{2,ij}=k_{mathrm{rep}}K_{ij}
left(c_i^H m-e^{-Deltamu_2}p,c_i^L c_j^Light)
]

(K_{ij}) is a symmetric mutation kernel. (k_{mathrm{rep}}) is genotype-independent. A high-energy parent produces a low-energy parent and a low-energy offspring; the offspring genotype is determined by (K_{ij}).

### R3 — maintenance / energy relaxation

[
C_i^H ightleftharpoons C_i^L
]

[
J_{3,i}=k_{mathrm{maint}}
left(c_i^H-e^{-Deltamu_3}c_i^Light)
]

This is a declared dissipative relaxation pathway.

## Why this is a stronger test

The genotype-match factor affects only R1. It does not appear in (k_{mathrm{rep}}). A genotype can reproduce faster only if its own high-energy replicator state is populated by energy capture. The high-energy state is lineage-associated rather than held in a shared ATP pool.

This removes v0.2's direct catalytic-match-to-replication-rate shortcut. It does not prove that such a coupling occurs in real chemistry; it supplies a clearer mechanistic hypothesis to test.

## Thermodynamic accounting

The standard chemical potentials are chosen so that the reaction affinities are:

[
A_{1,i}=Deltamu_1+lnrac{f c_i^L}{w c_i^H}
]

[
A_{2,ij}=Deltamu_2+lnrac{c_i^H m}{p c_i^L c_j^L}
]

[
A_{3,i}=Deltamu_3+lnrac{c_i^H}{c_i^L}
]

The reaction entropy-production rate is

[
sigma_{mathrm{rxn}}=
sum_iJ_{1,i}A_{1,i}
+sum_{ij}J_{2,ij}A_{2,ij}
+sum_iJ_{3,i}A_{3,i}
]

and the ideal feed/outflow terms are included separately. The complete declared system free energy includes F/W, M/P, and every low/high replicator species. The pointwise identity is tested as

[
dot G_{mathrm{reservoir}}-dot G_{mathrm{system}}
=sigma_{mathrm{total}}geq0.
]

No entropy-production term enters reproductive kinetics directly.

## Experimental arms

- **N:** baseline carrier kinetics; no genotype-specific match and no replication.
- **M:** fixed genotype library; genotype-specific energy capture but no replication.
- **D:** faithful copying, no new mutation.
- **L:** heritable mutation and selection.

D and L begin with exactly the same genotype concentrations and low/high energy-state split.

## Validation requirements

1. Local detailed balance for R1, R2 and R3.
2. Non-negative reaction and flow entropy production.
3. Pointwise and integrated free-energy balance closure.
4. Stoichiometric checks: total genotype abundance changes only through offspring production.
5. Positivity and timestep-refinement checks without state clipping.
6. At zero barrier, genotype match must have no kinetic effect and D/L total observables must coincide.
7. Compare static and target-switch environments, multiple barriers, mutation rates and initial standing-variation levels.
8. Report total fuel extent, replication extent, entropy production and state free-energy changes separately; do not collapse them into an unsupported scalar "efficiency."

## Limitations retained

The first v0.3 implementation uses a four-genotype (2-bit) deterministic ODE, a single shared fuel pool and monomer pool, and a deterministic target switch. It has no finite-population stochasticity, explicit spatial compartments, realistic molecular identities, or explicit mutation-repair energy cost. The low/high replicator states are an abstract energy-carrier representation.
