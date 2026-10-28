# S8 - total entropy as the objective

ES runs per kappa: 5, generations: 40, pairs: 12, episode steps: 2000, policy: equivariant

| condition | fitness | entropy_k3 | capture_fraction | leak_share | share_tier1 | share_tier2 | t2_reached | act_move | act_stay | act_invest | pop_late |
|---|---|---|---|---|---|---|---|---|---|---|---|
| optimised, kappa=3 | 35.810 [29.543, 40.072] | 35.810 [29.543, 40.072] | 0.878 [0.783, 0.935] | 0.144 [0.083, 0.250] | 0.122 [0.060, 0.155] | 0.326 [0.162, 0.412] | 0.700 [0.300, 1.000] | 0.449 [0.272, 0.735] | 0.008 [0.003, 0.013] | 0.544 [0.263, 0.717] | 57.304 [54.221, 59.333] |
| random controller, kappa=3 | 18.959 | 18.959 | 0.421 | 0.630 | 0.031 | 0.064 | 0.000 | 0.582 | 0.293 | 0.125 | 29.032 |
| hand-coded forager, kappa=3 | 28.961 | 28.961 | 0.491 | 0.555 | 0.123 | 0.627 | 1.000 | 0.711 | 0.017 | 0.272 | 41.844 |
| always invest, kappa=3 | 12.295 | 12.295 | 0.089 | 0.982 | 0.000 | 0.621 | 0.000 | 0.000 | 0.000 | 1.000 | 0.875 |
| always move, kappa=3 | 20.337 | 20.337 | 0.552 | 0.513 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 38.624 |
| no life forms, kappa=3 | 11.792 | 11.792 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Pre-registered contrasts (mean over ES runs, 95% bootstrap CI)

- H8a  optimised - hand-coded forager (kappa=3), entropy rate: 6.849 [0.582, 11.111]
- H8b  optimised - hand-coded forager (kappa=3), share of actions spent investing: 0.271 [-0.010, 0.444]
