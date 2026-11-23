# v0.3 initial work-pool charge: pilot results

**Status: completed exploratory deterministic rerun; not an equal-budget experiment.**

## Run and validation

GitHub Actions run 45173947881 completed successfully. The workflow ran the complete pytest suite and the revised 160-run standing-control pilot.

- 32 paired parameter/environment conditions.
- Five arms: D, L, Mmatched, Dmatched and Moracle.
- Barrier: 8 kT; mutation rates: 0.05 and 0.10; replication coupling: 0.5 and 1.0.
- Four initial rare-genotype concentrations: 1e-6, 1e-3, 1e-2 and 5e-2.
- Static and one-switch drifting environments (target 0 to 3 at t=50).
- Deterministic ODE simulations; no stochastic confidence intervals.

The run artifact is `ega-v03-initial-work-charge` (160 rows in `replicates.csv`, 32 paired contrasts in `matched_contrasts.csv`).

## Accounting checks

The run reported:

| Diagnostic | Maximum / minimum |
|---|---:|
| Pointwise free-energy identity residual | 1.73e-17 |
| Absolute integrated free-energy identity residual | 6.37e-6 |
| Absolute work-pool balance residual | 5.03e-8 |
| Minimum total entropy-production rate | 5.09e-3 |

These are numerical closure checks for the declared idealized model boundary. They do not establish that the boundary includes every energetic or material cost of a physical reactor.

The declared work-investment metric now includes initial catalyst free energy, initial T/D work-pool available exergy, and net replication and maintenance work transfers. Gross forward and reverse work transfers are also retained separately.

## Paired contrast results

Values below are arithmetic means of the 16 paired parameter conditions within each environment. Ratios are L divided by the comparator; values below 1 favour the comparator.

| Environment | Comparator | Late throughput | Cumulative fuel extent | Declared work investment | Material investment | Fuel extent / work |
|---|---|---:|---:|---:|---:|---:|
| Drifting | D | 1.014 | 1.004 | 1.001 | 1.003 | 1.003 |
| Drifting | Mmatched | 0.971 | 0.934 | 1.049 | 1.000 | 0.891 |
| Drifting | Dmatched | 0.673 | 0.758 | 0.900 | 0.734 | 0.840 |
| Drifting | Moracle | 1.112 | 0.948 | 1.039 | 1.000 | 0.913 |
| Static | D | 0.990 | 0.994 | 1.000 | 1.001 | 0.994 |
| Static | Mmatched | 1.255 | 1.041 | 1.054 | 1.000 | 0.988 |
| Static | Dmatched | 0.823 | 0.819 | 0.900 | 0.733 | 0.909 |
| Static | Moracle | 1.131 | 0.931 | 1.042 | 1.000 | 0.893 |

### Interpretation

1. **Against the same-initial-library faithful copier D**, L's average drifting late throughput is 1.4% higher, but cumulative fuel conversion is only 0.4% higher. Work and material investment are also slightly higher. This is a small conditional signal, not a demonstrated investment-adjusted advantage.
2. **Against Mmatched under drift**, L has 6.6% lower cumulative fuel conversion, 4.9% higher declared work investment and equal reported material investment. Fuel conversion per declared work is about 10.9% lower.
3. In static conditions, Mmatched exceeds L's cumulative fuel conversion by about 3.9% on average, even though L's late throughput is about 25.5% higher. This divergence is why late throughput cannot substitute for cumulative output.
4. Dmatched is a front-loaded, large standing-variation comparison with a different investment profile; it is not a clean equal-budget control.
5. Moracle is post-hoc initialized with L's final composition. It is an informed benchmark, not a feasible uninformed strategy or a strict mathematical upper bound.

The Mmatched material match is constructed by initializing it with the same total catalyst amount as L has at the end. It is therefore a useful material-matched counterfactual, but it front-loads the catalyst investment at t=0. The comparison does not equalize the timing of work expenditure, initial work endowment, or the opportunity cost of the initial catalyst library.

## Remaining accounting limitations

The current `material_investment` field is initial catalyst amount plus **net** replication extent. That is not a complete gross material ledger: it can conceal gross forward monomer uptake and reverse material return. The runner has now been amended to expose forward and reverse replication extents, gross monomer-equivalent uptake and reverse return separately in the next run.

The work metric is also a declared accounting convention, not a unique thermodynamic scalar price for every resource. Initial catalyst free energy, initial work-pool exergy, gross forward work and reverse recovery should remain separately visible. Work and material remain separate budget axes; no arbitrary weighted sum is justified.

## Conclusion and next gate

The revised initial-work charge closes one previously omitted endowment term and the numerical identities close within the stated tolerances. The evolutionary arm does **not** show a robust advantage over strong fixed-library controls in this pilot. In the drifting Mmatched contrast, it is worse on both cumulative output and declared work-normalized output.

This still does not answer the equal-investment question. The next gate is to save time-resolved cumulative work and gross material ledgers, construct a common feasible two-dimensional work/material budget region, and compare output only within that intersection without extrapolation. A separate common finite initial-endowment experiment is required to remove the front-loading asymmetry.

No result here supports claims about abiogenesis, the inevitability of life, or a universal thermodynamic law.
