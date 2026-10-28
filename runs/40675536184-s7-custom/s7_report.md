# S7 - complex world (v2)

seeds: 2, steps: 200000, scale: 2

| variant | entropy_rate | share_tier2 | share_tier1 | t2_reached | signal_rate | gen_mean | pop_mean_late | extinct |
|---|---|---|---|---|---|---|---|---|
| recurrent (~2,000 genes) | 100.403 [99.565, 101.242] | 0.016 [0.004, 0.028] | 0.001 [0.001, 0.001] | 1.000 [1.000, 1.000] | 0.016 [0.005, 0.027] | 1779.117 [1645.815, 1912.419] | 290.630 [279.162, 302.099] | 0.000 [0.000, 0.000] |
| small chemotaxis policy (29 genes) | 120.304 [116.617, 123.992] | 0.063 [0.037, 0.089] | 0.108 [0.000, 0.215] | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] | 1747.053 [1451.756, 2042.349] | 361.634 [321.738, 401.530] | 0.000 [0.000, 0.000] |

## Contrasts (difference of means, 95% bootstrap CI)

- S7b recurrent - small policy : share_tier2: -0.047 [-0.085, -0.009]
- S7b recurrent - small policy : entropy_rate: -19.901 [-24.426, -15.375]
- S7c recurrent, last window - first window : tier-2 share: -0.016 [-0.036, 0.004]
