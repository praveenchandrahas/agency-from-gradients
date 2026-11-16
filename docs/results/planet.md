# Planet: three follow-ups on the paper's model

Preregistered in [`planet/PREREGISTRATION.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/planet-v02-followups/planet/PREREGISTRATION.md), frozen before the runs. 520 runs, 20 replicates per cell, 95% bootstrap intervals on replicate means. Full tables are in [`planet/RESULTS.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/planet-v02-followups/planet/RESULTS.md).

!!! abstract "Verdict"
    **9 of 12 predictions supported.** The three that failed were my own guesses, not claims from the paper. Agency carriers beat non-carriers on the same planet. But the planet captures less energy as they win. And most of the rise in agency traits is drift.

## Why this page exists

The paper "Energy Capture, Agency, and Planetary Entropy" has its own model (v0.2) and its own repo. A consistency check of the paper left three gaps. I closed them here, in the main repo, with the paper's source copied in unchanged. With the new switches off, the engine reproduces the paper bit for bit. That is tested.

This is a separate model from the S-series on the other pages. Different world, different code.

## E1. Who wins when both types share a planet?

The paper compares whole planets. Carriers only, or no carriers. Selection never gets to choose.

So I put both types on one planet. Start 50/50. Let selection decide.

![Carrier fraction over time, by environment](../figures/planet_e1_competition.png)

- **Volatile:** carriers fix in 19 of 20 planets. Fraction 0.950.
- **Strong hotspots:** carriers fix in 20 of 20. Fraction 1.000.
- **Weak:** carriers drift down, from 0.665 at generation 220 to 0.484 at 660. Agency is not free.

Now the catch. In the strong world, throughput falls to 43.9 TW once carriers win. Non-carriers alone capture 134.7 TW. Selection picks the type that captures less.

Which part of agency wins? I ran two extra arms. Harvest bonus only. Directed movement only.

At generation 220, the bonus wins everywhere. Movement alone helps in volatile and strong. It does not in weak.

By generation 660 the split is clear. The bonus alone still holds (0.76 to 0.95). Movement alone collapses in weak (0.097) and seasonal (0.272).

The bonus is a hand-written term in the paper's model. So what selection rewards is the built-in reward. That is a limit on the claim, and it is mine to own.

## E2. How far does a trait rise if it does nothing?

Mutation plus clipping at zero pushes any trait upward. So a rise in agency proves nothing by itself.

I added five dummy traits. They mutate and clip like the agency traits. They do nothing.

![Agency traits against neutral markers](../figures/planet_e2_markers.png)

- Markers rise by +0.114 to +0.163 in every scenario, with no function at all.
- At generation 220, agency beats its markers only in the strong world: +0.057 [0.020, 0.093].
- In weak, agency ends below its markers: −0.032.
- By generation 660, agency is at or below its markers everywhere. The action trait is about 0.04, below where it started.

Most of the rise the paper reported is drift.

## E3. Why are populations small when each entity has plenty?

The paper's planets hold far fewer entities with agency. Per-entity energy is high. So why?

![Where the energy goes](../figures/planet_e3_demography.png)

It is inequality, not a transient.

- Mean-field growth is 1.17 with agency. Without it, 1.03.
- Realised growth is about 0.999. The surplus is not turning into people.
- The share of entities below the survival threshold: 31% with agency, 10% without.
- The best-off 10% earn 8.5 times the median.
- Two thirds of the population sits in the fullest 5% of patches (0.66, against 0.17).

![Population on the planet map](../figures/planet_e3_map.png)

Generation 220 is also the bottom of a dip. By generation 660 strong-world throughput recovers from 47.7 to 108.2 TW. Still below the 135 of non-carriers. But the paper's endpoint overstates the gap.

## What this does not show

- **One-sided test.** The resource pool is a fixed 0.1% of absorbed power. Controls already capture about 99% of it. Agency could not raise throughput above that ceiling even if it wanted to.
- **Why carriers win.** Their mean survival is lower than non-carriers'. My guess is that births go to the highest earners. I have not tested it.
- **The bonus is assumed.** See E1.
- **Three of twelve predictions failed.** P1b, P1c, P1d. All three were guesses. P3c held at generation 220 and flips sign at 660.
- **Twenty replicates.** Outcomes near fixation are lumpy. 0.950 means one planet out of twenty went the other way.
- **A toy planet.** It says nothing about Earth.

## Where the numbers live

| What | Where |
|---|---|
| Frozen predictions | [`planet/PREREGISTRATION.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/planet-v02-followups/planet/PREREGISTRATION.md) |
| All tables | [`planet/RESULTS.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/planet-v02-followups/planet/RESULTS.md) |
| Raw per-run CSVs | `planet/results/` on the same branch |
| Code and tests | `planet/planet/`, `planet/tests/` |
| Pull request | [#7, draft](https://github.com/praveenchandrahas/agency-from-gradients/pull/7) |
