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
| `drift` | births restore the population toward its initial size; parents are chosen uniformly at random among the living |

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
6. Replaced the original **drift control**, which went extinct and so was not a usable null, with a population-restoring neutral model.
7. Made the commons **patchy**, so directed foraging pays immediately.
8. Added a **hand-coded positive control** to measure headroom. Its first version went extinct because of two bugs in my code: it assumed the wrong observation order, and drained reservoirs looked "locked". Both fixed.
9. Added the **equivariant policy** as the default after the MLP failed to evolve useful behaviour.
10. Corrected the **S4 null**. A smoke run showed `delta_recovered > 0` even with no heredity, from survivorship bias; the interpretable quantity is the full-vs-no-heredity contrast.
