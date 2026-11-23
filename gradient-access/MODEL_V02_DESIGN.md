# Model v0.2 design requirements — explicit work coupling

**Purpose:** replace the v0.1 bookkeeping assumption with a minimal reaction network in which the free-energy gradient that drives catalysis also produces a finite work currency that replication must consume.

This is a design specification, not an implemented or validated model. No v0.2 result should be reported until the equations, numerical implementation and tests agree.

## 1. State variables and chemical species

Use two conserved binary pools:

- Fuel pool: fuel (F) and waste (W), with (f+w=1).
- Work pool: high-energy currency (T) and low-energy currency (D), with (t+d=1).

The reactor also contains catalyst genotypes (C_i), plus a declared monomer/building-block reservoir (M). The first implementation may keep (M) chemostatted, but its chemical potential and material exchange must be explicit.

All activities must remain strictly inside their physical domains during continuous integration. A boundary value of exactly zero must be handled analytically or avoided by a declared positive feed floor; it must not be hidden by clipping.

## 2. Catalytic energy-conversion reaction

Use the coupled reaction

[
F + D ightleftharpoons W + T.
]

Let the standard chemical-potential drop be (Deltamu_0), in (k_BT) units. Its dimensionless affinity is

[
mathcal A_1 =
Deltamu_0 + ln!left(rac{f,d}{w,t}ight).
]

For each genotype (i), define a positive catalytic rate multiplier (c_i). A local-detailed-balance kinetic law can be written

[
v_i^+ = k_i c_i f d,
qquad
v_i^- = k_i c_i e^{-Deltamu_0} w t,
qquad
J_i=v_i^+-v_i^-.
]

Thus (v_i^+/v_i^-=exp(mathcal A_1)), and the reaction entropy-production rate is

[
sigma_1 = sum_i J_imathcal A_1 ge 0.
]

Catalysts multiply both directions equally and therefore change kinetics, not the equilibrium constant. At equilibrium every net (J_i) is zero and (sigma_1=0).

The coupled reaction transfers chemical free energy into the work pool. Its stoichiometric updates are (F:-J), (W:+J), (D:-J), (T:+J). The fuel and work-pool balances must be integrated from these same extents; do not compute them independently.

## 3. Replication and mutation

Replication must consume the work currency and building blocks. A minimal explicit reaction is

[
C_i + mM + nT ightleftharpoons 2C_i + mP + nD,
]

where (P) is the declared polymerization waste and (m,n) are fixed stoichiometric coefficients. Its affinity must be derived from the chemical potentials of (C_i,M,P,T,D), including the population-dependent catalyst activity. Birth and reverse/degradation propensities must obey local detailed balance.

A birth event consumes exactly (n) work-currency units and (m) monomer units; it creates one offspring. Mutation changes the offspring genotype according to a declared transition kernel. If mutation has an extra energetic/material cost (for example, error correction), specify a separate reaction or cost term rather than charging an expected cost while recording a different realized cost.

The initial implementation may use a stochastic reaction-event algorithm for birth, degradation and mutation. If a deterministic approximation is retained, it must be derived from the same propensities and tested against a stochastic reference in the regime where both are valid.

## 4. Population selection

Genotypes must differ in the catalytic flux they generate through the energy-conversion reaction. Reproductive success must arise from the resulting allocation of work currency, not from a directly assigned fitness score. If the work pool is shared, specify the allocation rule and demonstrate that it conserves the pool and does not create energy.

Selection is not entropy maximization. Entropy production is a diagnostic, never a direct reproductive reward.

## 5. Open-reactor exchange

The first version may chemostat only the (F/W) pool. For feed activities (f_0,w_0), with (f_0+w_0=1), and flow rate (q), the ideal binary-mixture exchange entropy-production term is

[
sigma_{mathrm{flow}} =
q(f_0-f)ln!left(rac{f_0}{f}ight)
+q(w_0-w)ln!left(rac{w_0}{w}ight).
]

Both species must be included. This expression is non-negative for positive activities. If (T/D), monomers or polymerization waste are also exchanged, their fluxes and chemical-potential terms must be added.

## 6. Complete ledger requirements

Every step/event must close:

- (F/W) material balance, including reaction and feed/outflow.
- (T/D) work-currency balance, including energy conversion and replication.
- Monomer/polymer material balance.
- Catalyst count balance, including birth and degradation.
- Free-energy balance: chemical free-energy change equals declared work transfer plus dissipated free energy, with no untracked source.
- Entropy production: sum of reaction and exchange contributions over the declared boundary, including replication and all reservoir interfaces.

No negative work inventory, hidden energy subsidy, silent clipping or unrecorded birth is allowed. Initial catalyst construction must be treated as an explicit initial investment, with its material and free-energy cost included in comparisons.

## 7. Numerical and analytical gates

Before a parameter sweep:

1. Verify each reaction's forward/reverse ratio equals (exp(mathcal A_r)).
2. Verify zero net flux and zero entropy production at each reaction's equilibrium.
3. Verify (J_rmathcal A_rge0) for all valid states.
4. Verify stoichiometric conservation for every reaction and flow stream.
5. Verify the complete free-energy/work ledger closes to numerical tolerance.
6. Verify all concentrations and work inventories remain non-negative without clipping.
7. Compare at least two integration methods and demonstrate timestep convergence.
8. Compare deterministic population approximations with stochastic event simulations.
9. Verify that multiplying forward and reverse catalytic rates equally does not alter equilibrium.
10. Verify that no entropy-production variable enters the reproduction propensity.

## 8. Experimental fairness gates

The following controls must not be conflated:

- **Fixed-size:** abundance held constant by design.
- **Initial-abundance-matched:** same starting catalyst count only.
- **Trajectory-matched:** same abundance trajectory, requiring a declared intervention.
- **Total-investment-matched:** same cumulative material and work expenditure over the horizon.
- **Information-matched:** same access to target information and candidate-evaluation feedback.

For the central hypothesis, total-investment matching is essential. Compare L against (a) fixed random libraries, (b) faithful inheritance with the same initial library, (c) faithful inheritance with a larger initial standing library, and (d) non-replicating adaptive search. Report both throughput per total investment and cumulative throughput under a common finite investment budget. A control that is given a larger initial library must be charged for constructing it.

## 9. Statistical protocol

Before confirmatory execution:

- Freeze primary outcomes, contrasts, parameter ranges, exclusion rules and analysis code.
- Use independent paired seeds for environmental histories and separate random streams for genotype/population stochasticity.
- Select seed count using a power or precision analysis based on pilot variance; do not assume ten seeds are sufficient.
- Report effect sizes and uncertainty intervals, not only significance or interval overlap.
- Correct or hierarchically structure inference across multiple barriers, landscapes and drift rates.
- Reserve independent seeds as a held-out confirmatory set.
- Publish all replicates, trajectories, manifests, and failed/null runs.

## 10. Scope boundary

Even a successful v0.2 model would establish only a mechanism within a declared abstract reaction network. It would not establish abiogenesis, the inevitability of life, or a universal law that evolution must occur. Chemical realism and empirical tests would remain separate research stages.
