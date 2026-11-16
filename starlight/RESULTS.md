# Starlight: results

Every number below is computed by `analysis/report.py` from the CSVs in `results/`. Intervals are 95% bootstrap intervals on seed means. Predictions are in `PREREGISTRATION.md`.

## E1. Does persistence selection raise capture?

| | Prediction | Result | Verdict |
|---|---|---|---|
| P1a | Both starts converge on the same absorber size | start-high minus start-low: 0.005 [-0.004, 0.014]. Late `a`: 0.818 [0.811, 0.825] from 0.08, 0.823 [0.817, 0.829] from 2.0 | **Supported** |
| P1b | Late `a` within 25% of the predicted a* | a* = 0.797 (mean energy 1.178); evolved 0.821 [0.816, 0.825]; ratio 1.03 | **Supported** |
| P1c | Capture rises from both starts | from 0.08: +0.372 [0.371, 0.373]; from 2.0: +0.122 [0.120, 0.125] | **Supported** |
| P1d | Evolved capture within 0.02 of the best frozen value | best frozen: a = 0.65, C = 0.934. Evolved minus best: -0.003 [-0.004, -0.002] and -0.003 [-0.003, -0.002] | **Supported** |

Frozen-absorber capture curve (10 seeds each):

| a | 0.08 | 0.2 | 0.35 | 0.5 | 0.65 | 0.8 | 1 | 1.3 | 2 |
|---|---|---|---|---|---|---|---|---|---|
| C | 0.560 | 0.862 | 0.918 | 0.932 | 0.934 | 0.933 | 0.926 | 0.906 | 0.810 |

Evolved capture: 0.931 [0.931, 0.932] from the low start, 0.932 [0.931, 0.932] from the high start.

## E3. The furnace: is entropy itself selected?

| | Prediction | Result | Verdict |
|---|---|---|---|
| P3a | Costly furnace is purged (late `f` < 0.15) | 0.130 [0.126, 0.135] | **Supported** |
| P3b | Free furnace only drifts (late `f` not different from 0.5) | 0.496 [0.471, 0.523] | **Supported** |

What that did to the heat output (energy per step, late window):

| Arm | Heat from living | Heat from furnace | Furnace band captured | Usable band captured | Late `a` |
|---|---|---|---|---|---|
| free | 111.9 | 103.4 | 0.861 [0.853, 0.870] | 0.932 [0.931, 0.932] | 0.821 [0.817, 0.826] |
| costly | 111.6 | 71.7 | 0.597 [0.589, 0.604] | 0.930 [0.929, 0.930] | 0.837 [0.831, 0.843] |

## E2. Does behaviour evolve, and only when needed?

| | Prediction | Result | Verdict |
|---|---|---|---|
| P2a | Moving evolves with speed (`m` at 0.3 minus `m` at 0, arm `am`) | +0.799 [0.793, 0.806] | **Supported** |
| P2b | Sensing evolves with speed (directed-move rate at 0.5 minus at 0, arm `amg`) | +0.541 [0.541, 0.542]; 0 of 20 extinct at 0.5 | **Supported** |
| P2c | Moving buys capture at v = 0.3 (`am` minus `a`) | 0.810 [0.777, 0.843] | **Supported** |
| P2d | Sensing buys capture at v = 0.5 (`amg` minus `am`) | 0.547 [0.546, 0.547] | **Supported** |
| P2e | Unneeded sensing is not kept (`g` at 0 below 0.25, and below `g` at 0.5) | at 0: 0.102 [0.099, 0.104]; at 0.5: 0.713 [0.704, 0.723]; difference 0.612 [0.602, 0.622] | **Supported** |

Capture fraction C:

| arm | v = 0 | v = 0.1 | v = 0.2 | v = 0.3 | v = 0.5 | v = 0.8 |
|---|---|---|---|---|---|---|
| `a` | 0.932 [0.932, 0.933] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| `am` | 0.940 [0.940, 0.941] | 0.929 [0.929, 0.929] | 0.897 [0.896, 0.898] | 0.810 [0.776, 0.843] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| `amg` | 0.935 [0.935, 0.936] | 0.916 [0.915, 0.917] | 0.876 [0.874, 0.878] | 0.792 [0.784, 0.799] | 0.547 [0.546, 0.547] | 0.532 [0.532, 0.532] |

Extinct worlds (of 20):

| arm | v = 0 | v = 0.1 | v = 0.2 | v = 0.3 | v = 0.5 | v = 0.8 |
|---|---|---|---|---|---|---|
| `a` | 0 | 20 | 20 | 20 | 20 | 20 |
| `am` | 0 | 0 | 0 | 0 | 20 | 20 |
| `amg` | 0 | 0 | 0 | 0 | 0 | 0 |

Late motility m:

| arm | v = 0 | v = 0.1 | v = 0.2 | v = 0.3 | v = 0.5 | v = 0.8 |
|---|---|---|---|---|---|---|
| `am` | 0.058 [0.057, 0.058] | 0.462 [0.455, 0.470] | 0.820 [0.814, 0.825] | 0.857 [0.850, 0.863] | all extinct | all extinct |
| `amg` | 0.060 [0.059, 0.061] | 0.465 [0.454, 0.476] | 0.812 [0.802, 0.822] | 0.818 [0.810, 0.826] | 0.790 [0.780, 0.801] | 0.888 [0.886, 0.890] |

Late sensing g:

| arm | v = 0 | v = 0.1 | v = 0.2 | v = 0.3 | v = 0.5 | v = 0.8 |
|---|---|---|---|---|---|---|
| `amg` | 0.102 [0.100, 0.104] | 0.066 [0.065, 0.067] | 0.071 [0.069, 0.073] | 0.183 [0.170, 0.196] | 0.713 [0.704, 0.723] | 0.917 [0.914, 0.919] |

Directed moves per organism per step:

| arm | v = 0 | v = 0.1 | v = 0.2 | v = 0.3 | v = 0.5 | v = 0.8 |
|---|---|---|---|---|---|---|
| `am` | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| `amg` | 0.006 [0.006, 0.006] | 0.030 [0.030, 0.031] | 0.058 [0.056, 0.059] | 0.131 [0.124, 0.140] | 0.547 [0.547, 0.548] | 0.812 [0.811, 0.812] |

Late absorber a:

| arm | v = 0 | v = 0.1 | v = 0.2 | v = 0.3 | v = 0.5 | v = 0.8 |
|---|---|---|---|---|---|---|
| `a` | 0.814 [0.809, 0.819] | all extinct | all extinct | all extinct | all extinct | all extinct |
| `am` | 0.809 [0.805, 0.812] | 0.973 [0.967, 0.978] | 1.106 [1.099, 1.114] | 1.258 [1.236, 1.287] | all extinct | all extinct |
| `amg` | 0.812 [0.808, 0.815] | 0.981 [0.972, 0.991] | 1.138 [1.120, 1.154] | 1.190 [1.170, 1.211] | 0.971 [0.964, 0.978] | 1.020 [1.012, 1.028] |

## Not preregistered: things the runs showed that I did not predict

These were looked at after the fact. Treat them as leads, not findings.

- At v = 0.1, allowing sensing changed capture by -0.013 [-0.014, -0.012] (`amg` minus `am`).
- At v = 0.2, allowing sensing changed capture by -0.021 [-0.023, -0.020] (`amg` minus `am`).
- At v = 0.3, allowing sensing changed capture by -0.018 [-0.049, 0.019] (`amg` minus `am`).
- So where sensing was optional, the lineages that could sense captured slightly *less*. Selection did not maximise capture there. The cause is not established: it could be the running cost of the sensor, or crowding on the bright sites.
- Total heat per step: 111.9 with no furnace band (E1), 215.3 with a free furnace, 183.3 with a costly one. Selection gave up 32.0 units of entropy-producing heat per step to save a running cost of 0.01 per unit of furnace.
- The frozen perfect climber captured about 0.15 in the pilots. The evolved populations at v = 0.8 captured 0.53. Their directed-move rate settled just above the patch speed (0.81 against 0.8): fast enough to keep up, not so fast that everyone piles onto the peak.

