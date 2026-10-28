# S8 - total entropy as the objective

ES runs per kappa: 5, generations: 40, pairs: 12, episode steps: 2000, policy: equivariant

| condition | fitness | entropy_k3 | capture_fraction | leak_share | share_tier1 | share_tier2 | t2_reached | act_move | act_stay | act_invest | pop_late |
|---|---|---|---|---|---|---|---|---|---|---|---|
| optimised, kappa=1 | 14.838 [13.115, 16.307] | 27.635 [17.574, 36.766] | 0.432 [0.133, 0.732] | 0.583 [0.295, 0.872] | 0.205 [0.092, 0.341] | 0.332 [0.102, 0.562] | 0.600 [0.200, 1.000] | 0.371 [0.188, 0.586] | 0.139 [0.045, 0.284] | 0.490 [0.292, 0.632] | 32.228 [11.582, 52.522] |
| random controller, kappa=1 | 10.950 | 18.959 | 0.421 | 0.630 | 0.031 | 0.064 | 0.000 | 0.582 | 0.293 | 0.125 | 29.032 |
| hand-coded forager, kappa=1 | 15.304 | 28.961 | 0.491 | 0.555 | 0.123 | 0.627 | 1.000 | 0.711 | 0.017 | 0.272 | 41.844 |
| always invest, kappa=1 | 11.857 | 12.295 | 0.089 | 0.982 | 0.000 | 0.621 | 0.000 | 0.000 | 0.000 | 1.000 | 0.875 |
| always move, kappa=1 | 10.294 | 20.337 | 0.552 | 0.513 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 38.624 |
| no life forms, kappa=1 | 11.792 | 11.792 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Pre-registered contrasts (mean over ES runs, 95% bootstrap CI)

