# 04 — Local chemical disequilibrium and the first reaction-network model

**Status:** Technical note, version 0.1  
**Scope:** A well-mixed, chemostatted, abstract autocatalytic reaction network  
**Purpose:** Move from a planetary radiative energy budget to a local chemical free-energy accounting model without assuming life.

## 1. Why a local chemical model is needed

The stellar–planetary ledger describes energy and radiation entropy crossing a planetary boundary. It does not identify the local chemical reactions through which a portion of that energy can become available to matter. Origin-of-life questions require a smaller control volume with explicit chemical species, reaction pathways, chemical potentials, kinetics and material constraints.

The relevant local driving need not be sunlight alone. It may be represented by redox disequilibria, proton gradients, photochemical reactions, thermal gradients or other chemical-potential differences. This first model isolates chemical driving in a well-mixed reactor; spatial and geochemical mechanisms are deliberately deferred.

## 2. What the foundational readings motivate — and what they do not establish

In Chapter 6 of *What Is Life?*, Schrödinger describes organisms as maintaining a relatively stationary organization through exchanges with their environment. In the section “Organization Maintained by Extracting ‘Order’ from the Environment,” he explains the historical “negative entropy” language in terms of entropy with a negative sign. Importantly, his note to that chapter says he would have discussed free energy if writing for physicists, and acknowledges that the simple entropy argument does not explain why particular food molecules, rather than any ordered material, are usable. This is a useful warning: chemical availability and reaction free energy matter, not merely an abstract quantity called order.

The supplied article *A New Physics Theory of Life* summarizes Jeremy England's application of fluctuation relations to strongly driven systems coupled to a heat bath. It describes a possible statistical tendency toward outcomes that absorb and dissipate more work under specified conditions, and identifies self-replication as one possible mechanism. It also describes proposed empirical tests relating dissipation and replication rates. These ideas motivate measuring chemical work and dissipation, but they do not imply that every driven reaction network self-organizes or that entropy production is a universal evolutionary objective.

## 3. Minimal reaction network

The first model contains one dynamic autocatalyst X and three chemostatted reservoir species A, W and D:

\[
A + X \rightleftharpoons 2X + W \qquad (R_1)
\]
\[
X \rightleftharpoons D \qquad (R_2)
\]

The first reaction converts feedstock A into an additional X and waste W, with X catalyzing its own production. The second reaction converts X into a degraded reservoir species D. The reverse reactions are retained so that the kinetic model can be related consistently to reaction free energies.

The symbols are abstract chemical species. No molecular identity, plausible prebiotic pathway, catalyst structure or environmental setting is asserted.

## 4. Kinetics

Let the dimensionless activities of the chemostatted reservoirs be a_A, a_W and a_D, and let x be the activity of X. Activities are defined relative to a 1 mol/L standard state.

The mass-action net rates are:

\[
v_1=k_{1+}a_Ax-k_{1-}x^2a_W,
\qquad
v_2=k_{2+}x-k_{2-}a_D.
\]

The state equation is:

\[
\frac{dx}{dt}=v_1-v_2.
\]

The reverse rate constants are set by positive equilibrium constants:

\[
K_1=\frac{k_{1+}}{k_{1-}},\qquad K_2=\frac{k_{2+}}{k_{2-}}.
\]

This parameterization enforces detailed-balance consistency for the idealized reactions. It is not a claim that the abstract species correspond to real compounds.

## 5. Chemical potentials and entropy production

For ideal activities, the reaction quotients are:

\[
Q_1=\frac{x a_W}{a_A},\qquad Q_2=\frac{a_D}{x}.
\]

The reaction Gibbs energies are:

\[
\Delta_rG_1=RT\ln(Q_1/K_1),\qquad
\Delta_rG_2=RT\ln(Q_2/K_2).
\]

The reaction affinity is -ΔrG. For a reversible mass-action reaction parameterized consistently with its equilibrium constant, the net flux and affinity have the same sign. The model therefore calculates the internal reaction entropy-production density as:

\[
\dot s_{gen}=c^\circ\sum_{r=1}^{2}\frac{v_r(-\Delta_rG_r)}{T},
\]

where c° is the standard concentration in mol/L. The result has units J L⁻¹ K⁻¹ s⁻¹. The corresponding free-energy dissipation rate is T times sdot_gen.

This is a reaction-network balance under fixed reservoir chemical potentials. It is not the total entropy production of the reservoirs, chemostat apparatus, reactor walls or surrounding environment. Those components would have to be included for a larger closed accounting boundary.

## 6. Fixed point and low-concentration criterion

The one-state deterministic model has a positive fixed point given by the positive root of:

\[
k_{1-}a_Wx^2-(k_{1+}a_A-k_{2+})x-k_{2-}a_D=0.
\]

At low x, and neglecting the small reverse source from D, the linear per-capita growth coefficient is:

\[
\lambda=k_{1+}a_A-k_{2+}.
\]

The corresponding linear invasion threshold is:

\[
a_{A,crit}=k_{2+}/k_{1+}.
\]

Because the model retains a nonzero reverse reaction from the D reservoir, the zero state is not absorbing and the exact system has a small background abundance even below this threshold. The threshold is therefore a linearized criterion, not a sharp phase transition in this finite-reservoir-activity model.

## 7. First computational experiment

The baseline configuration uses:

- T = 298.15 K
- a_A = 1, a_W = 1, a_D = 10⁻⁸
- K1 = 10, K2 = 10⁻⁴
- k1+ = 0.1 s⁻¹, k2+ = 0.01 s⁻¹
- initial x = 10⁻⁴
- duration 5,000 s, RK4 step 0.1 s

A low-feed reference uses a_A = 10⁻⁶. A feed sweep changes a_A while holding other parameters fixed. Each simulation is compared with its analytic fixed point, and reaction entropy-production contributions are checked for non-negativity.

For the rounded Earth–Sun-like reference inputs, the model gives a baseline fixed point of approximately x = 9.000011, compared with a low-feed control fixed point of approximately 9.9991 × 10⁻⁵. This is a model-specific enrichment of about 9.0 × 10⁴. The result is not an empirical prediction: it follows from the illustrative rate and equilibrium parameters chosen for this toy network.

## 8. What this model can and cannot show

It can show, within its equations, that a driven autocatalytic reaction can maintain a non-equilibrium catalyst abundance above a low-feed reference, that the abundance depends on feed activity and kinetic loss, and that the specified reversible reactions produce non-negative chemical entropy production.

It cannot show that the network spontaneously assembles from unstructured matter, that the reaction is chemically plausible in an early-Earth environment, that the catalyst stores heritable information, that replication with variation occurs, or that natural selection operates. It also cannot establish that the network evolved because it maximizes dissipation: the model does not include a selection rule over alternative networks or structures.

## 9. Next discriminating experiments

1. Replace abstract A, X, W and D with a chemically specified reaction network and defensible standard chemical potentials.
2. Introduce finite feed reservoirs rather than chemostats, then account for the external work needed to replenish them.
3. Add competing catalytic pathways and compare persistence, yield, maintenance costs and entropy production independently.
4. Add spatial transport only when a concrete local environment and mechanism justify it.
5. Test whether catalytic organization appears from non-organized initial conditions rather than being inserted as an initial catalyst.
6. Only after a physical mechanism exists should the model investigate compartments, self-maintenance, copying, heredity and evolution.

## References

- Schrödinger, E. (1944). *What Is Life? The Physical Aspect of the Living Cell*. Chapter 6.
- *A New Physics Theory of Life*. Supplied article discussing Jeremy England's dissipation-driven adaptation proposal.
- Jarzynski, C. (1997). “Nonequilibrium Equality for Free Energy Differences.” *Physical Review Letters*, 78, 2690–2693. https://doi.org/10.1103/PhysRevLett.78.2690
- Crooks, G. E. (1999). “Entropy production fluctuation theorem and the nonequilibrium work relation for free energy differences.” *Physical Review E*, 60, 2721–2726. https://doi.org/10.1103/PhysRevE.60.2721
