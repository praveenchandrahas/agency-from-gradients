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

## 6. Interpretation boundaries

A successful result can support only a conditional statement about this abstract CSTR: under the selected rates, feed composition and dilution, a mutually catalytic reaction network can maintain some non-zero stationary abundance while consuming and exporting chemical material.

It cannot establish:
- spontaneous formation of the network from unstructured matter;
- a chemically plausible prebiotic pathway;
- a universal principle of maximum entropy production;
- self-repair, replication with heredity or Darwinian evolution;
- the emergence of life, agency or intelligence;
- a planetary-scale entropy budget.

A failed NESS test is also conditional: it may mean the selected feed, washout, rates or simulated horizon do not support stationarity. It does not rule out other networks or environmental regimes.

## 7. Next discriminating experiments

1. Extend simulation horizons and test whether the operational NESS classification is stable to window length and tolerance.
2. Apply perturbations to a reactor that has reached its candidate NESS and measure return times, basin of attraction and washout thresholds.
3. Vary trace X/Y feed over orders of magnitude, including a boundary-limit study, to quantify dependence on continuous seeding.
4. Compare different catalyst assignments under matched stoichiometry, feed, dilution and kinetic scale.
5. Sweep feed chemical potentials and dilution to identify persistence regions, rather than selecting a single favourable parameter point.
6. Add explicit pump, separation and reservoir-regeneration work only when the physical process and its thermodynamic boundary are specified.

The next conceptual transition is not from NESS directly to life. It is from stationary dissipative chemistry to chemical structures that reproduce with heritable variation under sustained driving.
