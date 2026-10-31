# Design

## What is being tested

The design hypothesis: *agency arises when a population of self-maintaining structures is selected only by persistence and reproduction, in an environment with a ladder of energy gradients, finite resources, heredity with variation, a real cost of failure, and succession.* The suite does not assume entropy production is an objective. It measures it.

Agency is operationalised narrowly as **viability restoration**: an agent that is displaced and depleted gets itself back to a viable energy state. Prediction is not yet measured.

## World

- Torus, 32 x 32. Population cap 200, initial 60. Asynchronous: every step, every living agent acts; births and deaths happen continuously.
- **Observation** (per agent): for each of the four neighbouring cells and its own cell, seven channels: commons level, Tier 1 locked / open, Tier 2 locked / open, and two smooth "scent" fields pointing toward each reservoir tier. Plus own energy and a bias.
- **Actions:** move N / E / S / W, stay, invest. Eating is automatic and shared evenly among agents on a cell.
- **Tier 0, commons:** regrows at `commons_regrow x field` per cell per step. `field` is a smooth patchy multiplier with mean 1. Energy above the per-cell cap leaks (passive dissipation).
- **Tier 1:** 12 sites, stock 150, regrow 0.3 / step. **Tier 2:** 4 sites, stock 800, regrow 1.6 / step.
- **Openness** of a reservoir is `min(progress / lock, 1)`. Each invest action adds 1 to progress; progress decays every step (2% for Tier 1, 15% for Tier 2). Harvest rate scales with openness. Tier 1 can be held open by one agent investing occasionally. Tier 2 needs about four agents investing continuously to be fully open, though partial openness pays partially.
- **Metabolism** 0.10 / step, move cost 0.03, invest cost 0.15. Reproduction needs energy >= 12; the parent pays 6 and the child receives 80% of that.

## Ablation factors (S2)

| Factor | On | Off |
|---|---|---|
| `scarcity` | commons regrow 0.008 | 0.08 (abundant) |
| `heredity` | child = parent + sparse mutation | child gets a fresh random genome |
| `mortality` | death at zero energy, plus 0.003 / step extrinsic hazard | zero-energy agents are bailed out to energy 1; no hazard |
| `succession` | Tier 2 sites form only where a Tier 1 site is drained (same total number) | Tier 2 sites exist from the start |

The gradient ladder (Tiers 1 and 2) is **not** a factor; see README limitation 5.

## Selection criteria (S1)

| Mode | Who reproduces |
|---|---|
| `persistence` | agents whose energy reaches the reproduction threshold |
| `entropy` | agents that have burned enough energy since their last birth (entropy used as a reward; the control the thesis argues against) |
| `task` | agents that have eaten enough commons energy (a conventional task reward) |
| `drift` | births restore the population toward its initial size; parents are chosen uniformly at random among the living. Not fully neutral: starvation still filters genomes, so only fecundity selection is removed |

## Metrics

| Metric | Definition |
|---|---|
| `capture_fraction` | energy intercepted by agents / (intercepted + passively leaked), last quarter of the run |
| `entropy_rate` | mean of leaked energy + kappa x energy dissipated by agents, per step, last quarter |
| `capture_ratio` | `entropy_rate` / the same environment's rate with no agents |
| `share_tier1/2` | share of intercepted energy from each reservoir tier |
| `t2_reached` | 1 if any Tier 2 site ever reached full openness |
| `pop_mean_late`, `extinct` | population health |
| `delta_recovered` (S4) | evolved minus random-genome agents that regain half the reproduction threshold within 150 steps after displacement and depletion |

### The accounting assumption, stated plainly

Agent dissipation counts `kappa` (default 3) entropy units per unit of energy; passive leakage counts 1. This encodes "a structure that processes energy at a lower temperature than the source produces more entropy per unit". It is an **assumption**, not a result. Consequently `capture_ratio` is mostly `1 + (kappa - 1) x capture_fraction`, plus corrections. S3 runs `kappa = 1` as a sanity check, where it must collapse toward 1. The empirical content of the suite is in `capture_fraction`, the tier shares, `t2_reached` and the S4 contrast.

`capture_fraction` is not comparable across ladder and no-ladder configurations: reservoirs leak passively whether or not anyone is there, so adding a ladder lowers the fraction even if agents capture more in absolute terms.

### Energy ledger

Every step is checked against: change in total energy = injected - leaked - heat - reproduction loss - energy removed at death + bailouts. The tests assert the residual stays below 1e-6, including through succession conversions.

## Policies

- `equivariant` (default, 27 parameters): one weight vector over channels applied to each direction's cues for movement, plus separate weights for stay and invest from the agent's own cell. This is chemotaxis-shaped and a strong inductive prior.
- `mlp` (about 450 parameters, one hidden layer): no prior. In pilots it did not improve on drift within 30,000 steps.

## Design history forced by pilots

All pilots used seeds >= 1000. None of these runs is confirmatory, but the changes were made *because* early versions showed selection doing nothing, so the final design is tuned toward a world where selection can act. That is a bias, and it is the reason the preregistration fixes the design before any seed 0-29 run.

1. **v0:** uniform commons, MLP policy, latched unlocks. Persistence selection equalled neutral drift on every metric; Tier 2 was never reached.
2. Added the **scent cue**; a policy sensing only four neighbours had almost nothing to evolve from.
3. Replaced the **latched unlock** with a maintained level. Under the latch, one lucky agent opened a site for everyone forever and unlock counts saturated whatever the policy.
4. Added an **extrinsic death hazard** and **sparse mutation** to get more generations per run (about 35 generations in 30,000 steps was far too few).
5. Made **openness graded**. A site that paid nothing until fully open was a needle in a haystack.
6. Replaced the original **drift control**, which went extinct and so was not a usable null, with a population-restoring random-parents model (later found to retain viability selection, see Selection criteria).
7. Made the commons **patchy**, so directed foraging pays immediately.
8. Added a **hand-coded positive control** to measure headroom. Its first version went extinct because of two bugs in my code: it assumed the wrong observation order, and drained reservoirs looked "locked". Both fixed.
9. Added the **equivariant policy** as the default after the MLP failed to evolve useful behaviour.
10. Corrected the **S4 null**. A smoke run showed `delta_recovered > 0` even with no heredity, from survivorship bias; the interpretable quantity is the full-vs-no-heredity contrast.

11. **S6 sharing rule** (`deposit_share="contributor"`): reservoir harvest on a cell split by each agent's decaying investment trace (decay 0.98, floor 0.02) instead of evenly. Default `"equal"` reproduces S1-S5 bit for bit (checked on seed 0 against the confirmatory CSV). Parameters fixed before the S6 run.
12. **World v2** (`world_v2=True`, `world_v2.py`, `policies_v2.py`). Added after the main run showed that evolved populations did not use big deposits and the objection that a few dozen genes is too few.

## World v2

| Addition | Detail |
|---|---|
| Observation (54) | The 37 v1 inputs unchanged (so the v1 forager works), then wall, danger and signal channels over the five visible cells, and season sin/cos |
| Actions (7) | v1 actions plus **signal** (costs `signal_cost` energy, dissipated as heat) |
| Policies | `recurrent` (hidden 24, tanh, ~2,070 genes), `mlp2` (~1,400), `equivariant2` (29, the small prior-laden policy on the same world) |
| Heritable traits | Two genes after the policy weights: body size in [0.5, 1.5] (scales metabolism, eating share and bite) and reproduction-threshold multiplier in [0.5, 1.5] |
| Seasons | Commons regrowth multiplied by `1 + season_amp sin(2 pi t / season_period)`; injection counted from the same field, so the ledger closes |
| Terrain | `n_walls` line segments of `wall_len` cells, never on reservoir sites; a move into a wall is blocked (cost still paid); gaps leave the torus connected |
| Danger | `n_danger` discs; extra death probability `danger_hazard` per step (only with mortality on) |
| Pheromone | Field decays (`signal_decay`) and diffuses (`signal_diffuse`); information only, not in the ledger |
| Mutation | Per-gene small mutation (`mut_rate`, `mut_sigma`) plus rare large mutation (`mut_big_p`, `mut_big_sigma`). `v2_config()` uses 0.02 / 0.10 / 0.0005 / 1.0 |
| Scale | `v2_config(scale=k)` multiplies the torus side by k and every count by k squared, keeping densities |
| Metrics added | `signal_rate`, `size_mean`, `repro_mult_mean`, `gen_mean` (mean generations of descent), `n_genes`, early-vs-late entropy rate and tier-2 share |

Tests: the ledger closes for all three v2 policies with mortality on/off, contributor sharing and no succession; walls block; the default v1 summary is unchanged by the v2 code; a v2 run exceeds 2,000 genes and more than 10 generations.

## S8: entropy as an explicit objective

A shared controller (all life forms run the same genome) is optimised by evolution strategies (antithetic sampling, centred-rank fitness, common random numbers within a generation). Fitness is the mean of `leak + kappa x heat` over an episode after a burn-in. No births, no extrinsic hazard; starvation is the only death. Behaviour is characterised by action shares (move, stay, invest), capture fraction, leak share, tier shares and population. Baselines: random controller, hand-coded forager, always-invest, always-move, no life forms. See `PREREGISTRATION_S8.md`. The kappa = 1 arm is the control for the accounting assumption.

## Plain-language explainer

`explainer/` builds a single page with the same JavaScript engine as the grid view (`webapp/sim.js`), drawn as swimming creatures, grass motes, wells and embers. Creature colours are founding families. It is not a different model, only a different rendering. The what-if explorer replays the S2 per-condition table; nothing in it is simulated live.

## S11: the cosmic entropy ledger (`src/agency_gradients/cosmos/`)

A stylised, deterministic ledger of a lifeless universe plus an entropy-maximising controller. It is a toy built on published formulas, not an N-body or hydrodynamic model. Preregistration: `PREREGISTRATION_S11.md`.

**Sources for the numbers used.** Observable-universe entropy 3.1e104 k_B, dominated by SMBHs; cosmic event horizon 2.6e122 k_B; stellar BHs 5.9e97 (Egan and Lineweaver 2010, arXiv:0909.3983). Their paper gives two different CMB values (Eq. 13: 2.0e89; Table 1: 5.4e89); the model computes 5.2e89 from the CMB photon entropy density and the observable volume. Affectable region about 16.5 Gly comoving vs 46.4 Gly observable, under 5% of galaxies (Ord 2021, arXiv:2104.01191; our integral gives 16.7 Gly and 4.7% of volume at v=c). BH entropy S = 4 pi G M^2/(hbar c) = 1.05e77 (M/Msun)^2. Hawking evaporation emits 1.4847 times the BH entropy lost (Page 2013, arXiv:1301.4995, quoting his 1976 result); lifetime 5120 pi G^2 M^3/(hbar c^4) = 2.1e67 yr (M/Msun)^3 (photon-only). GW150914 lost about 4.6% of mass; eps_gw is drawn from 2 to 10%.

**State.** Two compartments, unreached (U) and reached (R). Probes at v c from the Milky Way grow R as the comoving cone (v c int dt/a)/46.4 Gly cubed. Baseline physics acts in both; levers act in R. Stocks: IGM and cold gas, five stellar classes (exponential lifetimes, radiated energy at death = fuel fraction x 0.007 of the dying mass, plus a neutrino term for massive stars), white dwarfs, neutron stars, collector mass, and 80 factor-2 black hole mass bins each carrying (count, mass, sum M^2) so BH entropy is exact for the carried moments. Initial stellar content and the SMBH mass function (Schechter-like, solved to give 3.1e104 k_B for the total mass 4.8e18 Msun) are set so that stellar-BH entropy lands near 5.9e97 without tuning.

**Ledgers.** Mass-energy: non-BH mass + BH gravitational mass + stored work + radiated energy is constant. Baryon number: non-BH mass + fusion defect + baryons inside holes + evaporated is constant. Both are checked each step in tests (`tests/test_cosmos.py`) and in every experiment rollout (relative error < 1e-9, observed ~1e-15). A leak injected by hand is detected.

**Entropy.** Blackbody radiation carries (4/3) E/T. Starlight is created at T_eff; baseline dust reprocesses 30% at 20 K (scaled by gas fraction). Collectors capture a fraction kappa of reached starlight (and optionally accretion light), store up to xi_max (1 - T_c/T_hot) of it as work and radiate the rest at T_c = max(environment floor, (P/(sigma A))^(1/4)), with radiator area tied to collector mass. The floor is max(CMB, de Sitter temperature 2.2e-30 K). Spending work on levers produces waste heat at T_c, counted as entropy. Work never spent is not counted. The matter term (a few k_B per baryon) is about 1e80 and irrelevant.

**Bound domains.** Because Lambda separates unbound structures, a hole can only absorb gas from, and merge with holes in, its own gravitationally bound domain (default baryon mass 1.5e14 Msun; drawn between 3e13 and 5e14). This caps hole mass per domain and merger depth, and is the main reason the reachable-universe fraction is not simply converted into one giant hole. Without it (ablation) BH entropy reaches the holographic cap, which the model flags.

**Levers.** (a) star-formation rate multiplier up to 10 in R; (b) funnel cold gas into holes weighted by M^2 and Eddington-capped; (c) pairwise mergers (output mass 2(1-eps_gw) of the pair, exact second moment); (d) collapse WDs and NSs to holes; (e) collectors. Each action costs energy from the work reservoir; if the reservoir is short all requested actions are throttled together. Shares come from a softmax over five levers plus do-nothing.

**Seeds.** The model is deterministic. A seed draws SMBH entropy normalisation (lognormal sigma 0.5 in ln), star-formation timescale, radiative efficiency (6 to 30%), eps_gw and domain mass. Training uses seeds >= 1000, evaluation seeds 0-19.

**Search.** Phase A: 21 named strategies then an antithetic centred-rank evolution strategy over a 6-segment, 6-logit piecewise log-time allocation. Phase B: a 10-input, 16-hidden tanh network over log-time and stock features, same ES. Objective sign(g) log10(1+|g|), averaged over 4 training seeds.

**What the model excludes.** Life, intelligence as a physical agent (the controller has no body, memory limits or error), dark matter as a feedstock, relic neutrinos, galaxy-scale dynamics, radiation in the expansion history, proton decay, black hole spin and charge, gravitational-wave entropy, cosmic strings or other exotica, and anything beyond ordinary GR plus thermodynamics.
