# 06 — Continuously driven chemical organization in an open reactor

**Status:** Third executable chemical model, version 0.1  
**Purpose:** Test whether a continuously maintained chemical-potential gradient can support a non-equilibrium steady state (NESS) in a mutually catalytic network, and determine how catalytic strength and throughput affect its abundance and dissipation.

## 1. The question

The finite-batch RAF-like model showed that reciprocal catalysis can accelerate conversion of a finite food inventory. It could not establish persistent organization under continuing environmental supply: its free-energy store was finite and its trajectory ultimately relaxed toward equilibrium.

This model asks:

> Under what feed, dilution and catalytic conditions can a continuously driven chemical network maintain a non-zero population of its catalytic intermediates in a stationary non-equilibrium state?

This is a necessary intermediate test between finite-batch autocatalysis and any claim about living systems. A NESS is not life, replication, heredity or evolution.

## 2. Reactor and reaction network

The model uses a well-mixed continuous stirred-tank reactor (CSTR). The internal reaction network remains:

\[
A \rightleftharpoons X + W_X \quad (R_1;\; catalyst\;Y)
\]

\[
B \rightleftharpoons Y + W_Y \quad (R_2;\; catalyst\;X)
\]

\[
X \rightleftharpoons D_X \quad (R_3), \qquad
Y \rightleftharpoons D_Y \quad (R_4).
\]

The reaction fluxes are those of the finite-batch model. Reciprocal catalysis multiplies forward and reverse production rates equally, preserving each reaction's equilibrium constant.

All species exchange with finite-activity reservoirs through one dilution rate \(D\). For species \(i\), the net exchange term is:

\[
J_i^{ex}=D(c_i^{feed}-c_i).
\]

The state equation becomes:

\[
\dot{\mathbf c}=S\mathbf v + D(\mathbf c^{feed}-\mathbf c).
\]

The feed activities for A and B are set to one by default. Every other species has a small positive feed activity (default \(10^{-8}\)). This keeps all reservoir chemical potentials finite, but it also continuously supplies trace X and Y. The model is therefore explicitly seeded by its feed boundary and cannot demonstrate seed-free emergence.

## 3. Thermodynamic accounting

Reaction entropy production is calculated inside the reactor:

\[
\dot S_{gen}^{rxn}/V
=c^\circ\sum_r v_r\frac{-\Delta_rG_r}{T},
\qquad
\Delta_rG_r=RT\ln(Q_r/K_r).
\]

The finite-reservoir exchange term is separately calculated as:

\[
\dot S_{gen}^{ex}/V
=c^\circ\sum_i J_i^{ex}
\frac{\mu_i^{feed}-\mu_i}{T}
=c^\circ R\sum_i
J_i^{ex}\ln\left(\frac{c_i^{feed}}{c_i}\right).
\]

For the declared ideal-activity exchange law, each term is non-negative: the net exchange flux has the same sign as the reservoir-to-reactor chemical-potential difference.

The reported total is the sum of these two declared contributions. They are not collapsed into one opaque number. This accounting is an idealized chemical boundary, not a complete reactor engineering ledger.

**Not included:** mechanical pumping and mixing work; construction, regeneration and maintenance of reservoirs; temperature-control and heat-exchanger costs; spatial transport and reactor-wall dissipation. In particular, the exchange entropy term must not be presented as the complete energetic cost of maintaining the chemostats or apparatus.

The code reports cumulative feed and outflow activity, but does not assign molecular identities, standard chemical potentials or empirical reservoir work costs.

## 4. Operational NESS criterion

A finite numerical trajectory cannot prove existence or global stability of a mathematical steady state. The implementation therefore uses an explicit operational criterion.

Over the final fraction of the simulated trajectory (default 20%), it calculates:

1. Maximum relative difference between the first and last sampled concentration of each species.
2. Maximum coefficient of variation across the sampled window for any species.

A NESS is flagged only if both are below the configured tolerance (default \(10^{-3}\)). This is a finite-window diagnostic. It can miss slow drift, long-period oscillations or multiple attractors. A longer-horizon and perturbation stability analysis is needed before claiming a stable NESS.

## 5. Controls and comparisons

The principal null is the same reactor with the same feed composition, dilution rate, initial state, reaction constants and integration interval, but with catalytic strength set to zero.

The first sweep crosses catalytic strength with dilution rate. This tests whether persistent catalytic abundance depends on the balance between reaction kinetics and washout. It also reports reaction and reservoir-exchange entropy production separately.

A valid comparison must preserve feed composition and flow conditions. The model does not reward higher entropy production; entropy production is an outcome to measure. More dissipation is not automatically more organization, fitness or persistence.

## 6. Initial baseline result

The first CI baseline used the default settings above for 300 s with a 0.002 s RK4 step. The terminal-window diagnostic classified both the catalytic reactor and the matched-flow uncatalysed null as operational NESS cases.

| Measurement | Mutual catalysis | Uncatalysed null |
|---|---:|---:|
| Final X + Y activity | 1.4022044 | 0.00796736 |
| Operational NESS flag | Yes | Yes |

The catalytic case therefore maintained about 176 times the X+Y abundance of the matched-flow null in this parameterization. Importantly, mutual catalysis did **not** create the NESS condition: the uncatalysed reactor also reached the operational criterion, at a much lower catalytic-species abundance.

For the catalytic baseline, the reported terminal entropy-production rates were:

- Reaction contribution: 1.052176 J L⁻¹ K⁻¹ s⁻¹.
- Reservoir-exchange contribution: 0.0730092 J L⁻¹ K⁻¹ s⁻¹.

These are separate terms for the declared idealized boundary. They are not the total engineering cost of maintaining the reactor and reservoirs. The reproducible rounded summary is in [results/open_reactor_baseline_summary.json](../results/open_reactor_baseline_summary.json). GitHub Actions run 44028400465 passed all 36 unit tests and all workflow commands, including the baseline and matched-flow comparison.

This is one illustrative parameterization, not a phase diagram. It does not establish a universal advantage for autocatalytic networks, nor a causal relation between entropy production and organization. The continuous trace feed of X and Y is also a source of seeds.

## 7. Interpretation boundaries

A successful result can support only a conditional statement about this abstract CSTR: under the selected rates, feed composition and dilution, a mutually catalytic reaction network can maintain some non-zero stationary abundance while consuming and exporting chemical material.

It cannot establish:
- spontaneous formation of the network from unstructured matter;
- a chemically plausible prebiotic pathway;
- a universal principle of maximum entropy production;
- self-repair, replication with heredity or Darwinian evolution;
- the emergence of life, agency or intelligence;
- a planetary-scale entropy budget.

A failed NESS test is also conditional: it may mean the selected feed, washout, rates or simulated horizon do not support stationarity. It does not rule out other networks or environmental regimes.

## 8. Next discriminating experiments

1. Extend simulation horizons and test whether the operational NESS classification is stable to window length and tolerance.
2. Apply perturbations to a reactor that has reached its candidate NESS and measure return times, basin of attraction and washout thresholds.
3. Vary trace X/Y feed over orders of magnitude, including a boundary-limit study, to quantify dependence on continuous seeding.
4. Compare different catalyst assignments under matched stoichiometry, feed, dilution and kinetic scale.
5. Sweep feed chemical potentials and dilution to identify persistence regions, rather than selecting a single favourable parameter point.
6. Add explicit pump, separation and reservoir-regeneration work only when the physical process and its thermodynamic boundary are specified.
7. Map recovery across washout rates and perturbation severities, while checking that each pre-event reactor actually satisfies the operational NESS criterion.
8. Perform a positive-seed-feed limit study and longer post-perturbation horizons. The current ideal-reservoir expression requires strictly positive feed activities, so this cannot be interpreted as a true zero-seed experiment.

The next conceptual transition is not from NESS directly to life. It is from stationary dissipative chemistry to chemical structures that reproduce with heritable variation under sustained driving.


## 9. Recovery and resilience sensitivity results

The expanded recovery programme is documented in [results/open_reactor_resilience_sensitivity.md](../results/open_reactor_resilience_sensitivity.md), with a cross-model index in [results/README.md](../results/README.md). GitHub Actions run [#44031401732](https://github.com/praveenchandrahas/thermodynamic-emergence/actions/runs/44031401732) completed all 14 steps successfully.

### 9.1 Positive catalyst-feed limit

At 99% removal, post-event X/Y feed was reduced from 1e-8 to 1e-14. Across all four positive feed activities, approximately 99.9245% of removed X+Y was recovered and the 90%-of-pre-event abundance threshold was crossed in 65.25 s. Differences across this feed range are negligible at reported precision.

This is not a seed-free test. One per cent of the original catalyst population remains, and all feed activities are strictly positive. The result shows that recovery in this parameterization is not materially sensitive to the tested trace-feed range; it does not show that catalysts arise from zero.

### 9.2 Washout and removal map

The sweep crossed dilution rates 0.01, 0.025, 0.05, 0.1 and 0.2 s⁻¹ with removal fractions 90%, 99%, 99.9% and 99.99%. The pre-event state passed the operational NESS diagnostic at 0.01–0.1 s⁻¹ and failed at 0.2 s⁻¹.

At 0.01 s⁻¹, abundance recovery remained incomplete and the 90% threshold was not crossed during the 150 s post-event window. At 0.025 s⁻¹, recovery was approximately 97.5% but incomplete. At 0.05 s⁻¹, recovery was approximately 99.925%. At 0.1 s⁻¹, recovery was approximately 99.996–100.004%; the post-event NESS diagnostic passed for 90% and 99% removal but not for the two more severe removals.

The 0.2 s⁻¹ cases cannot be treated as resilience from a stationary reference because the pre-event state itself failed the NESS diagnostic. The grid suggests a possible loss-of-operational-steadiness region between 0.1 and 0.2 s⁻¹ for this parameterization and 150 s preconditioning window. It does not establish a critical washout threshold; the grid is sparse and slow transients may affect classification.

### 9.3 Observation-horizon sensitivity

At dilution 0.05 s⁻¹ and 99% removal, the 300 s total run (150 s post-event) restored approximately 99.925% of pre-event X+Y but failed the endpoint-drift NESS criterion (relative drift approximately 0.00265). At 600 s total (450 s post-event), relative endpoint drift fell to approximately 2.07e-8 and the operational NESS criterion passed. The 900 s run (750 s post-event) also passed.

The initial failure was therefore a finite-observation-window issue for this baseline parameterization. This supports relaxation back to the same measured catalytic abundance and operational stationary regime under the tested perturbation. It is not a proof of global asymptotic stability, uniqueness of the attractor or recovery of every possible structural property.

### 9.4 Updated interpretation

Taken together, the open-reactor experiments show that mutual catalysis amplifies stationary X+Y abundance relative to a matched-flow uncatalysed null, but the uncatalysed reactor also satisfies the operational NESS diagnostic. Baseline catalytic abundance can recover after 99% removal while residual catalysts remain. The tested positive trace-feed range has negligible influence on this recovery. Dilution and observation duration materially affect recovery and operational NESS classification.

These findings are conditional on the abstract deterministic well-mixed CSTR, selected kinetic parameters, positive catalyst feed and imposed removal operation. Removal work, pumping, mixing, reservoir regeneration and other engineering costs are not included. The model contains no finite-molecule stochastic extinction, spatial gradients, compartments, chemically validated prebiotic pathways, replication with heredity or evolution.

### 9.5 Next discriminating tests

1. Refine the dilution-rate grid between 0.1 and 0.2 s⁻¹ and lengthen preconditioning to distinguish a true loss of stationarity from slow drift.
2. Vary absolute initial X and Y concentrations, not only removal fractions, to locate extinction and recovery boundaries.
3. Develop a zero-external-seed formulation using finite-state stochastic kinetics or a thermodynamically consistent boundary that avoids the ideal-reservoir zero-activity logarithmic singularity.
4. Perform step-size convergence and broader kinetic-parameter sweeps; test alternative initial conditions and possible multiple stationary states.

No result in this section establishes seed-free emergence, biological self-repair, life, a universal maximum-entropy-production principle or a causal thermodynamic law of intelligence.
