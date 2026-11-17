# Experiment 01 — Persistence in a chemostatted autocatalytic network

**Status:** First computational protocol, v0.1  
**Model:** thermodynamic_emergence.chemistry  
**Question:** Under what feed activities does the specified autocatalytic network maintain a catalyst abundance substantially above its low-feed reference state?

## Hypothesis

For the stated reversible reaction network and fixed kinetic parameters, increasing the chemostatted feed activity of A increases the steady-state activity of autocatalyst X. Above the low-concentration linear invasion threshold, autocatalytic production can exceed first-order loss and support an enriched non-equilibrium steady state.

This is a model-conditional kinetic hypothesis. It is not a claim about real prebiotic chemistry or a general law of thermodynamic emergence.

## Model and intervention

Use:

- A + X <-> 2X + W
- X <-> D

Hold temperature, waste and degraded-reservoir activities, equilibrium constants and kinetic constants fixed. Vary only a_A over [1e-6, 0.05, 0.2, 0.5, 1.0, 2.0].

The low-feed reference is a_A = 1e-6; it is not a zero-feed condition. The approximate linear invasion threshold, neglecting the small reverse source from D, is a_A = k2+/k1+ = 0.1.

## Primary outcomes

1. Final catalyst activity x.
2. Relative enrichment over the analytic low-feed fixed point.
3. Relative error between numerical integration and the analytic fixed point.
4. Reaction-wise and total chemical entropy-production density.

## Controls and nulls

- Low-feed reference control: a_A = 1e-6.
- Below-threshold condition: a_A = 0.05.
- Above-threshold conditions: a_A = 0.2, 0.5, 1.0, 2.0.
- Numerical null: the integrated state should converge to the positive analytic fixed point for each parameter set.
- Thermodynamic consistency check: each reversible reaction's flux-affinity product should be non-negative, up to numerical tolerance.

## Predictions

- Catalyst abundance should remain near the low-feed background below the linear invasion threshold.
- Catalyst abundance should rise strongly above the threshold.
- The numerical solution should agree with the analytic fixed point within the declared tolerance.
- The reaction entropy-production contributions should be non-negative for all simulated states.

## Results from the illustrative baseline

The default feed activity a_A = 1 yields x ≈ 9.000011, compared with a low-feed reference fixed point x ≈ 9.9991e-5, an enrichment of approximately 9.0e4. The numerical integration agrees with the analytic fixed point to relative error below 1e-12 for the stored sweep cases.

These values are determined by illustrative model parameters. They are not empirical measurements and are not calibrated to any known chemical system.

## Failure criteria and limitations

The experiment fails its numerical checks if the solution becomes negative, entropy production is materially negative, or the integrated state does not approach the analytic fixed point. A failure of the predicted feed response would falsify this model's specific kinetic expectation, not the broader thermodynamic emergence programme.

Even a successful run does not demonstrate spontaneous seed-free formation of X: the initial condition contains X and the reverse R2 reaction supplies additional X from chemostatted D. It also does not demonstrate self-maintenance of a bounded chemical compartment, replication with heredity, selection, or abiogenesis. The chemostats are ideal reservoirs and their maintenance costs are outside the model boundary.


## Position in the research sequence

This experiment tests a single-species autocatalytic motif only. It does not test a collectively autocatalytic set. The next model should use a small RAF-like network with an explicit food set and catalyst assignments. Graph-theoretic RAF closure, kinetic accessibility from food, persistence, and spontaneous emergence must remain separate tests. The 2021 review by Ameta et al. documents substantial open challenges between experimentally observed chemical self-reproduction and canonical Darwinian evolution.
