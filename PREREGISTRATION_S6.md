# Pre-registration S6: is the H2 failure a free-rider problem?

Filed after the main confirmatory run (see `PREREGISTRATION.md`) and before any S6 confirmatory run. S1-S5 are unchanged: the new rule is behind `Config.deposit_share`, whose default `"equal"` reproduces S1-S5 bit for bit (checked on seed 0).

## Motivation and what is a post-hoc hypothesis

H2 failed: removing scarcity, heredity or mortality *raised* big-deposit access. My explanation, formed after seeing the data, is that opening a deposit is a public good (the benefit is split evenly on the square, the cost falls on the investor), so selection under fatal starvation and inheritance penalises investing. S6 is a test of that explanation, not a confirmation of the thesis.

## Manipulation

`deposit_share = "contributor"`: the reservoir harvest on a cell is split in proportion to each agent's investment trace (decay 0.98 per step; +1 per invest action on a reservoir) plus a floor of 0.02 for non-investors. Total harvest is unchanged. Parameters are fixed here and will not be tuned. Everything else is the full world (scarcity, mortality, succession on). Heredity is crossed with the sharing rule: 4 conditions.

## Protocol

Seeds 0-29, 20,000 steps, 95% percentile bootstrap, same decision rule as `PREREGISTRATION.md`. Plumbing pilot on seeds >= 1000 only. Because `t2_reached` ("ever fully open") was shown to be a coarse metric in the main run, the primary metric here is `share_tier2` (steady-state share of energy from big deposits); `t2_reached` is reported alongside.

## Hypotheses

**H6a.** Private benefit increases steady use of big deposits under heredity.
Supported if `share_tier2(contributor, heredity) - share_tier2(equal, heredity)` has a 95% CI above 0.
Not supported if the CI includes 0 or is below it. In that case the free-rider explanation, in this form, is not supported.

**H6b.** Heredity becomes load-bearing once investing pays privately.
Supported if `share_tier2(contributor, heredity) - share_tier2(contributor, no heredity)` has a 95% CI above 0.
(In the main run the equivalent contrast was negative.)

## Not preregistered

Any claim about kin sharing, other decay rates, other trace forms, entropy rate, or whether the effect transfers beyond this world. A positive result would say only that making the benefit private lets selection find big deposits here; it would not say Earth's agency arose this way.

## Deviation log

(none yet)

## Outcome

H6a not supported (CI includes 0); H6b not supported (heredity still lowers `t2_reached`; `share_tier2` CI includes 0). No deviations. Reports in `docs/results/s6_*`.
