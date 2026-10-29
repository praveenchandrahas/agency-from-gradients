# Preregistration S9 - engineered private reward: does learning from energy or heat produce agency?

Written and committed BEFORE the confirmatory run. Pilots (seeds >= 1000) are not evidence.

## Why
S8 showed an explicit entropy objective yields a furnace, not agency. Life does not reward entropy as such; it equips individuals with learned internal signals tied to energy and homeostasis. S9 gives every agent within-lifetime learning and varies the signal. Selection stays persistence-only in every arm. The aim here is engineering: does a private reward, learned in a lifetime, produce anything we would call agency under criteria fixed now?

## Mechanism (src/agency_gradients/world_learn.py, PlasticWorld)
Recurrent policy (hidden 24, ~2,000 genes, world v2). Each agent adds a private correction (dW, db) to its output layer, trained online by a reward-modulated policy gradient with an eligibility trace (lr 0.05, trace 0.95, advantage vs a running per-agent mean, normalised, clipped). The correction is reset at birth (no Lamarckian inheritance). Arms:
- off: no learning
- energy: reward = the agent's own energy change (intake minus cost): a life-like homeostatic signal
- heat: reward = the heat the agent dissipates this step: an explicit private entropy reward

## World (fixed)
v2_config(scale=2, policy="recurrent"), 100,000 steps, seeds 0-19 per arm (20 per arm). Plain v2 (seasons, walls, danger, signal channel). The day/night v3 world was tried in a pilot and every run went extinct, so it is not used.

## Agency criteria (fixed in advance)
1. Predictive probe (`predictive_probe`): extra held-out R^2 from adding the hidden state to the observation when predicting the agent's own energy gain over the next 20 steps (ridge, held-out agents), minus the same quantity for freshly drawn random genomes in the same environment (`pred_delta`).
2. Viability probe (`delta_recovered`, as in S4): recovery of displaced, depleted agents, evolved/trained minus random.

## Hypotheses (difference of means over runs with valid probes; 95% bootstrap CI)
- H9a: pred_delta(energy) - pred_delta(off) > 0
- H9b: pred_delta(heat) - pred_delta(off) > 0
- H9c: delta_recovered(energy) - delta_recovered(off) > 0
- H9d: delta_recovered(heat) - delta_recovered(energy) < 0 (the explicit entropy reward is worse for agency than the energy signal)
Supported means the stated CI bound excludes zero in the stated direction. Secondary, descriptive: entropy rate, tier-2 share, extinction, generations.

## Interpretation rules
- Runs that go extinct have no valid probes; they are excluded from H9a-d and their rate is reported beside each arm.
- A null on H9a/b cannot separate "no predictive information" from "the probe is too weak": the probe is linear, targets only the agent's own energy gain, and has no positive control in this study. In the 3-seed pilot all arms were near zero.
- The heat arm rewards spending; if it produces more entropy but not more recovery or prediction, that repeats the S8 lesson at the individual level.
- Learning is within a lifetime and not inherited, so this does not test a Baldwin effect.

## Deviation log
(empty at registration)
