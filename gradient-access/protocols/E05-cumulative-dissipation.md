# E05 — Cumulative dissipation and energetic accounting

## Question
Does evolutionary access translate into greater cumulative dissipation over a declared horizon?

## Required ledgers
- Reaction entropy production.
- Reservoir-exchange entropy production.
- Net reaction extent and free-energy release.
- Stored free energy.
- Catalyst construction/reproduction expenditure.
- Catalyst maintenance expenditure.
- Adaptive-search expenditure.
- Fuel inflow, outflow and reactor inventory.

## Accounting rule
Do not add stored energy to dissipated energy until it is actually dissipated. Avoid counting the same reaction free energy both as heat and as stored catalyst energy.

## Primary comparison
Paired-seed cumulative entropy production and cumulative free-energy release at the same external forcing and horizon. Report instantaneous late-window rates separately.

## Current limitation
The v0.1 implementation is an abstract dimensionless reactor. The thermodynamic ledger and its system boundary need independent derivation and analytic validation before interpreting numerical totals as physical entropy.
