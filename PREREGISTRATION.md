# Pre-registration

Filed before any confirmatory run. The design, parameters and analysis below are frozen at the commit that adds this file.

## Protocol

- **Confirmatory seeds:** 0 to 29, 20,000 steps, default `Config`. Pilot seeds (>= 1000) may be used freely for debugging and must not be reported as evidence.
- **Intervals:** 95% percentile bootstrap, 4,000 resamples (1,000 for the S2 main-effect table).
- **Decision rule:** a hypothesis is *supported* only if its stated interval excludes zero in the stated direction. An interval that includes zero means *not shown at this power*; it is not evidence of no effect.
- **Power note:** `t2_reached` is binary. With 30 runs per cell, differences smaller than roughly 0.25 are unlikely to be detected. A null on a factor in S2 may simply mean the effect is small or the design underpowered.
- **Deviations** from this document must be listed under "Deviation log" below, with the reason, before results are reported.

## Hypotheses and falsifiers

**H1 (S1). Persistence-only selection raises entropy production without rewarding it.**
Supported if `entropy_rate(persistence) - entropy_rate(drift)` has a 95% CI above 0.
Falsified for this world if the CI includes 0 or is below 0.

**H2 (S2). Tier-2 access needs scarcity, heredity and mortality.**
For each of the three, supported as load-bearing if `t2_reached(all four factors on) - t2_reached(that factor off)` has a 95% CI above 0.
A factor whose CI includes 0 is not shown to be load-bearing in this design. `succession` is tested two-sided, with no directional prediction.

**H3 (S4). Heredity contributes to restoration ability.**
Supported if `delta_recovered(full) - delta_recovered(no heredity)` has a 95% CI above 0.
The raw `delta_recovered` is not tested, because it is inflated by survivorship.

**H4 (S1). Rewarding entropy directly does not improve Tier-2 access over persistence.**
Falsified if `t2_reached(entropy) - t2_reached(persistence)` has a 95% CI above 0.

**H5 (S3). Accounting check, not evidence.**
`capture_ratio` with `kappa = 1` must lie between 0.7 and 1.15. If not, the accounting is broken and no S3 number is reported.

## Not preregistered (exploratory)

- Any claim that entropy-as-reward breeds "furnaces" (high entropy, low capture). The pilot did not show it and it is not claimed.
- Absolute `capture_ratio` values.
- Anything about prediction or world-modelling. Not measured.
- Interactions between factors, beyond what the per-condition table shows.

## What would change my mind

- H1 falsified: the "no objective needed" claim fails in this world.
- H2 with no factor load-bearing: the ablation grid cannot tell the conditions apart here, and the next step is a harder or longer world, not a conclusion.
- H3 falsified: whatever the evolved agents have, it is not heritable, which undercuts the agency reading of the whole suite.

## Deviation log

(none yet)
