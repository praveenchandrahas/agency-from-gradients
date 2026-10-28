# Pre-registration S8: what does an explicit entropy objective produce?

Filed after a 2-run-per-kappa pilot (seeds 1000-1001, `docs/results/pilot/s8_*`) and before any S8 confirmatory run. **The pilot informed these hypotheses and the fixed parameters below**, so unlike H1-H5 they are not blind predictions.

## Manipulation (the opposite of S1-S6, on purpose)

A single shared controller (the 27-parameter `equivariant` policy, run by all 60 life forms) is optimised by evolution strategies directly for world entropy production, `leak + kappa x heat`. Nothing rewards survival or reproduction: no births, no extrinsic hazard (`hazard = 0`), starvation is the only death. Everything else is the default world.

Fixed ES settings: 40 generations, 12 antithetic pairs, sigma 0.4, learning rate 0.3, episodes of 2,000 steps (first 400 discarded), common random numbers within a generation. Final controllers are evaluated on 8 held-out worlds (seeds 5000-5007) for 4,000 steps. Baselines (random controller, hand-coded forager, always-invest, always-move, no life forms) use the same evaluation. **Confirmatory:** ES-run seeds 0-4 for each kappa in {3, 1}. Pilot seeds are >= 1000.

## Hypotheses

**H8a.** At kappa = 3 the optimised controller exceeds the hand-coded forager on entropy rate.
Supported if `optimised - forager` has a 95% bootstrap CI above 0 across the 5 ES runs.

**H8b.** The objective produces "furnace" behaviour: more of the optimised controller's actions are investing than the forager's.
Supported if `act_invest(optimised) - act_invest(forager)` has a 95% CI above 0. (Pilot: 0.71 vs 0.27.)

**H8c.** The objective only has something to optimise because of the kappa assumption: the gain over a random controller is larger at kappa = 3 than at kappa = 1.
Supported if `gain(kappa=3) - gain(kappa=1)` has a 95% CI above 0.

## What would count as informative either way

- H8a supported and H8b supported: an explicit entropy objective finds a behaviour that scores higher than anything we hand-wrote, but it does so by burning energy, not by anything we would call agency.
- H8c not supported: the objective is not merely an artefact of kappa; follow up before drawing conclusions.
- Not preregistered: any claim about which tier the controllers use, about what the behaviour "means", or about transfer to the evolutionary setting. A shared controller removes the free-rider problem seen in S2/S6 by construction.

## Deviation log

(none yet)
