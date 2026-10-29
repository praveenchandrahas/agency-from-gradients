# Preregistration S7-v3 - combined "big genome, big population, recombination, richer world" comparison

Written and committed BEFORE any confirmatory run. Pilots (S7, seeds >= 1000, world v2) are not evidence for or against these hypotheses; they motivated the design.

## Question
In the pilots, a ~2,000-gene recurrent policy did not beat the 29-gene chemotaxis-shaped policy (it reached the big tier-2 deposits less often). Candidate causes: too many harmful mutations per child, no recombination, too small a population, too few generations. This test bundles the remedies: recombination + a ~5x lower mutation rate + a ~3x larger arena/population + a larger genome (hidden 48, ~5,385 genes) + a more complex world. Does selection by persistence alone then produce energy-ladder use that exceeds (a) random parents and (b) the small policy?

## World v3 (fixed, identical for all variants)
v2 world at scale 3 (96x96, ~3x population cap) plus: day/night cycle (period 500; night = regrowth x0.5, danger hazard x3; two day-phase inputs), resource field drifting one cell every 400 steps, danger zones random-walking every 50 steps, seasons, walls, signal field. Block crossover (block 48) with a random living neighbour within 3 cells (asexual if none); mutation rate 0.004 per gene (sigma 0.05) plus rare large mutations (p 0.0001, sigma 0.5). 200,000 steps. Source of truth: `v3_config` in `src/agency_gradients/config.py` (frozen from the commit that contains this file).

## Variants
- A: recurrent:48, selection = persistence (the treatment)
- B: recurrent:48, random parents (selection = drift; same machinery, no selection)
- C: 29-gene equivariant policy, same world and genetics (reference)
- D: hand-coded forager (headroom; not tested)

Seeds 0-19 for every variant (20 per arm). No seed or setting is changed after seeing results.

## Hypotheses (primary metric: share of harvested energy from tier 2, whole run, `share_tier2`; 95% bootstrap CI of the difference of means; "supported" = lower bound > 0)
- H7a: A - B > 0.
- H7b: A - C > 0.
- H7c: tier-2 share in the last tenth of the run minus the first tenth, within A, > 0.

Secondary, descriptive only: entropy_rate, generations (gen_mean), signal_rate, tier-1 share, tier-2 reach, extinctions.

## Interpretation rules (fixed in advance)
- Bundling: the comparison changes five things at once. A positive result shows the package works, not which part; a null does not show that none of the parts could work in other settings or at more generations.
- A tier-2 share below the 29-gene policy's would be reported as a failure of the large genome at this budget, not explained away.
- Gaps to D are reported as headroom.
- Entropy is measured, never rewarded; selection is by persistence only (as in earlier experiments).
- Plumbing smoke tests only on seeds >= 1000.

## Outcome (recorded after the run, Actions run 40738250309, seeds 0-19)
H7a, H7b, H7c: all NOT supported. A - B share_tier2 -0.000 [-0.001, -0.000]; A - C -0.037 [-0.092, -0.001]; A last - first window -0.020 [-0.033, -0.008]. Extinction before 200k steps: A 90%, B 70%, C 20%, D 20%, so A/B metrics come from truncated runs. Report: `docs/results/s7_v3/`.

## Deviation log
None. (Extinction handling was not specified in advance; extinct runs are included as they ended, which is a gap in this preregistration.)
