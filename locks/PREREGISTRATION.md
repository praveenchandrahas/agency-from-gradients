# Pre-registration S15, Locks: does life open gradients that nothing else opens?

**Status: FROZEN.** Committed to `main` on 2026-11-23, before the confirmatory run. The run records this file's SHA-256 in `RUN_INFO.txt`.

The reasoning is in [`SPEC.md`](SPEC.md). The engine is `locks/world.py`. The runner is `experiments/s15.py`. The analysis is `analysis/report.py`, frozen with this file. The workflow is `.github/workflows/s15.yml`. Any departure from this file goes in the deviation log below before results are reported.

## How the numbers were set

The author settled the five design decisions in `SPEC.md`, then asked for the run. The numbers below were set by Claude from the control pilot, the G6 calibration and the arithmetic under "My expectations". The author did not review them line by line before freezing. I record that here because it matters: the numbers were not tuned by the author, and they were not tuned on any living, fire or mineral world.

## What this run tests

H1 and H2 of the spec, in one lock. H3 (drifting and stacked locks) is not tested here. It gets its own preregistration, and only if H2 holds.

## The claim

> In cold, locked gradients, where passive structures and non-living dissipative ones stall, life opens the lock. Nothing else does.

## Frozen parameters

Every value is the default in `locks.Config` at the commit that adds this file.

| Parameter | Value | Meaning |
|---|---|---|
| Δμ₀ | 6 kT | Standard free-energy drop of F → W |
| f_in, w_in | 200, 1 | Feed levels of fuel and waste |
| k₀ | 100 per residence time | Attempt rate |
| dilution | 1 | Time is in residence times |
| b_cat, λ | 0, 0.5 kT per bit | A catalyst's route has barrier b_cat + λd |
| vol | 1,000 | Count to concentration |
| η | 0.5 | Share of its released free energy a growing catalyst can store |
| e_div | 20 kT | Stored energy at which a catalyst splits |
| upkeep | 0.5 kT per residence time | |
| hazard | 0.01 per residence time | Death from all other causes |
| μ | 0.002 per bit per division | Mutation, arm L only. Markers mutate at the same rate |
| n0, e0 | 100 catalysts, 10 kT each | Starting library for D and L |
| dt | 0.01 | Time step |

## Factors

- **Arms:** N, M, D, L, U, as defined in the spec.
- **Key length n:** 24 and 32. Both are primary. Each gets its own verdict. Why two: see "My expectations".
- **Barrier B:** 0, 2, 4, 6, 8, 10, 12, 16 kT.
- **Seeds:** 0 to 19, in every cell. D and L of the same seed start from the same library and the same lock. M's random keys come from a separate stream.
- **Length:** 4,000 residence times.
- **Windows:** primary 3,500 to 4,000. Secondary 1,500 to 2,000. Verdicts are taken on the primary window. Both are reported (risk R3).

**Matching.** In each (n, B) cell, M and U get the mean late-window catalyst count of L in that cell, over the 20 seeds, rounded. If every L world is extinct, the count is 0, and M and U are the passive world.

**Equivalent library (secondary).** At B = 16 only, M is also run with 10 and 100 times the matched count.

## Measurements

- **σ**: total entropy production, reactions plus mixing, in k_B per residence time, mean over the window.
- Reactions alone and mixing alone, fuel spent, catalyst count.
- For L: mean key distance to the lock, and mean marker distance to a random fixed target (the neutral baseline).
- Extinctions. An extinct world keeps running as the passive world and is scored as it runs.
- Intervals: 95% percentile bootstrap on seed means, 10,000 resamples, paired by seed. Bootstrap generator seeded with 15.

## Hypotheses and decision rules

All at the primary window, separately for n = 24 and n = 32.

| | Test | Supported if |
|---|---|---|
| **H1** | Structure beats passive at B = 16 | Intervals of σ(D) − σ(N) and σ(L) − σ(N) both lie above 0 |
| **H2a** | Life beats the mineral and the fire at B = 16 | Intervals of σ(L) − σ(M) and σ(L) − σ(D) both lie above 0 |
| **H2b** | Life's advantage grows with B | Interval of the least-squares slope over B of the per-seed advantage σ(L) − max(σ(M), σ(D)) lies above 0. Seeds resampled jointly across B |
| **H2c** | No lock, no advantage | At B = 0, the intervals of σ(X)/σ(N) − 1 for X = M, D, L all lie inside ±0.02 |
| **H2d** | Life never beats the designer bound | No interval of σ(L) − σ(U), at any B, lies above 0 |
| **H2e** | Nothing else opens the lock | At B = 16, the intervals of σ(D)/σ(U) and σ(M)/σ(U) both lie below 0.10. *Not supported* if either lies above 0.10. *Inconclusive* otherwise |

**H2e is new relative to the spec.** H2a tests whether life does *better*. It cannot test "nothing else does". A fire could open the lock to 90% and life to 99%, and H2a would pass. H2e asks the second half of the claim directly: do the non-living arms stall?

**Overall verdict, per key length,** in this order:

1. H2c not supported → *model broken*. Nothing else counts.
2. H2a and H2b both not supported → *the narrow claim fails in this model*.
3. H2a, H2b and H2e all supported → *the narrow claim is supported in this model*.
4. H2a and H2b supported, H2e not → *life does better, but something else also opens the lock. "Nothing else does" fails.*
5. Anything else → *mixed*.

H1 and H2d are checks. They are expected by construction (see the spec).

## Risks reported either way

- **R1. Overexploitation.** Extinctions per cell for D and L.
- **R2. Sheltering.** For L, marker distance minus key distance at the end. Above 0 means keys moved toward the lock faster than neutral drift. Below 0 would mean sheltering.
- **R3. Two horizons.** Every table at both windows.

## My expectations

Written before the run. They come from steady-state arithmetic only (`analysis/expectations.py`). No living, fire or mineral world was simulated to get them.

A growing catalyst survives when its gain pays its upkeep plus its share of hazard losses: about 0.65 kT per residence time. On untouched fuel at B = 16, that needs a key within 10 bits of the lock.

| | n = 24 | n = 32 |
|---|---|---|
| Chance a random key is within 10 bits | 0.27 | 0.025 |
| Expected viable keys in a library of 100 | 27 | 2.5 |
| Expected best key in the library | 6 bits off | 9 bits off |
| **Fire**, best library key, steady state | σ ≈ 990 to 1,070, about 560 catalysts | σ ≈ 35 to 340, about 25 to 230 catalysts, at risk of dying |
| **Life**, near-perfect key | σ ≈ 1,185, about 370 catalysts | σ ≈ 1,185, *if it climbs* |
| **Mineral**, 370 random keys | σ ≈ 280 (16% of fuel spent) | σ ≈ 60 (3%) |
| **Designer**, 370 perfect keys | σ ≈ 1,185 | σ ≈ 1,185 |

So I expect:

- **At n = 24, H2e fails for the fire.** A random library already holds a key good enough to live on cold fuel. The fire makes up for its weaker key with numbers. Life should still beat it (H2a), by about 10 to 20%. Overall: "life does better, but something else also opens the lock."
- **At n = 32, the fire mostly stalls.** The best library key is barely viable. Whether life wins depends on whether it climbs from that foothold before it starves. If it does, H2a and H2e both pass. If it doesn't, life dies with the fire and H2a fails.
- **The mineral stalls at both lengths**, unless the equivalent-library sweep shows that 10 or 100 times more random keys close the gap.

If these expectations hold, the honest reading is this. Whether "nothing else does" is true depends on how rare a working key is among the structures already lying around. That is a property of the chemistry, not of life. This model sets it with *n*, and I chose *n*.

## Pilots seen before freezing

- **Control pilot** (N and U, seeds 1000 to 1002). Table in `SPEC.md`. Raw output in `results/pilot_controls.json`.
- **G6 calibration.** Arm L seeded with the perfect key, B = 16, seed 1000, 400 residence times, n = 24 and n = 32. I looked at run time (about 0.7 s per 100 residence times), catalyst count (about 405), σ (about 1,195) and key distance (under 0.1). This is the positive control, not a random-start world.
- **Leak, recorded in the spec.** One random-start L world (seed 1000, B = 12, 100 residence times): I looked at its population size only.
- **Plumbing check.** Both stages and the report, at 10 residence times, seeds 1000 to 1001, all cells. I checked that every file was written and that the report built. I did not read its numbers.

## Deviation log

None yet.
