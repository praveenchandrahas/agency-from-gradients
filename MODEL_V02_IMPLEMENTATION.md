# v0.2 implementation note — coupled autocatalytic reactor

**Status:** first deterministic prototype implemented; validation tests are in progress. This is not yet a confirmatory experiment.

## Reaction network

The prototype uses four genotype states for 2-bit keys and three reversible reactions:

[
F + D ightleftharpoons W + T
]

[
C_i + M + T ightleftharpoons C_i + C_j + P + D
]

[
T ightleftharpoons D
]

- (F/W): fuel and waste.
- (T/D): high- and low-energy work currency (ATP/ADP analogue).
- (M/P): monomer and polymerization waste.
- (C_i): genotype (i), with the parent catalyst retained and an offspring (C_j) produced.

The second reaction is autocatalytic: the parent genotype catalyses its own reproduction, while the offspring may be mutated. The same genotype-dependent catalytic factor influences both the fuel-conversion reaction and the replication reaction. This is an explicit pleiotropic/autocatalytic assumption, not a general consequence of thermodynamics. The `replication_coupling` parameter can weaken or remove this link; it must be swept before interpreting any evolutionary advantage.

## Standard chemical potentials

The current prototype uses standard potentials (in (k_BT) units):

| Species | Standard potential |
|---|---:|
| Fuel (F) | 12 |
| Waste (W) | 0 |
| ATP-like (T) | 6 |
| ADP-like (D) | 0 |
| Monomer (M) | 0 |
| Polymer waste (P) | 0 |
| Catalyst (C_i) | 7 |

These imply reaction standard affinities:

- Fuel conversion: (Deltamu_1=6)
- Replication: (Deltamu_2=-1)
- Maintenance hydrolysis: (Deltamu_3=6)

Every affinity is calculated from these same potentials and the current activities. The forward/reverse rate ratios are constructed to equal the exponential of the corresponding affinity.

## Population arms

- **N:** uncatalysed baseline; no catalysts.
- **M:** fixed catalyst library; no replication.
- **D:** autocatalytic replication with faithful inheritance (identity mutation kernel).
- **L:** the same initial library with a symmetric bit-flip mutation kernel.

All D/L genotype concentrations are initially positive, including a small standing concentration of rare genotypes. This makes the first prototype a comparison of mutation against a small standing-variation seed, not a test of mutation from an exactly absent genotype.

## Thermodynamic boundary

The declared isothermal CSTR exchanges both members of each binary pool:

- (F/W) fuel/waste feed and outflow.
- (M/P) monomer/polymer feed and outflow.

The (T/D) pool is internal. Catalyst synthesis consumes (M) and (T), returning (P) and (D). The maintenance reaction also converts (T) to (D). The entropy-production diagnostic includes all three reactions and both binary-mixture exchange terms.

The implementation checks the differential free-energy identity

[
dot G_{mathrm{reservoir}}-dot G_{mathrm{system}}=dot S_{mathrm{prod}}
]

for the complete declared boundary. This is a stronger internal consistency check than a fuel-only mass residual. It does not include unmodelled apparatus, pressure work, heat leaks, or real chemical species.

## Numerical method

- Stiff ODE integration with SciPy's BDF solver.
- Adaptive internal steps, with a declared maximum step.
- No state clipping; leaving the positive activity domain is an error.
- Piecewise-constant target schedules allow environmental changes without changing standard chemical potentials.

## Current limitations and next gates

1. Only 2-bit genotype spaces are implemented in the first prototype.
2. The ODE is deterministic; finite-population stochastic extinction is not represented.
3. The parent genotype catalyses its own replication; the strength of this pleiotropic link is a key sensitivity parameter.
4. Mutation has no extra proofreading/repair cost in this prototype; the normal replication reaction cost is included.
5. The initial library includes a small positive amount of every genotype; larger and sparse standing libraries need separate comparisons.
6. The next experiments must sweep barrier, mutation rate, replication coupling, key length, target drift timing, initial standing variation and feed/maintenance parameters.
7. Only after those sweeps should the model be used for an equal-investment comparison. The v0.1 results remain exploratory and are not rescued by this new prototype.
