# Open-reactor resilience and recovery sensitivity results

## Run provenance

- Repository: `praveenchandrahas/thermodynamic-emergence`
- Workflow run: [#44031401732](https://github.com/praveenchandrahas/thermodynamic-emergence/actions/runs/44031401732)
- Commit tested: `ea0fe3fc2498b4c908137d1c631dc9cc4e78530e`
- Workflow conclusion: success; all 14 steps completed.
- Integrator step: 0.005 s.
- These are deterministic outputs from the current illustrative model and parameterization, not empirical measurements.

## 1. Positive catalyst-feed limit

Conditions: 99% removal of X and Y at t=150 s; post-event feed activities 1e-8, 1e-10, 1e-12 and 1e-14; endpoint t=300 s.

| Post-event X/Y feed activity | Fraction of removed X+Y recovered | Fraction of pre-event X+Y restored | Recovery time to 90% | Post-event operational NESS |
|---:|---:|---:|---:|---|
| 1e-8 | 0.9992452355 | 0.9992527832 | 65.25 s | No |
| 1e-10 | 0.9992452177 | 0.9992527655 | 65.25 s | No |
| 1e-12 | 0.9992452175 | 0.9992527653 | 65.25 s | No |
| 1e-14 | 0.9992452175 | 0.9992527653 | 65.25 s | No |

The measured differences across four orders of magnitude in positive catalyst feed are negligible at the reported precision. The pre-event state passed the operational NESS diagnostic; the post-event state did not within the 150 s observation window (relative endpoint drift approximately 0.0026466).

**Interpretation:** recovery in this experiment is not materially dependent on the tested trace-feed range. It is not evidence for seed-free emergence: after 99% removal, 1% of the pre-existing catalyst population remains, and every tested feed is strictly positive. The experiment tests sensitivity to a small external feed in a system that retains catalysts, not spontaneous generation from zero catalyst.

## 2. Washout rate × catalyst-removal map

Conditions: flow rates 0.01, 0.025, 0.05, 0.1 and 0.2 s^-1; removal fractions 0.9, 0.99, 0.999 and 0.9999; intervention at 150 s; 150 s post-event observation.

| Flow rate (s^-1) | Pre-event X+Y | Pre-event operational NESS | Removed-X+Y recovery range | Post-event NESS outcomes | Interpretation |
|---:|---:|---|---:|---|---|
| 0.01 | 1.74727 | Yes | 0.77939–0.77994 | 0/4 | Abundance recovery incomplete; 90% recovery threshold not reached in any condition |
| 0.025 | 1.61904 | Yes | 0.97465–0.97467 | 0/4 | Strong but incomplete recovery; threshold reached in about 91.65–97.5 s |
| 0.05 | 1.40220 | Yes | 0.999245–0.999245 | 0/4 | Near-complete abundance recovery; post-event state not stationary within 150 s |
| 0.1 | 0.95613 | Yes | 0.999956–1.000041 | 2/4 | Near-complete recovery; post-event NESS detected for 90% and 99% removal, not for 99.9% or 99.99% |
| 0.2 | 0.04613 | **No** | 0.99920–1.04487* | 0/4 | Pre-event operating point itself fails NESS criterion; do not interpret as a valid perturbation-resilience comparison |

*At 0.2 s^-1, the recovery fraction can exceed one because the pre-event state is not an established stationary reference. The unperturbed trajectory is also changing. These ratios are not evidence of super-recovery.

**Interpretation:** Within this coarse grid, 0.2 s^-1 is already beyond the tested range where the model reaches the specified pre-event operational NESS; 0.1 s^-1 still passes. This brackets a possible loss-of-operational-steadiness region between 0.1 and 0.2 s^-1 for this model and 150 s preconditioning window. It does not establish a critical washout threshold: the grid is coarse, and a longer preconditioning interval could alter classification. At lower flow, post-perturbation abundance recovery is slower or incomplete over 150 s. Full-state NESS is stricter than abundance recovery.

## 3. Observation-horizon sensitivity

Conditions: flow 0.05 s^-1; 99% removal at t=150 s; same dynamics and parameters; total duration 300, 600 or 900 s.

| Total duration | Post-event observation | Fraction of pre-event X+Y restored | Fraction of removed X+Y recovered | Relative endpoint drift | Max species CV | Operational NESS |
|---:|---:|---:|---:|---:|---:|---|
| 300 s | 150 s | 0.999252783 | 0.999245236 | 0.00264657 | 0.00075249 | No |
| 600 s | 450 s | 1.000000029 | 1.000000029 | 2.07e-8 | 5.26e-9 | Yes |
| 900 s | 750 s | 1.000000029 | 1.000000029 | 0.0 | 0.0 | Yes |

The 90%-of-pre-event abundance threshold was crossed at 65.25 s in all three runs.

**Interpretation:** The earlier 150 s post-event failure was a finite-observation-window issue for this baseline parameterization. With 450 s and 750 s of post-event observation, the model satisfies its operational NESS diagnostic and returns to the unperturbed abundance to numerical precision. This supports relaxation back to the same measured catalytic abundance under this perturbation. It is not a mathematical proof of global asymptotic stability, uniqueness of the attractor, or return of every unreported structural property.

## Overall conclusions

1. **Catalyst abundance is highly recoverable in the baseline regime.** At 0.05 s^-1, 99% removal is followed by recovery of about 99.925% of removed X+Y within 150 s.
2. **Recovery is not the same as immediate stationarity.** The 300 s run restores abundance closely but fails the strict endpoint-drift NESS criterion; longer observation passes it.
3. **The tested trace catalyst feed is not the driver of recovery.** The 1e-8 to 1e-14 positive-feed sweep is virtually invariant, but surviving catalyst remains. Zero feed was neither tested nor numerically admissible under the current ideal-reservoir logarithmic formulation.
4. **Washout constrains persistence.** At 0.2 s^-1 the pre-event state fails the NESS test, while 0.1 s^-1 passes. This is a bracket for further study, not a measured universal threshold.
5. **The response depends on flow and removal severity.** At 0.01 s^-1 the 150 s post-event window is insufficient even to reach 90% abundance recovery; at 0.025 s^-1 recovery is substantial but incomplete; at 0.05–0.1 s^-1 it is nearly complete.

## Limitations and next tests

- Abstract eight-species reaction network; illustrative parameters, not chemically calibrated or tied to a prebiotic pathway.
- Positive X/Y feed remains in all simulations. No seed-free origin-of-catalysis claim is supported.
- Catalyst removal is an imposed state intervention; physical separation work and associated entropy production are not included.
- The ideal, well-mixed CSTR approximation omits spatial gradients, diffusion, compartments, stochastic extinction, finite molecule counts and reactor engineering costs.
- Operational NESS is a finite-window numerical criterion, not a Lyapunov proof or exhaustive attractor analysis.
- The washout grid is sparse. Refine flow rates between 0.1 and 0.2 s^-1 and lengthen preconditioning to distinguish a true bifurcation from slow drift.
- Vary initial catalyst abundance, not only the fraction removed, to test extinction/recovery boundaries. Include a matched zero-feed formulation with finite-state stochastic kinetics or a thermodynamically consistent treatment that avoids the zero-activity logarithmic singularity.
- Repeat with independent parameter sweeps and numerical step-size/convergence checks before making broad claims.

## Merge recommendation

**Recommend merging the experiment and its results as a reproducible, model-conditional result.** CI passed all steps, the expanded sweeps ran, and the outputs support bounded conclusions. Do not present them as evidence that entropy alone produces life, seed-free autocatalysis, biological self-repair, or a universal maximum-entropy-production principle. The next scientific increment should refine the washout boundary, test catalyst extinction under decreasing initial seed, and strengthen stability/numerical-convergence analysis.
