# Pre-registration S12: where in physical-parameter space does persistence selection pay?

**Status: DRAFT. Not frozen. No S12 run of any kind has been made, pilots included.**
It becomes a preregistration when the author approves it and the commit that adds it lands on `main`. The script that implements it (`src/agency_gradients/experiments/s12_habitability.py`) does not exist yet. It will be written to this specification. Any place where the script departs from this file goes in the deviation log before results are reported.

## Question

The thesis, restated (see `docs/thesis-v2.md`), is conditional, not unconditional:

> Given a steady flux that arrives at a surface, a gradient the surface can tap, stores that hold energy for a while, and heredity, structures that capture more of the flux persist more.

S1 to S11 ran at one setting of the physical parameters. S12 asks the next question. **Does the effect depend on those parameters, and over what range does it appear?**

The two things the thesis adds are the flux and the stores. So the sweep varies exactly those: how much energy arrives, how much of it lands in the ladder, and how long the stores hold it.

## Honest framing

- **This tests the toy world, not Earth.** It cannot say how rare life is. It can say how rare *this world's* emergence is across a range of settings.
- **There is no "cold sink" knob.** The thesis leans on a hot source and a cold sink: sunlight in at about 5,800 K, infrared out at about 255 K. The pond has no temperature. The nearest knob is `kappa`, but that is an accounting weight. Sweeping it would change the *measurement*, not the world. So the temperature-ratio part of the thesis is **not tested here**.
- **The policy class is fixed and small.** The 27-gene, chemotaxis-shaped policy, as in S1 to S6. A map that comes back empty says nothing about larger genomes. S7 is the place for that.
- **Related results are already known.** H1 was supported. H2, S6 and S7 failed. My expectations below are informed by them, so H12a to H12c are not blind predictions. They are, however, written before any S12 run.

## Manipulation

Three physical knobs on the default world. Nothing else changes: heredity, mortality, succession and scarcity stay on, and `kappa = 3`.

| Knob | What it stands for | Fields set | Levels |
|---|---|---|---|
| **Surface flux, c** | Energy arriving as diffuse commons | `commons_regrow = c` | 0.004, 0.008, 0.016 |
| **Ladder throughput, m** | Energy arriving into locked reservoirs | `regrow1 = 0.30 m`, `regrow2 = 1.6 m` | 0.5, 1, 2 |
| **Residence time, τ** | How long an untapped store holds energy | `reservoir_leak = 1/τ`, `stock1 = 0.30 m τ`, `stock2 = 1.6 m τ` | 250, 500, 1000 steps |

Why the stocks are tied to the other two: in the engine, a reservoir's stock settles where regrowth balances leak, at `regrow / reservoir_leak`. Holding the stocks at that equilibrium keeps throughput and residence time independent of each other. Throughput is `m`. Residence time is `τ`.

**The centre cell** (c = 0.008, m = 1, τ = 500) is exactly the default `Config`: 0.30 × 500 = 150 and 1.6 × 500 = 800.

27 cells.

## Arms

| Arm | Description | Seeds |
|---|---|---|
| **A** | Persistence selection, evolved from random genomes (the treatment) | 0 to 19 |
| **B** | Random parents, `selection = "drift"` (the null) | 0 to 19 |
| **C** | The hand-coded forager (headroom) | 0 to 9 |

27 × (20 + 20 + 10) = **1,350 runs**. Each runs 20,000 steps, as in S1 to S6. By analogy with S2 (480 runs in roughly 30 to 60 minutes on two cores), I estimate roughly 1.5 to 3 hours on two cores. That is an estimate. I have not measured it.

Seeds 1000 and above are for plumbing checks only and are never reported as evidence.

## Protocol

- **Intervals:** 95% percentile bootstrap, 4,000 resamples. For the primary contrasts, resampling is **stratified by cell**. Within each cell, resample the runs of each arm independently, form the difference of cell means, and average over cells with equal weight.
- **Decision rule:** a hypothesis is *supported* only if the 95% interval excludes zero in the stated direction. I also report the Bonferroni-adjusted interval (98.33%, for three primary tests). Where the two disagree I say so, and I treat the result as not robust to multiplicity.
- **Extinct runs are kept.** They enter every metric as they ended. This was a gap in the S7 preregistration. Here it is fixed in advance. I also report extinction rates per arm per cell, and a sensitivity analysis with extinct runs removed.
- **Two checks that gate everything.** If either fails, no S12 result is reported.
  1. **Reproduction.** The centre-cell arm-A runs on seeds 0 to 19 must match, field for field, a fresh run of the persistence arm of `s1_selection` on seeds 0 to 19. The two use identical configs, so they should agree exactly.
  2. **Ledger.** Over all 27 configs, the energy ledger residual stays below 1e-6 in a smoke run.

## Measures

All already exist in `World.summary()`.

- **`capture_fraction`:** energy intercepted by agents over intercepted plus passively leaked, last quarter. This is the "absorbed rather than wasted" measure.
- **`share_tier2`:** the share of captured energy from the big reservoirs, last quarter. This is the ladder-climbing measure.
- **`first_t2`:** the step of the first full tier-2 opening, where it happens.
- **`extinct`, `pop_mean_late`, `entropy_rate`, `t2_reached`.**

**Emergence criterion, E (per run):** not extinct **and** `share_tier2 ≥ 0.10`.

The threshold is a judgement. I chose it as about five times the evolved level in the default world (about 0.02) and one fifth of the forager's (about 0.50). It is not derived from anything. So I also report the criterion rate at 0.05 and at 0.20, and the continuous `share_tier2`. The primary tests use the continuous measure, not E.

## Headroom cells

A **headroom cell** is a cell where arm C meets E in at least 8 of its 10 runs.

This separates two things the earlier experiments blurred together. A world where even a hand-coded forager cannot do it is a world where nothing could. It tells you nothing about evolution.

The primary tests use headroom cells only. The rule depends only on arm C, never on arms A or B. I also report every analysis over all 27 cells.

If there are **fewer than 5 headroom cells**, the primary tests are declared *not run*, and the finding is that the swept range mostly cannot support the behaviour even in principle.

## Hypotheses

All are pooled over headroom cells, A minus B.

**H12a. Persistence captures more of the flux.**
Supported if the pooled difference in `capture_fraction` has a 95% interval above 0.
*Why:* this is the thesis's core claim, in its own measure.

**H12b. Persistence climbs the ladder more.**
Supported if the pooled difference in `share_tier2` has a 95% interval above 0.
*Why:* this is the agency-relevant claim.

**H12c. Longer residence time widens the gap.**
Let `gap(τ)` be the pooled A-minus-B difference in `share_tier2` over headroom cells at that τ. Supported if `gap(1000) − gap(250)` has a 95% interval above 0. Evaluated only if each of those two τ levels has at least 2 headroom cells.
*Why:* this is the one claim that is new in thesis v2. It says stored energy, released slowly, is what lets selection find the ladder.

## My expectations

- **H12a: supported.** Consistent with H1.
- **H12b: not supported.** Consistent with S2, S6 and S7.
- **H12c: open.** I have no evidence either way. The thesis predicts yes, and this is the claim that can fail it.

## Not preregistered (exploratory)

- **Time to emergence.** `first_t2` by cell, among runs that reach it, and the fraction that never do. This is censored and conditional on success, so it is descriptive only. It is the nearest thing here to "life takes time".
- **The map.** The 3 × 3 × 3 grid of emergence rates, with extinction rates alongside.
- **Interactions** among c, m and τ beyond what the map shows.
- **Why** any pattern appears. Succession timing depends on stock size, because a tier-1 site is "drained" when its stock falls to 1. So τ may act through succession and not through storage as such. I will not claim to separate them.

## What would change my mind

- **H12c falsified.** The gap does not grow with residence time. Then storage is not doing, in this world, what thesis v2 says planetary storage does.
- **An empty map.** No cell where the headroom rule and the emergence criterion are both met under arm A. Then, for this policy class, selection alone does not find the ladder anywhere in the swept range. That is informative, and it is not a refutation of the thesis.
- **Too few headroom cells.** The next step is a wider sweep, filed as a new preregistration. It is not an extension of this one.

## Deviation log

(none yet)

## Outcome

(not run)
