# Experiment 02 — Mutual catalysis in a finite-resource batch

**Model:** thermodynamic_emergence.raf  
**Question:** Does reciprocal catalysis accelerate the finite-time production of the network's own catalytic species relative to an otherwise identical uncatalysed null?

## Hypothesis

For the declared abstract network, reciprocal catalysis increases X + Y at a fixed finite time compared with the same network with catalytic strength set to zero. The result is a kinetic hypothesis about this network and parameterization, not a claim about prebiotic chemistry.

## Network

Food set: F = {A, B}.

- R1: A <-> X + W_X, catalysed by Y.
- R2: B <-> Y + W_Y, catalysed by X.
- R3: X <-> D_X (loss).
- R4: Y <-> D_Y (loss).

R1 and R2 form the RAF-like reaction set. R3 and R4 are loss reactions outside that set.

## Intervention and null

Run the default finite-batch configuration. Compare:
- Catalytic case: alpha = 100.
- Uncatalysed null: alpha = 0.

All initial activities, reaction equilibrium constants, forward rates, time step and finite-resource boundary remain identical.

## Primary outcomes

1. X + Y at 10 s.
2. Fraction of initial A + B converted.
3. Integrated reaction entropy production.
4. Four moiety-balance errors.
5. Minimum reaction-wise entropy-production rate.

## Controls

- Uncatalysed kinetic null (alpha = 0).
- Numerical conservation check for A + X + D_X, A + W_X, B + Y + D_Y and B + W_Y.
- Thermodynamic check that each reversible reaction's flux-affinity product is non-negative up to numerical tolerance.
- The catalyst multiplier is applied equally to forward and reverse rates, so the equilibrium constants are unchanged.

## Failure criteria

The run fails its numerical checks if moiety balances drift beyond tolerance, any species becomes non-positive, or any reaction entropy-production contribution is materially negative. The model-specific kinetic prediction is not supported if the catalytic case does not produce more X + Y than the uncatalysed null at the declared finite time.

## Interpretation boundary

The initial chemical disequilibrium is finite; there is no chemostat or continuous external energy supply. The model should relax toward equilibrium and cannot sustain a non-equilibrium steady state. Small uncatalysed background rates seed the network, and initial X and Y are tiny but nonzero. The model therefore does not demonstrate spontaneous molecular assembly, seed-free emergence, life, heredity or evolution.
