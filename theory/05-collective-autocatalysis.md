# 05 — A finite-resource mutually catalytic network

**Status:** Second executable chemical model, version 0.1  
**Purpose:** Test whether mutual catalysis can accelerate the conversion of a finite food supply into a chemically organized set of intermediates, while separating formal RAF closure from kinetic and thermodynamic claims.

## 1. The question

The first chemical model showed that a single autocatalytic species can be amplified in a chemostatted toy system. It did not test whether multiple reactions can form a collectively autocatalytic network, and it relied on an imposed initial catalyst plus a reverse source.

This model asks a narrower, discriminating question:

> Given a small RAF-like network and a finite initial chemical disequilibrium, does mutual catalysis accelerate the production of its own catalytic species relative to an otherwise identical uncatalysed kinetic null?

It does not ask whether the network spontaneously assembles from realistic prebiotic chemistry. That would require chemically identified species, plausible pathways and measured thermodynamic parameters.

## 2. Declared food set and reaction set

The food set is:

\[
F = \{A, B\}.
\]

The RAF reaction set is:

\[
R = \{R_1, R_2\}
\]

with reactions:

\[
A \rightleftharpoons X + W_X \quad (R_1;\; catalyst\;Y)
\]

\[
B \rightleftharpoons Y + W_Y \quad (R_2;\; catalyst\;X)
\]

The catalyst assignments are reciprocal:

- R1 is catalysed by Y, which is produced by R2.
- R2 is catalysed by X, which is produced by R1.

The loss reactions are outside the RAF reaction set:

\[
X \rightleftharpoons D_X \quad (R_3), \qquad
Y \rightleftharpoons D_Y \quad (R_4).
\]

The stoichiometric matrix uses species order (A, B, X, Y, W_X, W_Y, D_X, D_Y) and reaction order (R1, R2, R3, R4):

\[
S =
\begin{pmatrix}
-1&0&0&0\\
0&-1&0&0\\
1&0&-1&0\\
0&1&0&-1\\
1&0&0&0\\
0&1&0&0\\
0&0&1&0\\
0&0&0&1
\end{pmatrix}.
\]

This formal network is food-generated and reflexively autocatalytic under the declared catalyst assignments. That is a graph/stoichiometric closure statement, not proof of kinetic viability or spontaneous emergence.

## 3. Finite-resource boundary and conserved moieties

Unlike the previous model, A, B, wastes and degradation products are all dynamic. There are no chemostats and no replenishment. The initial food activities are finite.

The stoichiometry conserves four bookkeeping moieties:

\[
A + X + D_X, \quad A + W_X, \quad
B + Y + D_Y, \quad B + W_Y.
\]

These are formal abstract moieties, not atom-balanced molecular formulas. They make explicit that the model has finite material resources and that products cannot be sustained by an invisible infinite reservoir.

The initial state contains tiny positive X and Y activities to avoid singular ideal chemical potentials. In addition, R1 and R2 have small uncatalysed background rates. Thus the network can be seeded from food in the equations, but this is not molecular self-assembly or a seed-free origin-of-life model.

## 4. Kinetics and detailed balance

Let the activities be a, b, x, y, w_x, w_y, d_x and d_y. The production fluxes are:

\[
v_1 = (k_{p+}a-k_{p-}xw_x)(1+\alpha y),
\]

\[
v_2 = (k_{p+}b-k_{p-}yw_y)(1+\alpha x).
\]

The loss fluxes are:

\[
v_3=k_{l+}x-k_{l-}d_x, \qquad
v_4=k_{l+}y-k_{l-}d_y.
\]

The catalytic multiplier is applied equally to forward and reverse production rates. This preserves the equilibrium constant and detailed balance; catalysis changes the rate of approach to equilibrium, not the equilibrium composition.

The state equation is:

\[
\dot{\mathbf c}=S\mathbf v.
\]

For each reaction, ideal-activity reaction Gibbs energy is:

\[
\Delta_rG=RT\ln(Q_r/K_r).
\]

The reaction entropy-production density is calculated as:

\[
\dot s_{gen}=c^\circ\sum_r v_r(-\Delta_rG_r)/T.
\]

Each reversible reaction's flux-affinity product should be non-negative up to numerical error. The batch is closed to material replenishment, so its initial chemical disequilibrium is a finite free-energy store. Entropy production is transient and must decay as the system approaches equilibrium.

## 5. Baseline and null experiment

The illustrative baseline uses equal initial food activities A = B = 1, tiny positive initial activities for X, Y, wastes and degradation products, production forward rate 0.02 s⁻¹, production equilibrium constant 10, loss forward rate 0.001 s⁻¹, loss equilibrium constant 10⁻⁴, and catalytic strength α = 100. The batch runs for 10 s with a 0.001 s RK4 step.

The null uses exactly the same initial state, reaction constants, material boundary and integration settings, but sets α = 0. This isolates the kinetic contribution of mutual catalysis.

Primary outcomes:

1. X + Y activity at a common finite time.
2. Food conversion fraction.
3. Reaction-wise and integrated entropy production.
4. Conservation errors for the four declared moieties.
5. Difference between catalytic and uncatalysed trajectories.

A finite-time increase in X + Y is evidence of kinetic acceleration in this model only. Because the catalysts multiply forward and reverse rates equally, the eventual equilibrium composition is unchanged. This model does not demonstrate sustained dissipation, a non-equilibrium steady state or a universal preference for maximum entropy production.

## 6. Falsification and interpretation

The implementation should fail its checks if any declared moiety drifts materially, any reaction entropy-production contribution becomes materially negative, or the catalytic case does not outperform the uncatalysed null at the chosen finite time.

A successful result supports only this conditional statement: in this abstract finite-batch network, reciprocal catalysis can accelerate the transient conversion of finite food into catalytic intermediates.

It does not establish that:
- the reactions correspond to chemically plausible early-Earth pathways;
- the network spontaneously assembles from unstructured matter;
- RAF closure guarantees kinetic accessibility;
- the system maintains itself under sustained environmental driving;
- X and Y copy with heritable variation;
- Darwinian evolution or life has emerged.

## 7. What should follow

The next useful tests are not to add more complexity indiscriminately. They are to vary one assumption at a time:

1. Sweep catalytic strength and initial food disequilibrium.
2. Vary background uncatalysed rates to quantify dependence on spontaneous seeding.
3. Apply catalyst-removal perturbations and measure recovery time.
4. Compare networks with the same stoichiometry but different catalyst assignments.
5. Replace the abstract reactions with a chemically specified network only when defensible species, reaction pathways and standard chemical potentials are available.
6. Introduce continuous driving only with an explicit external-work and reservoir-maintenance ledger.

The critical distinction remains: RAF closure, kinetic accessibility, persistence, perturbation recovery, replication and evolution are different properties and must not be collapsed into a single claim.


## 8. Perturbation and recovery experiment

The next experiment extends the same finite-batch model with an explicit intervention. The network first evolves for 5 s. A specified fraction of both X and Y is then physically removed from the reactor, and the remaining material evolves until the original 10 s endpoint.

The intervention is tested at removal fractions 0.9, 0.99 and 0.999. The uncatalysed background production factor is independently varied over 1, 0.1, 0.01 and 0.001. This separates the contribution of residual spontaneous background kinetics from the contribution of the surviving mutually catalytic species.

The rate law is now:

\[
v_1=(k_{p+}a-k_{p-}xw_x)(\epsilon+\alpha y),
\qquad
v_2=(k_{p+}b-k_{p-}yw_y)(\epsilon+\alpha x),
\]

where \(\epsilon\) is the background rate factor and \(\alpha\) is catalytic strength. The same multiplier acts on forward and reverse fluxes, preserving the equilibrium constant. The uncatalysed null is \(\alpha=0\); it retains the chosen background factor.

Recovery metrics are kept distinct:

- **Fraction of removed X+Y recovered:** net increase after the intervention divided by the amount removed.
- **Fraction of pre-perturbation X+Y restored:** final X+Y divided by the pre-perturbation value.
- **Final X+Y relative to unperturbed:** final perturbed X+Y divided by the matched unperturbed run's final X+Y.

These metrics can exceed one or fall below zero in unusual parameter regimes; they are not clipped. Food remaining at intervention and at the endpoint is reported so that apparent recovery is not interpreted without resource context.

The removal operation is a physical outflow of catalyst material. Consequently, the post-intervention conservation ledger is reset to the remaining reactor inventory. The energetic cost of separation/removal is not modelled. This is a material intervention, not a catalyst-inactivation experiment.

A successful recovery result would show only that this seeded abstract network can regenerate some of its catalyst abundance under the remaining finite-resource conditions. It would not establish self-repair in the biological sense, spontaneous emergence, or persistence under continuous environmental forcing.


## 9. Preliminary sweep result and an important confound

The first automated 12-condition sweep is recorded in [results/raf_perturbation_sweep.json](../results/raf_perturbation_sweep.json). At the default background factor \(\epsilon=1\), the unperturbed network has already consumed most of its food by the 5 s intervention time: only about 0.172 of the initial total food activity remains. Following 90%, 99% and 99.9% removal, final X+Y is respectively about 15.9%, 3.33% and 1.57% of the matched unperturbed endpoint.

At \(\epsilon=0.001\), about 1.639 total food activity remains at the same 5 s intervention time. The network is much less developed before intervention, but has substantially more remaining food. The final perturbed X+Y is about 83.1%, 75.0% and 41.6% of the matched unperturbed endpoint for the three removal fractions. The fraction of pre-intervention X+Y restored exceeds one in these cases because the post-intervention trajectory grows beyond its much smaller pre-intervention X+Y value.

This is not evidence that a less-developed network is more robust. The fixed-time comparison changes at least two relevant state variables together: pre-intervention catalyst abundance and remaining food. It therefore does not isolate resilience at matched organizational maturity. The current result is best read as evidence that recovery depends strongly on resource availability and background kinetics in this particular model.

**Required next control:** trigger removal when X+Y reaches a specified common threshold, rather than at a common clock time. Match the pre-intervention catalyst abundance and, where possible, the remaining food inventory across background-rate conditions. If exact matching cannot be achieved, report the mismatch and compare a two-dimensional response surface over pre-intervention X+Y and remaining food. Only then can the model make a cleaner claim about perturbation resistance or recovery.


## 10. Matched-state recovery control

The fixed-time pilot in Section 9 changed background kinetics throughout the entire trajectory. This changed both the catalyst abundance and the amount of food remaining at the intervention time, so it did not isolate post-perturbation recovery. That pilot is retained as a diagnostic of the confound, not as a clean resilience comparison.

The refined factorial experiment now holds the entire pre-perturbation history fixed at \(\epsilon=1\). At 5 s, the same pre-intervention state is used for each condition; the selected fraction of X and Y is removed; only then is \(\epsilon\) changed to 1, 0.1, 0.01 or 0.001 for the remaining five seconds. Thus initial catalyst abundance and remaining food at the moment of intervention are matched across the background-rate conditions.

This isolates the effect of the post-intervention background rate more cleanly. It still does not isolate catalyst-driven recovery from all possible nonlinear kinetic effects, and it remains a short, finite-batch, seeded model. The updated run is recorded separately in [results/raf_matched_recovery_sweep.json](../results/raf_matched_recovery_sweep.json). The primary comparison is the final X+Y abundance relative to the same unperturbed reference, alongside the fraction of pre-intervention X+Y restored and the remaining food inventory.

The more general lesson is methodological: robustness comparisons should match the state at which the perturbation is applied. A common clock time is not sufficient when changing parameters also changes the trajectory leading up to the intervention.


## 11. Matched-state sweep results

The refined sweep is recorded in [results/raf_matched_recovery_sweep.json](../results/raf_matched_recovery_sweep.json). All 12 conditions share the same pre-perturbation state: at 5 s, total remaining food activity is approximately 0.1721. Only the background reaction factor after removal changes.

The central result is that recovery is poor and strongly dependent on how much catalyst survives:

| X and Y removed | Fraction of removed X+Y recovered | Final X+Y vs unperturbed |
|---:|---:|---:|
| 90% | about 6.3% | about 15.7% |
| 99% | about 1.3% | about 2.2% |
| 99.9% | about 0.16% | about 0.26% |

Changing the post-intervention background factor from 1 to 0.001 has only a small effect on these outcomes. In this parameterization, the surviving catalyst abundance matters much more than the small uncatalysed background contribution during the recovery window.

This is a negative result for the stronger resilience claim: the network does not robustly reconstruct its pre-perturbation abundance after severe catalyst removal. It can continue to amplify what remains, but the amplification is not sufficient to restore the original level within the remaining five seconds and finite food budget.

The inference is strictly model-conditional. It does not show that real autocatalytic chemical systems cannot recover; the abstract rate laws, parameter values, network topology, intervention and timescale are all chosen. It does, however, prevent us from casually describing this toy RAF-like network as self-repairing or robust.
