# Local chemical disequilibrium: minimal autocatalytic network (v0.1)

## Purpose

This is the first executable local-chemistry model in Thermodynamic Emergence. It asks whether an externally maintained chemical disequilibrium can support a non-equilibrium steady state with a strongly enriched autocatalyst, and how that state changes with feed availability.

It is deliberately an abstract reaction-network experiment. It is **not** a proposed prebiotic pathway, a model of a hydrothermal vent, or a demonstration of abiogenesis.

## Reaction network

The well-mixed control volume contains one dynamic species, the autocatalyst **X**, and three chemostatted reservoir species, **A**, **W** and **D**:

\[
A + X \rightleftharpoons 2X + W \qquad (R_1)
\]
\[
X \rightleftharpoons D \qquad (R_2)
\]

R1 is autocatalytic: one X participates on both sides and the net reaction converts feedstock A into another X plus waste W. R2 is a loss/conversion pathway that removes X into reservoir D. The reverse reactions are retained; this avoids silently treating the network as an irreversible kinetic machine.

The abstract species can be assigned a conserved moiety bookkeeping in which A contains the X-forming unit plus the waste unit, while D contains the X-forming unit. This is only a stoichiometric abstraction; no molecular structures are specified.

## Kinetics and thermodynamic consistency

Activities are dimensionless relative to a 1 mol/L standard state. The reservoirs hold a_A, a_W and a_D fixed. x is the dynamic activity of X.

The net rates are:

\[
v_1 = k_{1+} a_A x - k_{1-}x^2 a_W,\qquad
v_2 = k_{2+}x-k_{2-}a_D.
\]

The reverse rates obey detailed-balance parameterization:

\[
K_1=k_{1+}/k_{1-},\qquad K_2=k_{2+}/k_{2-}.
\]

For ideal activities, reaction Gibbs energies are:

\[
\Delta_rG_1=RT\ln\left(\frac{x a_W/a_A}{K_1}\right),\qquad
\Delta_rG_2=RT\ln\left(\frac{a_D/x}{K_2}\right).
\]

The state equation is:

\[
\frac{dx}{dt}=v_1-v_2.
\]

For the specified ideal reaction network, the internal chemical entropy-production density is calculated as:

\[
\dot s_{gen}=c^\circ\frac{v_1(-\Delta_rG_1)+v_2(-\Delta_rG_2)}{T},
\]

where c° is the standard concentration in mol/L. Each reversible mass-action flux has the same sign as its reaction affinity -ΔrG, so each reaction contribution should be non-negative apart from floating-point error. The reported units are J L⁻¹ K⁻¹ s⁻¹.

The corresponding local free-energy dissipation rate is T times sdot_gen, in J L⁻¹ s⁻¹. It is the dissipation associated with the declared reaction boundary and chemostatted chemical potentials, not the total energy input or entropy production of the apparatus and environment.

The model's positive fixed point can also be calculated analytically from the quadratic state equation. The numerical integration is compared with this fixed point as a convergence check.

## Default illustrative experiment

The baseline uses T = 298.15 K, a_A = 1, a_W = 1, a_D = 1e-8, K1 = 10, K2 = 1e-4, k1+ = 0.1 s⁻¹, and k2+ = 0.01 s⁻¹. The initial catalyst activity is 1e-4; integration runs for 5,000 s with a 0.1 s RK4 step.

The low-feed reference control uses a_A = 1e-6. It is not a zero-feed limit because ideal chemical potentials become singular at zero activity and the reverse reactions are retained.

The feed sweep is an independent set of simulations with the other parameters fixed. The low-concentration linear growth coefficient is k1+ a_A - k2+; its sign changes at a_A = k2+/k1+ = 0.1 when the small reverse-source term is neglected. Because the reverse reaction from D is nonzero, the exact model has a small background concentration rather than a mathematically absorbing zero state. Treat 0.1 as a linear invasion threshold, not a sharp phase transition.

## Run

From the repository root:

\`\`\`bash
python -m pip install -e .
python -m thermodynamic_emergence.chemistry_cli
python -m thermodynamic_emergence.chemistry_cli --json
python -m thermodynamic_emergence.chemistry_cli --sweep
python -m unittest discover -s tests -v
\`\`\`

## Interpretation limits

- A, W and D are abstract species; no specific prebiotic chemistry is represented.
- The model is well-mixed and has no spatial gradients, diffusion, compartments or mineral surfaces.
- Chemostats hold reservoir activities fixed; their pumps and external apparatus are outside the model boundary.
- The model has autocatalysis but no heredity, mutation, lineage or Darwinian evolution.
- The reaction standard free energies are implied by illustrative equilibrium constants, not measured chemical data.
- A high entropy-production rate is an output of this chosen network and parameterization. The model does not optimize entropy production and does not show that entropy production caused the network to arise.
- The model demonstrates a conditional kinetic possibility in an abstract driven network. It does not establish that such a network forms spontaneously from prebiotic chemistry.

## Relation to the foundational readings

Schrödinger's *What Is Life?*, Chapter 6, frames the organism's maintenance as requiring exchange with its environment and explicitly notes that free energy is the more technically appropriate concept in this discussion. He also warns that a simple entropy argument alone does not explain why particular food molecules, rather than any ordered material, are usable. This model follows that caution by writing chemical potentials and reaction free energies explicitly.

The supplied article *A New Physics Theory of Life* summarizes England's proposal that strongly driven systems coupled to a heat bath may, under specified conditions, evolve toward states that absorb and dissipate more work. It discusses replication as one possible route and proposes testing correlations between dissipation and replication. The present model is a minimal mechanistic test-bed for chemical driving and autocatalysis; it does not test England's broader statistical-mechanical result or establish a universal maximum-dissipation principle.

## References

- Schrödinger, E. (1944). *What Is Life? The Physical Aspect of the Living Cell*. Chapter 6, “Order, Disorder and Entropy,” especially “Organization Maintained by Extracting ‘Order’ from the Environment” and the note on free energy.
- *A New Physics Theory of Life*. Supplied article discussing Jeremy England's dissipation-driven adaptation proposal, fluctuation relations, self-replication and suggested experimental tests.
- Jarzynski, C. (1997). “Nonequilibrium Equality for Free Energy Differences.” *Physical Review Letters*, 78, 2690–2693. https://doi.org/10.1103/PhysRevLett.78.2690
- Crooks, G. E. (1999). “Entropy production fluctuation theorem and the nonequilibrium work relation for free energy differences.” *Physical Review E*, 60, 2721–2726. https://doi.org/10.1103/PhysRevE.60.2721


## Where this sits in the origin-of-life literature

This first model is a single autocatalytic motif, not a collectively autocatalytic set. RAF theory formalizes networks in which reactions are catalyzed by species in the food set or produced by the network, and whose reactants can be generated from the food set. Such closure is a stronger organizational property than one species catalyzing its own production, but it still does not by itself establish kinetic viability, spontaneous emergence or Darwinian evolution.

Ameta et al. (2021) review experimental autocatalytic systems and emphasize the remaining gaps between chemical self-reproduction and heritable Darwinian evolution. The next model should therefore investigate a small RAF-like network, with graph closure, kinetic accessibility, finite resources and perturbation tests treated separately.

References:
- Hordijk, W., & Steel, M. (2018). “Autocatalytic Networks at the Basis of Life’s Origin and Organization.” *Life*, 8(4), 62. https://doi.org/10.3390/life8040062
- Ameta, S., Matsubara, Y. J., Chakraborty, N., Krishna, S., & Thutupalli, S. (2021). “Self-Reproduction and Darwinian Evolution in Autocatalytic Chemical Reaction Systems.” *Life*, 11(4), 308. https://doi.org/10.3390/life11040308
- Rao, R., & Esposito, M. (2016). “Nonequilibrium Thermodynamics of Chemical Reaction Networks: Wisdom from Stochastic Thermodynamics.” *Physical Review X*, 6, 041064. https://doi.org/10.1103/PhysRevX.6.041064
