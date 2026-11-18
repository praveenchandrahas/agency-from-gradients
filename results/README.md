# Results index

All numerical results below are model outputs under declared assumptions, not empirical observations of prebiotic chemistry.

## 1. Stellar–planetary radiation ledger

The zero-dimensional Earth-like baseline uses a blackbody star, spherical planet, spectrally neutral Bond albedo, Lambertian reflection and graybody thermal emission. It closes the energy balance at approximately 238.205 W m⁻² global mean absorbed/emitted power (residual about -5.7e-14 W m⁻²). Effective emission temperature is approximately 254.586 K; net radiative entropy export is approximately 1.27318 W m⁻² K⁻¹. Interpreting this as internal entropy generation is conditional on steady entropy storage and no matter or other non-radiative entropy transfers. The Petela solar-exergy estimate is approximate.

Files: [baseline](earth_like_baseline.json), [albedo sensitivity](albedo_sensitivity.csv), [model guide](../models/stellar_planet/README.md).

**Supports:** a numerically closed radiative ledger under its assumptions. **Does not support:** climate, habitability, local gradients, chemical free-energy availability, life or agency.

## 2. Single chemostatted autocatalyst

Network: A + X ⇌ 2X + W; X ⇌ D. A, W and D are fixed reservoirs; X is dynamic. Starting X activity is 1e-4; final X is approximately 9.000011, versus background-control equilibrium X approximately 9.9991e-5 (about 90,008× enrichment). Total reported reaction entropy production is approximately 8.61506 J L⁻¹ K⁻¹ s⁻¹; free-energy dissipation rate approximately 2,568.58 J L⁻¹ s⁻¹.

Files: [baseline](local_chemical_baseline.json), [feed sensitivity](local_chemical_feed_sweep.csv), [theory](../theory/04-local-chemical-disequilibrium.md).

**Limitations:** X is initially nonzero and reverse D→X supplies more X. Reservoir maintenance is outside the boundary. Chemistry and parameters are abstract; this is not seed-free emergence or a prebiotic pathway.

## 3. Finite-resource mutual catalysis

A/B are finite food resources; X/Y mutually catalyse production with reversible loss. Catalysis accelerates finite-time conversion, but the closed batch relaxes toward equilibrium and does not sustain a NESS.

The matched-state catalyst-removal sweep holds the pre-event state and remaining food fixed, then varies only the post-event background rate. Recovery falls sharply with removal severity; lowering the background factor has only a small effect. The earlier unmatched sweep is confounded because changing background rates before intervention changes catalyst abundance and food remaining at intervention. Recovery ratios above one in that sweep do not mean restoration of a mature state.

Files: [matched-state sweep](raf_matched_recovery_sweep.json), [earlier confounded sweep](raf_perturbation_sweep.json), [theory](../theory/05-collective-autocatalysis.md), [protocol](../experiments/protocols/03-catalyst-removal-recovery.md).

## 4. Continuously driven open reactor

The abstract mutually catalytic network is placed in a well-mixed CSTR with continuous feed and dilution. At dilution 0.05 s⁻¹, catalytic strength 10 and duration 300 s:

| Measurement | Catalytic | Uncatalysed matched-flow null |
|---|---:|---:|
| Final X+Y activity | 1.4022044 | 0.00796736 |
| Operational NESS diagnostic | Pass | Pass |

Catalytic X+Y abundance is about 176× the null in this parameterization, but catalysis is not required for the NESS diagnostic. Catalytic baseline entropy-production rates: reaction 1.052176 and reservoir exchange 0.0730092 J L⁻¹ K⁻¹ s⁻¹, reported separately.

Files: [baseline summary](open_reactor_baseline_summary.json), [model and boundary](../theory/06-open-reactor-ness.md), [protocol](../experiments/protocols/04-open-reactor-ness.md).

**Limitations:** all species including X/Y receive positive feed, so the model is continuously seeded. The exchange entropy term is not the full engineering cost of pumping, mixing, reservoirs or temperature control. Operational NESS is a finite-window diagnostic, not proof of global stability.

## 5. Open-reactor recovery and sensitivity

Full report: [resilience and recovery sensitivity](open_reactor_resilience_sensitivity.md). CI: [workflow run #44031401732](https://github.com/praveenchandrahas/thermodynamic-emergence/actions/runs/44031401732), all 14 steps passed.

- **Positive-feed limit:** at 99% removal, reducing positive X/Y feed from 1e-8 to 1e-14 barely changes recovery: approximately 99.925% of pre-event abundance is restored, with the 90% threshold crossed in 65.25 s. This is not zero-feed recovery: 1% of the original catalyst remains.
- **Washout map:** pre-event operational NESS passes at dilution 0.01–0.1 s⁻¹ and fails at 0.2 s⁻¹. This only brackets a possible loss-of-steadiness region between 0.1 and 0.2 s⁻¹ for this coarse grid and 150 s preconditioning. At 0.01 s⁻¹ recovery is incomplete within 150 s; at 0.025 s⁻¹ it is about 97.5%; at 0.05–0.1 s⁻¹ it is near complete. The 0.2 s⁻¹ cases are not stationary-reference perturbation tests.
- **Horizon:** at 0.05 s⁻¹ and 99% removal, 150 s post-event restores about 99.925% abundance but fails the NESS drift test. At 450 s and 750 s post-event, the operational NESS criterion passes and abundance returns to the unperturbed value to numerical precision.

## Cross-model conclusions and evidence boundary

1. The radiative ledger is a physical accounting baseline, not a mechanism for life.
2. Seeded autocatalysis amplifies X under fixed reservoir conditions, but the seed source is explicit.
3. Mutual catalysis accelerates finite-batch conversion, but does not sustain a NESS in a closed finite batch.
4. A continuously driven abstract network can maintain an operational NESS; the uncatalysed null also does so at lower X+Y abundance.
5. Open-reactor abundance recovers after severe removal in the baseline regime, but surviving catalysts remain and full stationarity takes longer.
6. Washout and observation horizon materially affect outcomes. No universal entropy-driven organizing law has been demonstrated.

Current evidence reaches model demonstration under selected assumptions with limited robustness checks. It does not reach empirical support or generalization. No model yet includes chemically validated prebiotic pathways, stochastic finite-molecule extinction, spatial gradients/compartments, replication with heredity, Darwinian evolution or intelligence. Entropy production is measured as an outcome, never used as a fitness bonus.
