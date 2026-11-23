# Simulation Architecture

## Layers

1. **Gradient landscape:** fuel reservoir, waste complement, free-energy affinity, activation barriers and environmental drift.
2. **Catalytic phenotype:** bit-string genotype mapped to a lock-specific catalytic multiplier.
3. **Reactor kinetics:** reversible forward/reverse rates multiplied equally by catalysis.
4. **Population dynamics:** reproduction, mutation, selection, turnover, extinction and population caps.
5. **Thermodynamic diagnostics:** reaction entropy production and declared fuel-reservoir exchange entropy.
6. **Investment ledger:** initial catalyst construction, reproduction, maintenance, mutation and adaptive-search costs.
7. **Analysis:** paired-seed contrasts, bootstrap uncertainty, per-catalyst rates and sensitivity analysis.

## Time and resource accounting

Simulation duration is declared in residence-time units and integration uses dt = duration / steps. Environmental drift and catalyst turnover are hazards per residence-time unit, converted to per-step probabilities. Initial catalyst construction, reproduction, maintenance, mutation and adaptive-search costs are reported separately. Equal late-window catalyst abundance is not equivalent to equal cumulative investment.

## Experimental arms

N, M, D, L, U and A are defined in the README. Mmatched, Dmatched, Amatched and Umatched are controls initialized at the paired L run's rounded late-window mean. Dmatched reproduces faithfully without new mutation; the others are fixed populations or bounded search. D and L begin from identical random genotype libraries under paired seeds. D has no new mutation but can select among standing variation.

## Core invariants

- Catalysis multiplies forward and reverse rates by the same factor.
- Catalysts do not change the equilibrium constant.
- At B = 0, catalytic leverage is zero and all arms share the passive reaction rate.
- Entropy production never enters reproductive fitness.
- Fuel balance residuals are reported.
- Stored-energy coupling is disabled until explicit storage chemistry is implemented.

## Known simplifications

The first executable model uses bit-string keys, an abstract scalar reaction per lock and a well-mixed flow reactor. It has no spatial transport, identified prebiotic molecules, finite-molecule stochasticity, compartment chemistry or complete waste-reservoir entropy accounting. See [MODEL_LIMITATIONS.md](MODEL_LIMITATIONS.md).
