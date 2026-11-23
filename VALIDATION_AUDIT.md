# Scientific validation audit — v0.1

**Status: blocking audit. The long-horizon numerical results are reproducible outputs of the code, but the current implementation does not yet support claims of energetic-cost parity or complete thermodynamic accounting. Do not treat the previous evolutionary advantage as validated at comparable total investment.**

## Scope

This audit checks whether the implementation supports the quantities and comparisons used in the exploratory findings. It is a code-and-model audit, not an external experimental validation.

## Blocking findings

### V1 — Reproduction expenditure is never accumulated

In `src/ega/model.py`, `cumulative_reproduction_energy` is initialized to zero and returned, but no code increments it when births occur. `src/ega/experiments.py` includes this field in `total_investment_energy`. Consequently, the reported total investment omits the reproduction expenditure of D, L and Dmatched. The resulting total-investment contrasts are invalid.

The birth calculation uses an expected per-offspring mutation cost to cap births, while actual mutation expenditure is computed after offspring are generated. Actual mutation cost is recorded but is not debited from an explicit work/energy store. This is not a closed energy budget.

### V2 — The energy available for reproduction is not the reaction free-energy release

The model computes `released_energy = throughput * cfg.delta_mu`. But the implemented reversible rates are

`forward = rate * fuel` and `reverse = rate * exp(-delta_mu) * (1-fuel)`.

The actual dimensionless reaction affinity is therefore

`A = ln(forward/reverse) = delta_mu + ln(fuel/(1-fuel))`.

It varies with reactor composition. Multiplying net throughput by the constant standard-affinity parameter `delta_mu` is not the actual reaction free-energy dissipation rate except at a special composition. More importantly, the model does not specify a chemically coupled work-producing reaction that converts this free energy into the work used for replication. Reaction dissipation cannot simply be assumed to be fully available as reproductive work.

### V3 — Fuel-reservoir exchange entropy omits the complementary waste species

The state variable represents a binary mixture: fuel activity `f` and complementary waste activity `1-f`. The feed has `f_in` and `1-f_in`. For ideal binary mixing, the exchange contribution must include both species:

`q (f_in-f) ln(f_in/f) + q ((1-f_in)-(1-f)) ln((1-f_in)/(1-f))`.

The current code includes only the fuel term. It therefore does not calculate the full ideal-mixture exchange entropy for the stated two-species boundary. The pure-fuel default `fuel_feed=1` also creates a zero-activity boundary for the waste species, requiring special treatment rather than an unqualified finite ideal-mixture formula.

### V4 — The matched controls are not all matched over the observation window

Mmatched and Amatched are fixed-size populations initialized to L's rounded late-window mean abundance. Dmatched is initialized at that abundance but can reproduce and grow thereafter. It is therefore an **initial-abundance-matched** control, not a trajectory- or late-window-abundance-matched control. The current naming and interpretation can invite a stronger claim than the design supports.

### V5 — The thermodynamic boundary remains incomplete

The implementation omits a complete stoichiometric ledger for all chemical species, work currency, catalyst synthesis, mutation, replication, turnover, pumping, mixing apparatus, heat transfer and reservoir regeneration. The current `sigma_total` is a partial diagnostic, not the entropy production of a closed, fully declared physical boundary.


### V6 — The reproductive energy constraint is not binding in the reported runs

The published trajectory artifact shows that D and L populations approach the 500-catalyst cap very rapidly. There are 200 trajectories per arm (400 D/L trajectories total). Across all barriers and designs, 80% of D and 80% of L trajectories are already at or above 400 catalysts after the first integration step; by the second step, all D and all L trajectories are at or above 400. At barriers 0, 4 and 8 kT, all D/L runs are already at or above 400 after the first step. At 12 kT, the mean first-step populations are approximately 268 for D and 254 for L; after the second step, 100% of D and 80% of L runs are at or above 400. All D/L runs eventually touch the 500 cap, but the median first-hit step is 27 for D and 24 for L.

This rapid approach to capacity indicates that the configured reproduction/maintenance costs do not create a sustained resource-limited growth regime over most of the tested grid. The late-window comparison is primarily a competition among near-capacity populations, not an experiment demonstrating persistence under a tight energy budget. The result is consistent with the cost-scale mismatch already identified in V1/V2 and strengthens the requirement for explicit work coupling and cost calibration.

## Consequences for the existing findings

- The raw throughput trajectories remain outputs of the specified abstract kinetic model.
- The paired-seed design and shared drift histories remain useful implementation properties.
- The zero-barrier invariance remains a valid code-level invariant for the current rate construction.
- The previous total-investment metric and any claim of energetic-cost matching are not valid because reproduction expenditure is missing.
- Most D/L trajectories approach the cap rapidly: 80% are at or above 400 after the first step and all are at or above 400 after the second; all eventually touch 500. This indicates no sustained resource-limited growth regime over most of the tested grid.
- The current entropy totals are partial and should not be presented as complete reactor entropy production.
- The L-versus-Dmatched result is an initial-abundance comparison with a replicating control, not a matched population-trajectory comparison.
- None of these simulations establishes an empirical thermodynamic law or a physical mechanism for the origin of replicators.

## Required redesign before new confirmatory runs

1. Specify an explicit stoichiometric network containing fuel, waste, an internal work currency and the work-consuming replication process.
2. Derive every reaction affinity from chemical potentials and every flux from a local-detailed-balance kinetic law.
3. Couple energy generation to work production explicitly. Track the work currency as a state variable; replication, mutation, maintenance and search must debit it. Prevent negative work inventory.
4. Include both fuel and waste in reservoir exchange, and include all work-currency and replication reactions in the entropy-production ledger.
5. Replace clipping with a positivity-preserving integration method or a validated timestep restriction; report any numerical correction explicitly.
6. Make population controls explicit: fixed-size, initial-size-matched, trajectory-matched and total-investment-matched are distinct designs and must be named separately.
7. Add conservation, detailed-balance, equilibrium, non-negative entropy production, work-budget closure and integration-convergence tests derived analytically.
8. Sweep genotype–phenotype maps (smooth, rugged and epistatic), key length, mutation rate, population cap, turnover, coupling efficiency and drift.
9. Increase independent paired seeds, predeclare primary contrasts and uncertainty methods, and use a held-out confirmatory run after the model and analysis are frozen.

## Decision

The v0.1 run is retained as an exploratory software/model demonstration. It is not a valid energetic-cost test. The next model version must pass the above analytical and numerical gates before evolutionary advantage is re-evaluated.