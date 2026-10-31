# Pre-registration S11: what is the best way to increase the entropy of a lifeless universe?

Written and committed BEFORE any confirmatory run. Pilots use seeds >= 1000 and are not evidence. Confirmatory seeds: 0-19.

## Reading taken (unattended run)
The task was run unattended, so no questions were asked. Readings taken:
1. "The agent" is a controller with no body in the biological sense: it launches self-replicating probes at 0.5 c (ablation: c, 0.1 c) from the Milky Way at "now" and acts only on matter its probe cone has reached. Light speed limits everything.
2. The model is deterministic given its parameters. A **seed** therefore indexes a *draw of the uncertain physical parameters* (SMBH entropy calibration within the Egan-Lineweaver range, star-formation timescale, radiative efficiency, merger energy loss, bound-domain mass). Policies are trained on seeds >= 1000 and evaluated on held-out seeds 0-19. Confidence intervals are bootstrap over the 20 seeds, so they express **parameter uncertainty, not noise**.
3. Experiment scripts live in `src/agency_gradients/experiments/` (the repo's actual layout), not a top-level `experiments/`.

## Question
Given a universe with stars, galaxies, supernovae, compact remnants, supermassive black holes (SMBHs), dark matter and ΛCDM expansion, but no life, which actions by an entropy-maximising agent yield the largest gain in total entropy over a do-nothing universe, at fixed horizons, once reach limits and action costs are enforced? And does an open-ended policy search find anything a small set of hand-designed levers misses?

## Model (stylised ledger, not N-body; details in docs/DESIGN.md)
- Flat ΛCDM (H0 67.4, Ωm 0.315), a(t) analytic; "now" is a=1. Reach: probes at v/c travel a comoving distance; the reached volume fraction is (chi/46.4 Gly)^3 (Ord 2021: affectable region 16.5 Gly comoving vs observable 46.4 Gly, about 4.5% of volume at v=c).
- Two compartments, reached (R) and unreached (U), with baseline physics in both and levers acting in R only.
- Stocks (Msun): IGM gas, cold gas, five stellar classes (exponential lifetimes, luminosities from fuel fractions), white dwarfs, neutron stars, collector mass, and a black hole population in 52 factor-2 mass bins carrying (number, mass, sum of M^2), so entropy is exact for the carried moments.
- Black hole entropy S/kB = 4 pi G M^2/(hbar c) = 1.05e77 (M/Msun)^2. Mergers lose a fraction eps_gw of mass to gravitational waves (area theorem holds). Accretion has radiative efficiency eta (rest mass dm adds (1-eta) dm to the hole). Hawking evaporation (far horizon only) emits entropy 1.4847 times the black hole entropy lost (Page).
- Photon entropy: blackbody energy E at T carries (4/3) E/T. Reprocessing starlight (T_eff) to T_c adds (4/3) E (1/T_c - 1/T_eff). Collector radiator temperature is max(environment floor, (P/(sigma A))^(1/4)), where the area A is tied to collector mass. The floor is max(T_cmb(a), de Sitter temperature 2.2e-30 K).
- SMBH mass function calibrated so the baseline SMBH entropy is about 3.1e104 kB (Egan and Lineweaver 2010). Stellar BH entropy is not tuned and is checked against their 5.9e97.
- Ledgers: a mass-energy ledger and a baryon-number ledger must close to relative 1e-9 every step (tests fail otherwise). A hard check flags any state whose BH entropy exceeds the cosmic-event-horizon entropy 2.6e122 kB.
- Bound domains: matter in different gravitationally bound domains (default baryon mass 1.5e14 Msun, a cluster) cannot be merged with each other because Λ separates them. Merging within a domain can proceed until one hole per domain. This is the main reach-type assumption beyond the cone, and is ablated.
- Dark matter and relic neutrinos are inert (not fed to holes, no entropy change). Hawking radiation, CMB entropy and neutrinos are constant baselines or far-horizon only.

## Baseline and objective
Baseline: the same world with all levers off. Primary metric: **gain = S_total(agent) - S_total(baseline)** at the horizon, in kB; also report the absolute value and the breakdown by component (BH, photon, matter, Hawking radiation, CMB). Search objective: sign(g) log10(1 + |g|), because gains span many decades.

## Horizons
100 Gyr, 1e12 yr, 1e14 yr. Optional far horizon 1e113 yr (past evaporation of 1e15 Msun holes), clearly flagged speculative: it multiplies hole entropy by 1.48 and tests only whether the ranking changes.

## Levers (shares of effort in a simplex; "do nothing" takes the remainder)
(a) accelerate gas to star conversion (rate multiplier up to 10 in R). (b) funnel cold gas into SMBHs (accretion weight proportional to M^2, Eddington-capped). (c) trigger black hole mergers (within bound domains, pair delay). (d) collapse white dwarfs and neutron stars into black holes. (e) deploy starlight collectors that harvest work and radiate at lower T_c. (f) do nothing.
Every lever costs energy drawn from the agent's work reservoir W, fed only by collectors (plus a tiny seed); waste heat is counted as entropy at T_c. Actions are throttled when W is short. Costs in units of rest-mass energy of mass processed: a 1e-6, b 1e-4, c v_d^2 = 1e-4 (v_d=0.01 c), d 1e-3, e 1e-6; these are assumptions, ablated by 0.5x, 2x, and also 1e3x to find where they bind.

## Search
Phase A: all pure and pairwise-mixed strategies, then evolution strategy (antithetic, centred-rank, as S8) on a piecewise-in-log-time allocation (6 segments x 6 logits). Phase B: a 10-input, 16-hidden tanh network from log-time and current stocks, same ES, population 24 antithetic pairs, 60 generations, 5 independent ES runs per horizon. Training seeds 1000-1003. Comparators: best Phase A, random policies (20), do-nothing.

## Primary hypotheses (95% bootstrap CIs over seeds 0-19; supported means the stated bound excludes 0)
- **H11a** At every horizon the best Phase A strategy has gain > 0 and its gain is dominated (> 90% of gain) by the black hole component. Judged by the CI of gain and the mean BH share.
- **H11b** Horizon dependence: the best gain at 1e14 yr exceeds the best gain at 100 Gyr (difference CI lower bound > 0), expected because mergers and feeding need time and reach grows.
- **H11c** Reach: removing the reach limit (all matter immediately reachable) raises the best gain (CI lower bound > 0); expected large.
- **H11d** Open search: Phase B best policy (mean over ES runs) minus best Phase A, gain in log10 units, lower bound > 0. Prior: **not expected to hold**; I expect Phase B to match or fall short of Phase A.
- **H11e** Black hole lever removal: with levers b, c, d disabled, the best strategy's log10 gain is lower by more than 5 decades than with them (CI). Expected by construction.
- **H11f** Photon route: removing the radiator-area limit makes collectors competitive with the black hole route (gain from lever e alone exceeds the best BH-lever gain at 1e14 yr). Prior: it does at long horizons; flagged unphysical.
- **H11g** Coefficient scaling: black hole entropy coefficient x0.1 and x10 change best log10 gain by about -1 and +1 (within 0.5) when BH-dominated; deviation shows nonlinear effects. Descriptive, no direction beyond that.
- **H11h** Costs: halving or doubling costs at the default calibration changes best log10 gain by < 0.5 (CI includes 0). Prior: costs are cheap against stellar energy so costs do not bind; the 1e3x arm should show where they do.

## Sensitivity plan
Re-optimise (Phase A search) under each ablation and report best strategy and gain at each horizon: no BH levers; BH coefficient x0.1, x10; no reach limit (F=1); cost x0.5, x2, x1000; probe speed c and 0.1 c; domain mass 1e12 and 1e16 and none (with the horizon cap check); radiator-area limit off; radiative efficiency 0.05 and 0.3.

## Exploit-audit plan
(1) Ledger tests inside every rollout (reject and penalise any violation). (2) Inspect best policies: action shares over time. (3) For each best policy, re-evaluate with each cost x10 and x100, with energy from accretion not capturable, with no radiator-area relaxation, with domain floor on and off, and with the BH entropy cap active. A gain that disappears under a single tightening is flagged as dependent on that assumption. (4) Any exploit found is fixed in the model, re-run, and logged below.

## Interpretation rules
- A result that matches "make, feed and merge black holes" is a consistency check on the formulas, not a discovery.
- Gains are reported as parameter-uncertainty intervals, not statistical significance of noise.
- Phase B not beating Phase A is reported as a null.
- Connection to the thesis: report whether the result supports or complicates "the entropy-maximal structure is a black hole, not an agent". The model excludes life by assumption and so cannot test whether life increases entropy.

## Pilot (seeds >= 1000; not evidence)
To be filled after pilot.

## Outcome
To be filled after the confirmatory run.

## Deviation log
(empty at registration)
