# Experiment 03 — Catalyst removal, recovery and background seeding

**Model:** thermodynamic_emergence.raf  
**Question:** After a mutually catalytic network has developed, how much of its X+Y abundance can it recover after catalyst removal, and how does this depend on the residual uncatalysed background rate?

## Hypothesis

At a fixed finite endpoint, the degree of recovery depends jointly on removal severity, residual food, surviving catalyst abundance and background reaction kinetics. The experiment does not presume complete recovery.

## Intervention

1. Evolve the finite-batch model for 5 s.
2. Remove 90%, 99% or 99.9% of both X and Y.
3. Continue the same reactor for the remaining 5 s.
4. Compare with a matched unperturbed run.

The removal operation is material outflow. The post-intervention conservation ledger begins from the remaining reactor inventory. The physical energy cost of removing/separating catalyst material is not included.

## Factorial sweep

- Removal fractions: 0.9, 0.99, 0.999.
- Pre-perturbation background factor is held at 1.0 for every condition. After removal, the background factor is set to 1, 0.1, 0.01 or 0.001.
- Catalytic strength, equilibrium constants, food, and duration otherwise remain fixed.

The production flux multiplier is epsilon + alpha times the reciprocal catalyst activity. It is applied equally to forward and reverse fluxes, preserving each reaction's equilibrium constant. The sweep changes epsilon only after the intervention, so all conditions share the same pre-perturbation history, catalyst abundance and remaining food. The unperturbed reference retains epsilon = 1 throughout.

## Primary outcomes

1. Fraction of removed X+Y recovered.
2. Fraction of pre-perturbation X+Y restored.
3. Final X+Y relative to the unperturbed endpoint.
4. Food remaining at intervention and at endpoint.
5. Post-intervention moiety-balance errors.

The recovery metrics are intentionally not clipped: values below zero or above one are possible and should be interpreted literally.

## Controls and numerical checks

- Matched unperturbed run.
- Matched background-factor runs.
- Post-intervention material balances relative to the remaining inventory.
- Reaction-wise entropy-production non-negativity.
- Time-step alignment for the intervention time.

## Interpretation boundary

This tests regeneration after a specified material removal in an abstract seeded network. It is not evidence of biological self-repair, seed-free emergence, heredity, Darwinian evolution or persistence under sustained environmental forcing. Apparent recovery must be interpreted alongside remaining food and background-rate dependence.
