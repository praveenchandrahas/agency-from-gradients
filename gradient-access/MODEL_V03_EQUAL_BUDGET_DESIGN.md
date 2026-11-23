# v0.3 design — equal-investment comparisons and thermodynamic audit

**Status: experimental design; not yet an implemented or validated model.** This document specifies the next validation gate after the v0.2 coupled-reaction prototype. It does not revise or upgrade the evidential status of v0.1 or v0.2 results.

## 1. Objective

Test whether mutation plus selection increases cumulative access to a kinetically constrained fuel gradient when evolving and non-evolving systems are compared at the same *time-resolved energetic and material investment*.

The primary comparison is not throughput per catalyst, nor a ratio of two independently accumulated costs. It is the attainable cumulative fuel-conversion output under common investment budgets.

The v0.2 standing-control experiment is not an equal-budget test: Mmatched and Dmatched are initialized at L's final catalyst abundance (front-loaded), while L builds that abundance during the run. This is useful as a material-matched counterfactual, but it does not equalize the timing or the work history. Its reported ratios must remain exploratory.

## 2. Preserve the thermodynamic boundary

Retain the declared v0.2 isothermal CSTR and explicitly state its boundary:

- Internal state: F/W, T/D, M/P and each catalyst genotype C_i.
- Reactions: fuel-to-work conversion, genotype-changing autocatalytic replication, and maintenance hydrolysis.
- Reservoir interfaces: both members of the F/W and M/P binary pools.
- Excluded from this abstract boundary: apparatus construction, pumping work not represented by the ideal CSTR flow term, pressure-volume work, heat leaks, catalyst synthesis before the initial state, and real molecular side reactions.

The result may be called *thermodynamically closed within the declared idealized boundary* only if every included reaction and reservoir exchange appears in both the state balance and entropy/free-energy ledger. It must not be described as complete accounting for a physical reactor.

## 3. Independent analytical gates

Before running a new parameter grid, test each of the following independently.

### 3.1 Stoichiometry and local detailed balance

Represent the reaction network by a stoichiometric matrix S and reaction extent vector J. Verify that every state derivative is generated from the same stoichiometric updates and reservoir-flow terms.

For every reversible reaction r, derive the affinity from the same species chemical potentials used in the free-energy function and verify:

- ln(v_r^+ / v_r^-) = A_r;
- sigma_r = J_r A_r is non-negative;
- at equilibrium, J_r = 0 and A_r = 0;
- multiplying forward and reverse catalytic rates by the same positive factor changes kinetics but not equilibrium.

For replication, test each parent-to-offspring channel separately, including the catalyst activity of the offspring in the reverse propensity. Mutation-kernel row sums and material conservation must be checked.

### 3.2 Reservoir exchange

For both binary pools, include both species in the flow entropy term. Test the expression against direct chemical-potential flux accounting over random positive states. Test limiting behaviour near the domain boundaries and reject unsupported zero-activity feeds rather than hiding singularities with clipping.

### 3.3 Work-pool balance

Verify pointwise and integrated that

work generation - work consumed by replication - work consumed by maintenance
= change in work-pool free energy,

using the same reaction extents and chemical potentials as the state ODE.

The initial T/D pool is an initial resource. Report its available exergy relative to the pool's equilibrium composition as an explicit initial endowment. Do not silently treat the initial ATP-like inventory as free.

### 3.4 Whole declared-boundary free-energy identity

For the chosen sign convention, verify at every state:

reservoir chemical free-energy input - change in internal system free energy
= total entropy-production rate.

Integrate separately over each constant-target segment and report pointwise and integrated residuals. Add tests that independently calculate the two sides, rather than reusing a helper that shares the implementation under test.

### 3.5 Numerical integrity

- No clipping, renormalization or silent state repair.
- Fail loudly if an activity leaves its physical domain.
- Demonstrate convergence under at least three maximum-step settings and two tolerances.
- Cross-check BDF against a second solver on non-stiff cases and a stochastic event reference for small populations.
- Report solver failures and all negative/null outcomes.

## 4. Define investment as a vector, not an arbitrary scalar

Do not combine work and material costs with an undocumented conversion factor. Report at least two independent cumulative budgets.

### Work/chemical-exergy budget

Report separately:

1. Initial catalyst free energy (the initial catalyst library is not free).
2. Initial available work-pool exergy relative to the T/D equilibrium state.
3. Gross forward work-currency expenditure on replication.
4. Gross forward work-currency expenditure on maintenance.
5. Reverse-reaction work recovery, separately (never hide it inside a negative cumulative cost).
6. Final stored work-pool exergy.

The net and gross quantities must both be available. The budget definition used for matching must be fixed before the run. If recovered work is credited, credit only the explicitly modelled reverse reaction and show the gross flows too.

### Material budget

Report separately:

1. Initial catalyst amount and genotype composition.
2. Gross monomer uptake for replication.
3. Reverse/degradation return of monomer-equivalent material.
4. Net catalyst material retained.
5. Polymer waste exported.

Do not use final catalyst count as a substitute for cumulative material investment.

### Mutation and search costs

The current v0.2 model has no separate proofreading/repair reaction. State that assumption explicitly. Any new mutation, repair, candidate-evaluation or search operation must either be represented by a physical reaction/resource debit or be labelled an unpriced algorithmic operation. Do not compare an unpriced adaptive-search control as if it were a physical chemistry control.

## 5. Equal-budget comparison protocol

For every arm, save time-resolved cumulative output and the complete investment vector. The primary output is cumulative net fuel-conversion extent; late throughput is secondary.

Construct the attainable output frontier in the two-dimensional (work/exergy investment, material investment) plane.

- Compare arms only over the common feasible budget region.
- At each preregistered budget pair, interpolate output along each arm's trajectory without extrapolation.
- Use a fixed interpolation rule and tolerance declared before looking at arm differences.
- If an arm cannot reach a budget pair, mark it infeasible; do not silently substitute its final state.
- Report cumulative output, output per work, output per material, and the Pareto frontier. Ratios are secondary summaries, not the primary test.
- Include initial library construction as a time-zero investment. A library front-loaded at t=0 must pay its full initial free-energy and material endowment.
- Also report a common finite *initial endowment* experiment in which every arm receives the same work and monomer budget at t=0 and must allocate it among catalyst construction, replication, maintenance and operation.

The initial-endowment experiment is the stronger primary design. It prevents a front-loaded control from receiving a larger resource endowment merely because it starts with more catalysts.

## 6. Required arms

At minimum:

- N: uncatalysed baseline.
- M: fixed random library, with its complete initial construction cost charged.
- D: faithful copying, no new mutation, same initial library as L.
- L: mutation plus selection, same initial library as D.
- D-large: faithful copying with a larger standing-variation library, charged for its complete time-zero construction.
- M-large: fixed library with the same initial total material as D-large.
- A: non-replicating adaptive search, only if candidate evaluation and information access are explicitly priced and matched.
- An ideal target-informed design may be reported as a non-physical upper-bound reference, never as a fair competitor.

A fixed-size or trajectory-matched arm may be added as a diagnostic, but it must not be confused with total-investment matching.

## 7. Experimental grid and inference

Use the v0.2 pilot only to select a tractable range. Expand beyond the 2-bit genotype space and include:

- smooth, rugged and epistatic genotype–phenotype maps;
- static and multiple target-switch schedules;
- activation barriers;
- mutation rate and explicit mutation/repair cost;
- turnover and maintenance demand;
- finite population size and stochastic extinction;
- sparse versus broad standing variation.

Use paired environmental histories with independent random streams for population events. Choose replicate count by a precision/power analysis from pilot variance. Freeze primary outcomes, budget definitions, common-budget grid, contrasts, exclusions and analysis code before the confirmatory run. Reserve held-out seeds.

## 8. Interpretation rules

A positive result must survive both work and material matching over the common feasible budget region. A benefit in late throughput alone is not sufficient. A benefit against a small initial library is not sufficient if a charged, larger standing-variation library matches or exceeds it.

A null or negative result is a valid outcome. No result from this abstract network establishes abiogenesis, inevitability of life, or a universal thermodynamic law.

## 9. Implementation sequence

1. Audit and independently test the existing v0.2 ledger, including the initial work-pool endowment.
2. Add time-resolved gross and net investment traces without changing the reaction dynamics.
3. Implement the common-budget frontier analysis and test it on synthetic trajectories with known answers.
4. Add a finite initial-endowment mode so all arms draw from the same work and material budgets.
5. Run a small deterministic pilot, inspect budget feasibility and numerical residuals, then freeze the design.
6. Only after these gates pass, run the paired stochastic experiment.
