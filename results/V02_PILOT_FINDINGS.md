# v0.2 coupled-reaction pilot — findings

**Status:** exploratory deterministic sensitivity study. Not confirmatory evidence.

**Workflow:** [run 1 — v0.2 thermodynamic validation pilot](https://github.com/praveenchandrahas/evolutionary-gradient-access/actions/runs/45165208194)  
**Artifact:** `ega-v02-thermodynamic-pilot` (240 simulation rows, 108 paired D/L contrasts, CSVs, manifest, summary and figure)

## 1. What was run

The v0.2 model couples a reversible fuel-to-work reaction, autocatalytic replication and a maintenance/hydrolysis sink:

[
F+D ightleftharpoons W+T
]

[
C_i+M+T ightleftharpoons C_i+C_j+P+D
]

[
T ightleftharpoons D
]

The same genotype-dependent catalytic factor affects fuel conversion and self-replication, scaled by `replication_coupling`. This is an explicit pleiotropic/autocatalytic assumption, not a consequence of thermodynamics alone.

The deterministic grid covered:

- 3 activation barriers: 4, 8, 12 (k_BT)
- 3 per-bit mutation rates: 0.01, 0.05, 0.10
- 3 replication-coupling values: 0, 0.5, 1
- 2 initial concentrations for the rare target genotype: (10^{-6}), (10^{-3})
- 2 environments: static target 00; or target switch 00 (ightarrow) 11 at time 50
- D: faithful inheritance; L: symmetric bit-flip mutation
- N and M: uncatalysed and fixed-library controls

Each D/L pair had exactly the same initial genotype concentrations. All four genotypes were present initially; the target genotype was rare. The grid has no stochastic replicates and therefore no confidence intervals.

## 2. Numerical and thermodynamic checks

| Diagnostic | Result |
|---|---:|
| Simulation rows | 240 |
| Paired D/L conditions | 108 |
| Maximum pointwise free-energy identity residual | (2.22	imes10^{-16}) |
| Maximum integrated free-energy residual | (2.13	imes10^{-5}) |
| Maximum integrated work-pool residual | (1.24	imes10^{-6}) |
| Minimum observed total entropy-production rate | (3.22	imes10^{-4}) |
| Minimum fuel activity | 0.928 |
| Minimum work-currency activity | 0.412 |
| Minimum monomer activity | 0.474 |

The pointwise identity closes to floating-point precision:

[
dot G_{mathrm{reservoir}}-dot G_{mathrm{system}}=dot S_{mathrm{prod}}
]

The small integrated residuals are numerical quadrature error, not a pointwise thermodynamic inconsistency. Simpson integration is performed separately across each constant-target segment. No state clipping was used.

## 3. Mutation versus faithful copying

The table reports the mean L/D ratio over the 54 conditions in each environment. A ratio above 1 favours mutation.

| Metric, L/D | Static | Target drifting |
|---|---:|---:|
| Late fuel-conversion throughput | 0.9916 | 1.0127 |
| Cumulative fuel-reaction extent | 0.9970 | 1.0025 |
| Declared work investment | 0.9979 | 1.0040 |
| Catalyst material investment | 0.9985 | 1.0027 |
| Cumulative fuel extent per declared work | 0.9991 | 0.9985 |
| Cumulative fuel extent per catalyst material | 0.9985 | 0.9998 |
| Late throughput per catalyst | 0.9931 | 1.0099 |

### Static environment

Mutation generally imposes a load. L had higher late throughput in only 6 of 54 conditions; its mean late-throughput ratio was 0.9916. The penalty became larger as mutation rate and replication coupling increased.

### Drifting environment

L had higher late throughput in all 54 conditions, but the effect was modest: mean ratio 1.0127, median 1.0041, range 1.00003–1.0715.

The effect increased with mutation rate:

| Mutation rate | Mean L/D late-throughput ratio under drift |
|---:|---:|
| 0.01 | 1.0025 |
| 0.05 | 1.0122 |
| 0.10 | 1.0232 |

It also increased with the assumed replication coupling:

| Replication coupling | Mean L/D late-throughput ratio under drift |
|---:|---:|
| 0 | 1.0005 |
| 0.5 | 1.0112 |
| 1 | 1.0262 |

This is consistent with a mutation/adaptation trade-off: mutation is mostly a cost in a static environment, but helps the system respond to a target shift. The dependence on replication coupling is important: the effect becomes larger when the genotype's catalytic match also increases its self-replication rate.

However, the late-throughput result does **not** translate into a cumulative efficiency advantage. Under drift, L's mean cumulative fuel extent was 0.25% higher than D's, while its declared work investment was 0.40% higher and catalyst material investment 0.27% higher. Mean fuel extent per unit declared work was therefore slightly lower for L (L/D = 0.9985). The corresponding material-normalized result was essentially parity (0.9998).

## 4. Fixed-library comparison

M begins with the same initial catalyst library as D and L but does not replicate. D and L achieve higher total cumulative fuel conversion than M, but do so by spending more work and material.

Mean D/M and L/M ratios across the grid:

| Metric | Drifting: D/M | Drifting: L/M | Static: D/M | Static: L/M |
|---|---:|---:|---:|---:|
| Cumulative fuel extent | 1.145 | 1.148 | 1.205 | 1.201 |
| Declared work investment | 1.856 | 1.867 | 2.171 | 2.158 |
| Catalyst material | 1.388 | 1.392 | 1.519 | 1.514 |
| Fuel extent per work | 0.722 | 0.721 | 0.700 | 0.699 |
| Fuel extent per catalyst material | 0.861 | 0.861 | 0.849 | 0.848 |

Thus, the replicating systems produce more total throughput, but their work and material investments rise by substantially more. In this parameterization, the fixed library is more efficient per unit of declared work and catalyst material. This comparison is not yet a fully matched-budget experiment; a larger fixed library could be a stronger control.

## 5. What this does and does not establish

**Supported within this model:** mutation can improve late adaptation after a target shift; the effect is conditional on mutation rate and on the assumed coupling between catalytic performance and self-replication. Mutation is generally disadvantageous in a static environment.

**Not established:** that evolution accesses dissipative pathways more efficiently than fixed or faithful-copying systems at equal total energetic and material investment. The cumulative, cost-normalized results are near parity or slightly favour D/M.

The model remains highly abstract:

1. Only a 2-bit, four-genotype landscape was used.
2. The environment makes one deterministic target switch, not stochastic drift.
3. The ODE is deterministic; finite-population noise and extinction are absent.
4. All genotypes start with positive concentration. The tested rare-variant range (10^{-6}) to (10^{-3}) does not yet represent a genuinely large standing library.
5. Mutation has no extra proofreading or repair cost.
6. The same genotype-dependent catalytic factor affects self-replication. The results cannot be generalized beyond that explicit autocatalytic assumption.
7. The initial catalyst library is an initial condition; its free energy is included in the state ledger, but synthesis is not simulated as a separate historical process.

## 6. Next validation gates

The next experiment should directly challenge the mutation result with stronger non-mutating controls:

1. Increase the initial target-genotype standing variation to 0.01 and 0.05, not just (10^{-6}) and (10^{-3}).
2. Add a uniform, fixed catalyst library and a faithful-copying D-large population initialized at the same total catalyst-material budget as the evolved population.
3. Compare cumulative throughput at matched work and material budgets, not only late throughput.
4. Expand the genotype space and use rugged as well as smooth landscapes.
5. Add finite-population stochastic dynamics and multiple paired realizations.
6. Replace the direct pleiotropic replication-coupling assumption with a compartmental or lineage-associated work-allocation model. The energy captured by a lineage should fund its own reproduction, rather than assigning a faster replication rate directly from catalytic match.

**Current conclusion:** v0.2 provides a thermodynamically closed toy reaction network and a conditional adaptation signal. It does not yet support the stronger claim that evolution outperforms non-evolving alternatives at comparable energetic and material costs.
