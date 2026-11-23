# Model limitations and validation boundary (v0.1)

This file is deliberately explicit about what the first executable model does not establish.

## Mechanistic abstractions

1. **Catalytic key landscape:** catalysts are bit strings; target matching is a chosen mathematical landscape, not a molecular structure–activity relation.
2. **Reaction chemistry:** each lock is represented by a reversible scalar reaction with a prescribed affinity. There are no atom-resolved stoichiometric networks or identified prebiotic compounds.
3. **Waste and reservoirs:** the model tracks one fuel activity and treats waste activity as its complement. The reservoir-exchange entropy term covers the declared fuel exchange only; it is not a complete multicomponent mixing or reactor entropy budget.
4. **Population dynamics:** catalyst birth, mutation and turnover are coarse-grained algorithmic operations. Replication chemistry, compartment formation, finite-molecule stochasticity and physical inheritance are absent.
5. **Selection:** parent sampling is weighted by modelled catalytic contribution. This is a stipulated genotype-to-performance mechanism, not a derived origin of Darwinian evolution.
6. **Adaptive arm A:** A is an oracle-assisted search control: candidate scores are evaluated directly against the model's target landscape. It is a deliberately strong algorithmic comparator, not a physical non-living chemistry. Amatched fixes its catalyst count to L's late-window mean abundance.
7. **Material matching:** M is fixed at the initial library size; L and D may grow. Mmatched, Dmatched, Amatched and Umatched are controls initialized at L's paired late-window mean. Dmatched can reproduce faithfully without new mutation; the others are fixed populations or bounded search. This matches catalyst count, not cumulative construction/maintenance energy or the exact evolved genotype distribution. The model now reports initial construction, reproduction, maintenance, mutation and adaptive-search expenditures separately; equal-total-investment comparisons still require careful interpretation.
8. **Designer arm U:** U begins with target-matched catalysts. It is an idealized benchmark, not a naturally attainable competitor.
9. **Storage:** nonzero energy-storage coupling is rejected in v0.1. Catalyst construction and maintenance are represented as separate bookkeeping costs, but no explicit chemical storage reaction is modelled.
10. **Spatial and ecological effects:** no spatial transport, compartments, multiple species ecology or environmental feedback is represented.

## Thermodynamic boundary

Reaction entropy production is calculated from net reversible reaction flux times the logarithmic forward/reverse rate ratio. The declared fuel-reservoir exchange term is calculated from the ideal-activity chemical-potential difference. These are useful internal diagnostics for this abstract reactor, but the system boundary omits waste-reservoir exchange, pumping, mixing apparatus, heat transfer, catalyst synthesis chemistry and reservoir regeneration.

Consequently, `sigma_total` in v0.1 means the sum of the two implemented terms, not a complete entropy-production budget for a physical reactor or organism. Cumulative fuel extent and free-energy release are also model proxies. Do not report them as empirical physical quantities.

## Required gates before confirmatory use

- Derive all species and reservoir fluxes from one explicit stoichiometric and chemical-potential ledger.
- Close fuel and waste mass balances without clipping.
- Verify closed-box relaxation to equilibrium and zero entropy production at equilibrium.
- Verify catalyst multipliers preserve equilibrium for every lock.
- Demonstrate non-negative total entropy production over the full declared boundary.
- Perform integration-step convergence and alternative integration-scheme comparisons.
- Match M and D/L on catalyst abundance and cumulative material/energy investment.
- Match A and L on search/evaluation costs and information access.
- Sweep smooth, rugged and epistatic landscapes, and multiple population caps.
- Freeze the parameter ranges, primary outcomes and falsifiers before confirmatory runs.

The long-horizon implementation integrates 100 residence-time units. Environmental drift uses an independent random-number stream so paired arms experience the same target history. The integration scheme remains explicit Euler and the horizon is not evidence of asymptotic stationarity. A passing unit-test suite is not a substitute for these scientific validation gates.


## Audit update — 2026-11-23

A follow-up implementation audit identified three blocking defects in v0.1: reproduction expenditure is omitted from the reported investment total; the reproductive energy proxy uses the constant standard-affinity parameter rather than the state-dependent reaction affinity and is not linked to an explicit work-coupling reaction; and the ideal-mixture exchange entropy omits the complementary waste species. In addition, Dmatched is matched only at initialization and can subsequently grow. These findings supersede any interpretation of v0.1 as an equal-total-investment or complete-entropy test. See [VALIDATION_AUDIT.md](VALIDATION_AUDIT.md).

A further audit of the published trajectories found that 80% of D and 80% of L runs reach at least 400 of the 500 allowed catalysts after the first step; all are at or above 400 after the second. All D/L runs eventually touch the cap, with median first-hit steps of 27 for D and 24 for L. This indicates that the configured costs do not impose a sustained resource-limited growth regime over most of the grid. See [VALIDATION_AUDIT.md](VALIDATION_AUDIT.md).