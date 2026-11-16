# Planet: results

Every number below is computed by `analysis/report.py` from the CSVs in `results/`. Intervals are 95% bootstrap intervals on replicate means, 20 replicates per cell. Predictions are in `PREREGISTRATION.md`. The endpoint is the mean over generations 201 to 220, the paper's endpoint. A second endpoint, 641 to 660, is shown beside it.

520 runs, 0 extinct.

## First, the paper's own table

Replicates 0 to 5 at generation 220 use the paper's seeds. Mean ± between-replicate SD. These equal Table 2 of the paper.

| Scenario | Population | Collector | Agency | Throughput (TW) | Per entity (GW) | Occupancy |
|---|---|---|---|---|---|---|
| weak | 5211 ± 3044 | 0.936 ± 0.013 | 0.195 ± 0.061 | 109.84 ± 32.74 | 25.53 ± 9.21 | 0.803 ± 0.254 |
| seasonal | 3657 ± 3141 | 0.953 ± 0.011 | 0.215 ± 0.060 | 85.67 ± 48.22 | 30.75 ± 10.30 | 0.639 ± 0.357 |
| volatile | 2911 ± 2329 | 0.941 ± 0.012 | 0.206 ± 0.044 | 81.11 ± 28.16 | 33.13 ± 7.98 | 0.579 ± 0.226 |
| strong | 1106 ± 1021 | 0.944 ± 0.032 | 0.258 ± 0.022 | 41.91 ± 28.46 | 42.21 ± 6.26 | 0.292 ± 0.215 |
| volatile, no agency | 8463 ± 287 | 0.941 ± 0.008 | 0.000 ± 0.000 | 135.93 ± 0.56 | 16.08 ± 0.56 | 0.998 ± 0.003 |
| strong, no agency | 8271 ± 522 | 0.942 ± 0.008 | 0.000 ± 0.000 | 134.42 ± 0.98 | 16.30 ± 1.00 | 0.992 ± 0.002 |

## E1. Competition: carriers and non-carriers on one planet

|  | Source | Prediction | Result | Verdict |
|---|---|---|---|---|
| P1a | paper | From 50/50, carriers gain share in volatile and strong (F > 0.5) | volatile: 0.950 [0.850, 1.000]; strong: 1.000 [0.999, 1.000] | **Supported** |
| P1b | guess | In strong, carriers gain early and lose later | highest mean F up to generation 40: 0.956 (generation 40); endpoint 1.000 [0.999, 1.000] | **Not supported** |
| P1c | guess | F(bonus) > F(movement) in all four environments | weak: 0.384 [0.218, 0.550]; seasonal: 0.323 [0.152, 0.494]; volatile: -0.017 [-0.163, 0.102]; strong: 0.231 [0.008, 0.451] | **Not supported** |
| P1d | guess | Movement alone loses in strong (F < 0.5) | 0.719 [0.531, 0.889] | **Not supported** |

Carrier fraction F, generations 201 to 220:

| Environment | full, from 10% | full, from 50% | full, from 90% | bonus only, from 50% | movement only, from 50% |
|---|---|---|---|---|---|
| weak | 0.255 [0.115, 0.410] | 0.665 [0.497, 0.824] | 0.947 [0.906, 0.981] | 0.841 [0.731, 0.933] | 0.456 [0.321, 0.594] |
| seasonal | 0.456 [0.301, 0.615] | 0.948 [0.885, 0.995] | 0.983 [0.955, 1.000] | 0.913 [0.833, 0.975] | 0.590 [0.451, 0.726] |
| volatile | 0.947 [0.860, 0.995] | 0.950 [0.850, 1.000] | 1.000 [1.000, 1.000] | 0.845 [0.707, 0.959] | 0.863 [0.754, 0.945] |
| strong | 0.657 [0.464, 0.834] | 1.000 [0.999, 1.000] | 0.950 [0.850, 1.000] | 0.950 [0.850, 1.000] | 0.719 [0.531, 0.889] |

Carrier fraction F, generations 641 to 660:

| Environment | full, from 10% | full, from 50% | full, from 90% | bonus only, from 50% | movement only, from 50% |
|---|---|---|---|---|---|
| weak | 0.081 [0.007, 0.201] | 0.484 [0.266, 0.703] | 0.812 [0.642, 0.952] | 0.762 [0.615, 0.896] | 0.097 [0.008, 0.218] |
| seasonal | 0.218 [0.083, 0.377] | 0.875 [0.730, 1.000] | 0.926 [0.821, 1.000] | 0.926 [0.836, 0.988] | 0.272 [0.109, 0.469] |
| volatile | 0.950 [0.850, 1.000] | 0.950 [0.850, 1.000] | 1.000 [1.000, 1.000] | 0.882 [0.752, 0.993] | 0.612 [0.424, 0.795] |
| strong | 0.663 [0.462, 0.856] | 1.000 [1.000, 1.000] | 0.950 [0.850, 1.000] | 0.950 [0.850, 1.000] | 0.700 [0.501, 0.900] |

Mean carrier fraction on the way there, full arm from 50%:

| Environment | 10 | 20 | 30 | 40 | 80 | 120 | 160 | 220 | 330 | 440 | 550 | 660 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| weak | 0.633 | 0.708 | 0.689 | 0.684 | 0.699 | 0.687 | 0.676 | 0.664 | 0.633 | 0.569 | 0.518 | 0.482 |
| seasonal | 0.680 | 0.804 | 0.846 | 0.856 | 0.925 | 0.944 | 0.951 | 0.944 | 0.928 | 0.912 | 0.891 | 0.875 |
| volatile | 0.731 | 0.853 | 0.893 | 0.912 | 0.942 | 0.947 | 0.949 | 0.950 | 0.950 | 0.950 | 0.950 | 0.950 |
| strong | 0.757 | 0.879 | 0.938 | 0.956 | 0.987 | 0.995 | 0.998 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

The two types side by side, full arm from 50%, generations 201 to 220. Crowding is the number of entities sharing a patch, averaged over the entities of that type. A peak patch is one that is brighter than all eight neighbours.

| Environment | Type | Mean net energy | Mean survival | Crowding | Share on peak patches | Patches occupied |
|---|---|---|---|---|---|---|
| weak | carriers | 0.358 [0.250, 0.475] | 0.838 [0.829, 0.847] | 36.3 [30.3, 43.9] | 0.088 [0.061, 0.125] | 0.514 [0.390, 0.643] |
| weak | non-carriers | 0.536 [0.334, 0.758] | 0.909 [0.884, 0.935] | 14.8 [9.6, 19.7] | 0.005 [0.002, 0.007] | 0.438 [0.260, 0.619] |
| seasonal | carriers | 0.674 [0.559, 0.779] | 0.818 [0.808, 0.830] | 47.9 [41.4, 55.1] | 0.133 [0.099, 0.171] | 0.481 [0.373, 0.598] |
| seasonal | non-carriers | 0.957 [0.595, 1.306] | 0.934 [0.898, 0.965] | 17.0 [2.7, 35.4] | 0.013 [0.002, 0.029] | 0.100 [0.016, 0.210] |
| volatile | carriers | 0.790 [0.707, 0.857] | 0.810 [0.805, 0.816] | 54.2 [47.9, 60.7] | 0.236 [0.204, 0.269] | 0.449 [0.364, 0.539] |
| volatile | non-carriers | 0.962 [0.648, 1.243] | 0.962 [0.928, 0.980] | 5.3 [1.1, 13.4] | 0.035 [0.012, 0.059] | 0.051 [0.000, 0.150] |
| strong | carriers | 0.887 [0.829, 0.945] | 0.803 [0.799, 0.806] | 48.9 [43.8, 54.9] | 0.203 [0.168, 0.238] | 0.304 [0.244, 0.369] |
| strong | non-carriers | 0.885 [0.722, 1.123] | 0.977 [0.971, 0.980] | 1.5 [1.0, 2.0] | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.002] |

Aggregate throughput (TW). The pool allows about 136.

| Environment | mixed, 201-220 | all carriers, 201-220 | no carriers, 201-220 | mixed, 641-660 | all carriers, 641-660 | no carriers, 641-660 |
|---|---|---|---|---|---|---|
| weak | 110.9 [94.4, 126.4] | 116.5 [101.1, 129.6] | not run | 136.5 [136.3, 136.7] | 136.1 [135.2, 136.6] | not run |
| seasonal | 72.3 [55.7, 90.1] | 81.4 [62.0, 100.7] | not run | 126.9 [124.3, 129.5] | 125.1 [122.1, 128.1] | not run |
| volatile | 70.8 [59.5, 83.3] | 72.4 [63.3, 82.6] | 136.1 [135.9, 136.2] | 121.4 [118.8, 124.0] | 122.8 [120.5, 124.7] | 136.2 [136.2, 136.2] |
| strong | 43.9 [36.0, 52.3] | 47.7 [38.3, 57.8] | 134.7 [134.4, 135.0] | 108.1 [106.4, 109.6] | 108.2 [106.7, 109.9] | 135.2 [135.1, 135.3] |

## E2. Neutral markers: how far does a trait rise if it does nothing?

|  | Source | Prediction | Result | Verdict |
|---|---|---|---|---|
| P2a | review | Markers rise by at least 0.05 in each of the six scenarios | weak: +0.134; seasonal: +0.163; volatile: +0.125; strong: +0.127; volatile, no agency: +0.122; strong, no agency: +0.114 | **Supported** |
| P2b | paper | Agency is selected in strong: A − M > 0 | 0.057 [0.020, 0.093] | **Supported** |
| P2c | review | In weak, markers match at least half of the rise in agency | rise in M / rise in A = 1.32 [1.06, 1.56] | **Supported** |

Agency composite A and marker composite M, generations 201 to 220. Both start at 0.068.

| Environment | A | M | A − M | rise in M / rise in A |
|---|---|---|---|---|
| weak | 0.171 [0.158, 0.190] | 0.203 [0.194, 0.212] | -0.032 [-0.050, -0.007] | 1.32 [1.06, 1.56] |
| seasonal | 0.216 [0.190, 0.243] | 0.232 [0.204, 0.262] | -0.015 [-0.042, 0.013] | 1.11 [0.92, 1.32] |
| volatile | 0.216 [0.188, 0.248] | 0.194 [0.174, 0.216] | 0.021 [-0.017, 0.065] | 0.85 [0.63, 1.13] |
| strong | 0.255 [0.228, 0.283] | 0.198 [0.177, 0.221] | 0.057 [0.020, 0.093] | 0.69 [0.55, 0.87] |

Agency composite A and marker composite M, generations 641 to 660. Both start at 0.068.

| Environment | A | M | A − M | rise in M / rise in A |
|---|---|---|---|---|
| weak | 0.155 [0.146, 0.171] | 0.284 [0.268, 0.299] | -0.129 [-0.152, -0.099] | 2.50 [1.98, 2.97] |
| seasonal | 0.205 [0.184, 0.229] | 0.266 [0.236, 0.300] | -0.061 [-0.102, -0.019] | 1.45 [1.12, 1.84] |
| volatile | 0.192 [0.169, 0.220] | 0.214 [0.192, 0.237] | -0.022 [-0.059, 0.022] | 1.18 [0.85, 1.57] |
| strong | 0.226 [0.206, 0.246] | 0.238 [0.213, 0.264] | -0.012 [-0.048, 0.022] | 1.07 [0.86, 1.34] |

Each agency trait minus its own marker, generations 201 to 220. Above zero: pushed up by selection. Below zero: pushed down.

| Environment | sensing | processing | prediction | planning | action |
|---|---|---|---|---|---|
| weak | 0.003 [-0.047, 0.068] | 0.007 [-0.034, 0.052] | -0.011 [-0.042, 0.022] | -0.048 [-0.074, -0.022] | -0.111 [-0.140, -0.077] |
| seasonal | -0.041 [-0.116, 0.024] | -0.003 [-0.085, 0.068] | -0.047 [-0.133, 0.021] | 0.034 [-0.031, 0.108] | -0.020 [-0.065, 0.029] |
| volatile | -0.013 [-0.105, 0.090] | 0.055 [-0.016, 0.124] | 0.012 [-0.064, 0.092] | 0.018 [-0.034, 0.073] | 0.035 [-0.029, 0.097] |
| strong | 0.069 [-0.044, 0.191] | 0.048 [-0.038, 0.145] | 0.057 [-0.012, 0.130] | 0.042 [-0.055, 0.134] | 0.070 [0.005, 0.135] |

Each agency trait minus its own marker, generations 641 to 660. Above zero: pushed up by selection. Below zero: pushed down.

| Environment | sensing | processing | prediction | planning | action |
|---|---|---|---|---|---|
| weak | -0.075 [-0.132, 0.004] | -0.092 [-0.124, -0.057] | -0.121 [-0.154, -0.091] | -0.113 [-0.146, -0.082] | -0.241 [-0.276, -0.209] |
| seasonal | -0.065 [-0.122, -0.005] | -0.020 [-0.114, 0.077] | -0.007 [-0.100, 0.073] | 0.003 [-0.069, 0.076] | -0.215 [-0.267, -0.169] |
| volatile | 0.001 [-0.082, 0.093] | 0.066 [0.007, 0.122] | -0.010 [-0.103, 0.083] | 0.011 [-0.043, 0.081] | -0.177 [-0.234, -0.132] |
| strong | 0.040 [-0.050, 0.138] | 0.036 [-0.056, 0.141] | 0.045 [-0.018, 0.112] | 0.015 [-0.062, 0.088] | -0.196 [-0.245, -0.152] |

The action trait itself:

| Environment | start | 201 to 220 | 641 to 660 |
|---|---|---|---|
| weak | 0.079 | 0.082 [0.064, 0.107] | 0.044 [0.042, 0.045] |
| seasonal | 0.082 | 0.191 [0.143, 0.241] | 0.038 [0.034, 0.042] |
| volatile | 0.080 | 0.240 [0.201, 0.282] | 0.042 [0.039, 0.046] |
| strong | 0.081 | 0.261 [0.211, 0.312] | 0.035 [0.033, 0.037] |

## E3. Demography: why do populations stay small when each entity has plenty?

|  | Source | Prediction | Result | Verdict |
|---|---|---|---|---|
| P3a | review | Mean-field growth above 1.10 with agency, below 1.06 without | volatile: 1.166; strong: 1.172; volatile, no agency: 1.027; strong, no agency: 1.033 | **Supported** |
| P3b | guess | The gap is inequality, not a transient: realised growth within 0.99 to 1.01, and more entities below the survival threshold with agency (strong) | realised growth: volatile 0.9989, strong 0.9987; difference in share below threshold: 0.206 [0.190, 0.222] | **Supported** |
| P3c | review, doubted | Entity-weighted crowding is lower with agency than without (strong) | with minus without: -31.3 [-39.5, -24.2] | **Supported** |
| P3d | review | At 641 to 660 the contrast still holds in both pairs: throughput lower, per entity higher | volatile: -13.5 [-15.7, -11.5] TW, +13.4 [12.9, 13.9] GW; strong: -27.0 [-28.5, -25.4] TW, +16.2 [15.7, 16.7] GW | **Supported** |
| P3e | review | Carriers pick the truly best neighbour at least 80% of the time in generations 0 to 20 | weak: 0.953; seasonal: 0.974; volatile: 0.990; strong: 0.985 | **Supported** |

On P3c, Claude's guess before the runs was that the review's claim would fail. At 641 to 660 the same difference is 31.0 [24.3, 37.1].

Checked, not predicted: the controls capture 0.993 [0.992, 0.994] (volatile, no agency) and 0.984 [0.981, 0.986] (strong, no agency) of the resource pool at the endpoint.

Where the energy goes, generations 201 to 220. Net energy is in model units. The survival threshold is 0.05.

| Scenario | Mean net | 10th pct | Median | 90th pct | Share below threshold | Mean-field growth | Mean survival + births | Realised growth |
|---|---|---|---|---|---|---|---|---|
| weak | 0.347 [0.240, 0.463] | -0.025 [-0.098, 0.041] | 0.244 [0.206, 0.289] | 0.862 [0.491, 1.265] | 0.129 [0.084, 0.178] | 1.067 [1.038, 1.097] | 1.000 [0.999, 1.001] | 0.9994 [0.9974, 1.0014] |
| seasonal | 0.649 [0.509, 0.780] | -0.195 [-0.235, -0.156] | 0.329 [0.301, 0.357] | 1.958 [1.476, 2.425] | 0.260 [0.228, 0.289] | 1.137 [1.113, 1.159] | 0.996 [0.992, 1.000] | 0.9981 [0.9939, 1.0022] |
| volatile | 0.782 [0.701, 0.851] | -0.254 [-0.277, -0.227] | 0.398 [0.377, 0.415] | 2.374 [2.091, 2.625] | 0.293 [0.277, 0.304] | 1.166 [1.155, 1.173] | 0.999 [0.997, 1.001] | 0.9989 [0.9962, 1.0014] |
| strong | 0.856 [0.791, 0.916] | -0.194 [-0.218, -0.168] | 0.319 [0.304, 0.334] | 2.714 [2.479, 2.931] | 0.310 [0.300, 0.321] | 1.172 [1.170, 1.174] | 0.997 [0.993, 1.001] | 0.9987 [0.9970, 1.0002] |
| volatile, no agency | 0.187 [0.185, 0.188] | 0.037 [0.023, 0.049] | 0.190 [0.186, 0.193] | 0.322 [0.315, 0.329] | 0.068 [0.062, 0.074] | 1.027 [1.026, 1.029] | 0.998 [0.998, 0.999] | 0.9980 [0.9978, 0.9983] |
| strong, no agency | 0.194 [0.190, 0.198] | -0.068 [-0.089, -0.049] | 0.225 [0.218, 0.232] | 0.353 [0.337, 0.369] | 0.104 [0.096, 0.113] | 1.033 [1.030, 1.037] | 0.996 [0.995, 0.998] | 0.9980 [0.9974, 0.9984] |

Where the entities are, generations 201 to 220:

| Scenario | Population | Patches occupied | Per occupied patch | Crowding, entity-weighted | Share of population in the fullest 5% of patches | Share on peak patches |
|---|---|---|---|---|---|---|
| weak | 6377 [5106, 7560] | 0.849 [0.731, 0.951] | 18.3 [16.1, 20.3] | 35.4 [27.7, 45.0] | 0.206 [0.134, 0.289] | 0.050 [0.033, 0.071] |
| seasonal | 3474 [2246, 4768] | 0.584 [0.442, 0.730] | 13.1 [11.1, 15.4] | 55.1 [45.6, 65.8] | 0.470 [0.366, 0.572] | 0.135 [0.090, 0.183] |
| volatile | 2224 [1730, 2916] | 0.511 [0.442, 0.589] | 10.7 [9.9, 11.9] | 59.4 [52.5, 66.7] | 0.495 [0.447, 0.538] | 0.222 [0.195, 0.252] |
| strong | 1345 [993, 1742] | 0.336 [0.262, 0.415] | 10.0 [9.6, 10.5] | 52.0 [46.1, 58.9] | 0.665 [0.601, 0.725] | 0.198 [0.160, 0.237] |
| volatile, no agency | 8580 [8445, 8723] | 0.990 [0.989, 0.992] | 22.6 [22.2, 23.0] | 40.4 [36.6, 44.5] | 0.107 [0.102, 0.112] | 0.060 [0.060, 0.061] |
| strong, no agency | 8659 [8497, 8814] | 0.962 [0.959, 0.964] | 23.5 [23.0, 23.9] | 83.3 [77.2, 90.0] | 0.168 [0.161, 0.176] | 0.023 [0.022, 0.024] |

The headline numbers, generations 201 to 220:

| Scenario | Throughput (TW) | Per entity (GW) | Share of pool captured | Agency | Action | Cooperation | Technology |
|---|---|---|---|---|---|---|---|
| weak | 116.5 [101.5, 129.9] | 21.9 [18.5, 25.7] | 0.861 [0.757, 0.953] | 0.171 [0.158, 0.189] | 0.082 [0.064, 0.107] | 0.739 [0.676, 0.803] | 0.707 [0.675, 0.737] |
| seasonal | 81.4 [61.5, 100.6] | 31.9 [27.3, 36.3] | 0.615 [0.470, 0.756] | 0.216 [0.190, 0.243] | 0.191 [0.143, 0.243] | 0.811 [0.754, 0.865] | 0.684 [0.641, 0.727] |
| volatile | 72.4 [63.2, 82.4] | 36.1 [33.3, 38.5] | 0.562 [0.496, 0.635] | 0.216 [0.188, 0.249] | 0.240 [0.201, 0.282] | 0.852 [0.805, 0.889] | 0.636 [0.597, 0.676] |
| strong | 47.7 [38.5, 58.0] | 38.4 [36.2, 40.5] | 0.375 [0.305, 0.452] | 0.255 [0.228, 0.282] | 0.261 [0.213, 0.311] | 0.825 [0.759, 0.882] | 0.607 [0.559, 0.657] |
| volatile, no agency | 136.1 [135.9, 136.2] | 15.9 [15.6, 16.1] | 0.993 [0.992, 0.994] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.597 [0.543, 0.650] | 0.625 [0.580, 0.666] |
| strong, no agency | 134.7 [134.4, 135.0] | 15.6 [15.3, 15.9] | 0.984 [0.981, 0.986] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.500 [0.442, 0.558] | 0.524 [0.474, 0.574] |

Where the energy goes, generations 641 to 660. Net energy is in model units. The survival threshold is 0.05.

| Scenario | Mean net | 10th pct | Median | 90th pct | Share below threshold | Mean-field growth | Mean survival + births | Realised growth |
|---|---|---|---|---|---|---|---|---|
| weak | 0.196 [0.180, 0.226] | 0.057 [0.012, 0.084] | 0.200 [0.181, 0.233] | 0.324 [0.277, 0.407] | 0.060 [0.050, 0.077] | 1.028 [1.019, 1.043] | 1.002 [1.000, 1.005] | 1.0012 [1.0000, 1.0030] |
| seasonal | 0.493 [0.419, 0.559] | -0.291 [-0.322, -0.255] | 0.412 [0.377, 0.444] | 1.341 [1.095, 1.565] | 0.242 [0.217, 0.264] | 1.137 [1.117, 1.154] | 1.000 [0.998, 1.002] | 0.9998 [0.9991, 1.0004] |
| volatile | 0.564 [0.551, 0.576] | -0.329 [-0.335, -0.324] | 0.469 [0.463, 0.475] | 1.539 [1.497, 1.580] | 0.269 [0.266, 0.271] | 1.160 [1.159, 1.161] | 1.001 [1.000, 1.002] | 1.0007 [1.0002, 1.0013] |
| strong | 0.666 [0.653, 0.679] | -0.317 [-0.326, -0.310] | 0.380 [0.374, 0.388] | 1.983 [1.935, 2.028] | 0.273 [0.270, 0.275] | 1.167 [1.166, 1.168] | 1.000 [0.999, 1.001] | 0.9995 [0.9990, 1.0001] |
| volatile, no agency | 0.186 [0.185, 0.186] | 0.049 [0.040, 0.058] | 0.189 [0.186, 0.191] | 0.312 [0.309, 0.315] | 0.061 [0.058, 0.064] | 1.026 [1.025, 1.027] | 1.000 [0.999, 1.000] | 1.0000 [0.9999, 1.0001] |
| strong, no agency | 0.197 [0.193, 0.202] | -0.058 [-0.074, -0.042] | 0.228 [0.222, 0.235] | 0.357 [0.342, 0.373] | 0.098 [0.091, 0.105] | 1.036 [1.032, 1.039] | 1.000 [1.000, 1.001] | 0.9999 [0.9997, 1.0001] |

Where the entities are, generations 641 to 660:

| Scenario | Population | Patches occupied | Per occupied patch | Crowding, entity-weighted | Share of population in the fullest 5% of patches | Share on peak patches |
|---|---|---|---|---|---|---|
| weak | 8314 [7891, 8573] | 0.995 [0.986, 1.000] | 21.7 [20.7, 22.3] | 30.0 [26.7, 35.1] | 0.103 [0.092, 0.121] | 0.033 [0.032, 0.035] |
| seasonal | 4959 [4328, 5643] | 0.898 [0.875, 0.921] | 14.2 [12.8, 15.8] | 106.3 [97.8, 114.2] | 0.315 [0.281, 0.345] | 0.036 [0.034, 0.039] |
| volatile | 4228 [4091, 4362] | 0.890 [0.866, 0.910] | 12.4 [12.2, 12.6] | 116.6 [112.3, 121.0] | 0.351 [0.345, 0.356] | 0.096 [0.091, 0.101] |
| strong | 3346 [3262, 3436] | 0.773 [0.761, 0.786] | 11.3 [11.1, 11.5] | 108.2 [105.1, 111.5] | 0.407 [0.403, 0.412] | 0.053 [0.048, 0.058] |
| volatile, no agency | 8666 [8649, 8683] | 0.996 [0.995, 0.996] | 22.7 [22.6, 22.7] | 37.4 [34.5, 40.5] | 0.102 [0.099, 0.106] | 0.064 [0.063, 0.065] |
| strong, no agency | 8374 [8304, 8440] | 0.970 [0.969, 0.972] | 22.5 [22.3, 22.7] | 77.2 [72.3, 82.4] | 0.161 [0.154, 0.168] | 0.022 [0.022, 0.023] |

The headline numbers, generations 641 to 660:

| Scenario | Throughput (TW) | Per entity (GW) | Share of pool captured | Agency | Action | Cooperation | Technology |
|---|---|---|---|---|---|---|---|
| weak | 136.1 [135.2, 136.6] | 16.6 [15.9, 17.8] | 0.998 [0.993, 1.000] | 0.155 [0.146, 0.171] | 0.044 [0.042, 0.045] | 0.879 [0.875, 0.883] | 0.834 [0.826, 0.842] |
| seasonal | 125.1 [122.2, 128.1] | 26.9 [24.5, 29.2] | 0.940 [0.923, 0.958] | 0.205 [0.183, 0.229] | 0.038 [0.034, 0.042] | 0.893 [0.879, 0.906] | 0.775 [0.741, 0.809] |
| volatile | 122.8 [120.5, 124.8] | 29.1 [28.6, 29.6] | 0.929 [0.914, 0.942] | 0.192 [0.169, 0.221] | 0.042 [0.038, 0.047] | 0.902 [0.887, 0.915] | 0.729 [0.689, 0.769] |
| strong | 108.2 [106.7, 109.8] | 32.4 [31.9, 32.9] | 0.832 [0.821, 0.843] | 0.226 [0.207, 0.246] | 0.035 [0.033, 0.037] | 0.896 [0.874, 0.914] | 0.715 [0.680, 0.751] |
| volatile, no agency | 136.2 [136.2, 136.2] | 15.7 [15.7, 15.8] | 0.998 [0.998, 0.998] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.868 [0.867, 0.869] | 0.842 [0.840, 0.844] |
| strong, no agency | 135.2 [135.1, 135.3] | 16.2 [16.1, 16.3] | 0.995 [0.994, 0.995] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.861 [0.857, 0.864] | 0.833 [0.829, 0.836] |
