> **Generated.** Everything below the line is written by `analysis/report.py` from CI run [45129057522](https://github.com/praveenchandrahas/agency-from-gradients/actions/runs/45129057522), commit `1fb3aa4`, preregistration SHA-256 `277201cd…5df7`. Raw runs: `ci-results` branch, `s15/45129057522/runs.tar.gz` (1,696 files). Plain-language reading: [`docs/results/s15.md`](../docs/results/s15.md).

---

# S15, Locks: results

Computed by `analysis/report.py` from the run files. Predictions and decision rules: `PREREGISTRATION.md`.
Intervals are 95% bootstrap intervals on seed means (10,000 resamples), paired by seed.
Entropy production σ is in k_B per residence time: reactions plus mixing.
Primary window: residence times 3,500 to 4,000. Secondary: 1,500 to 2,000.

## Key length 24

### Verdicts, primary window

**Overall: life does better, but something else also opens the lock: 'nothing else does' fails.**

| | Test | Result | Verdict |
|---|---|---|---|
| H1 | D − N and L − N at B = 16, above 0 | 923.1 [875.7, 971.8]; 1185.4 [1184.6, 1186.2] | Supported |
| H2a | L − M and L − D at B = 16, above 0 | 895.8 [889.0, 902.4]; 262.4 [213.5, 310.7] | Supported |
| H2b | Slope over B of L − max(M, D), above 0 | 19.60 [15.48, 23.76] per kT | Supported |
| H2c | At B = 0, M, D, L within ±2% of N | M 0.0000 [0.0000, 0.0000]; D 0.0000 [0.0000, 0.0000]; L 0.0000 [0.0000, 0.0000] | Supported |
| H2d | L − U never above 0 | largest at B = 0: 0.0 [0.0, 0.0] | Supported |
| H2e | At B = 16, D/U and M/U below 0.10 | D 0.778 [0.739, 0.819] (not supported); M 0.244 [0.239, 0.250] (not supported) | Not supported |

### Verdicts, secondary window

**Overall: life does better, but something else also opens the lock: 'nothing else does' fails.**

| | Test | Result | Verdict |
|---|---|---|---|
| H1 | D − N and L − N at B = 16, above 0 | 923.9 [875.8, 971.8]; 1184.4 [1183.6, 1185.2] | Supported |
| H2a | L − M and L − D at B = 16, above 0 | 894.7 [887.9, 901.4]; 260.4 [212.5, 308.6] | Supported |
| H2b | Slope over B of L − max(M, D), above 0 | 19.54 [15.32, 23.76] per kT | Supported |
| H2c | At B = 0, M, D, L within ±2% of N | M 0.0000 [0.0000, 0.0000]; D 0.0000 [0.0000, 0.0000]; L 0.0000 [0.0000, 0.0000] | Supported |
| H2d | L − U never above 0 | largest at B = 10: 0.0 [-0.7, 0.7] | Supported |
| H2e | At B = 16, D/U and M/U below 0.10 | D 0.779 [0.739, 0.820] (not supported); M 0.244 [0.239, 0.250] (not supported) | Not supported |

### σ by arm and barrier, primary window

| arm | B = 0 | B = 2 | B = 4 | B = 6 | B = 8 | B = 10 | B = 12 | B = 16 |
|---|---|---|---|---|---|---|---|---|
| N | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 333 [333, 333] | 65 [65, 65] | 10 [10, 10] | 1 [1, 1] | 0 [0, 0] |
| M | 1192 [1192, 1192] | 1160 [1160, 1160] | 910 [909, 910] | 490 [486, 494] | 323 [316, 329] | 294 [287, 301] | 290 [283, 297] | 290 [283, 297] |
| D | 1192 [1192, 1192] | 1160 [1160, 1160] | 955 [926, 990] | 922 [873, 971] | 923 [875, 970] | 923 [875, 971] | 924 [876, 972] | 923 [875, 971] |
| L | 1192 [1192, 1192] | 1160 [1160, 1160] | 1028 [971, 1085] | 1185 [1185, 1186] | 1185 [1185, 1186] | 1185 [1185, 1186] | 1185 [1184, 1186] | 1185 [1185, 1186] |
| U | 1192 [1192, 1192] | 1160 [1160, 1160] | 1171 [1171, 1171] | 1186 [1186, 1186] | 1186 [1186, 1186] | 1186 [1186, 1186] | 1186 [1186, 1186] | 1186 [1186, 1186] |

### σ by arm and barrier, secondary window

| arm | B = 0 | B = 2 | B = 4 | B = 6 | B = 8 | B = 10 | B = 12 | B = 16 |
|---|---|---|---|---|---|---|---|---|
| N | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 333 [333, 333] | 65 [65, 65] | 10 [10, 10] | 1 [1, 1] | 0 [0, 0] |
| M | 1192 [1192, 1192] | 1160 [1160, 1160] | 910 [909, 910] | 490 [486, 494] | 323 [316, 329] | 294 [287, 301] | 290 [283, 297] | 290 [283, 297] |
| D | 1192 [1192, 1192] | 1160 [1160, 1160] | 955 [924, 991] | 923 [875, 971] | 924 [875, 973] | 923 [875, 971] | 924 [876, 972] | 924 [876, 971] |
| L | 1192 [1192, 1192] | 1160 [1160, 1160] | 1028 [970, 1085] | 1185 [1185, 1186] | 1185 [1185, 1186] | 1186 [1185, 1186] | 1185 [1185, 1186] | 1184 [1184, 1185] |
| U | 1192 [1192, 1192] | 1160 [1160, 1160] | 1171 [1171, 1171] | 1186 [1186, 1186] | 1186 [1186, 1186] | 1186 [1186, 1186] | 1186 [1186, 1186] | 1186 [1186, 1186] |

### Fuel spent, primary window

| arm | B = 0 | B = 2 | B = 4 | B = 6 | B = 8 | B = 10 | B = 12 | B = 16 |
|---|---|---|---|---|---|---|---|---|
| N | 0.987 | 0.929 | 0.646 | 0.199 | 0.032 | 0.005 | 0.001 | 0.000 |
| M | 0.987 | 0.929 | 0.656 | 0.309 | 0.191 | 0.172 | 0.170 | 0.169 |
| D | 0.987 | 0.929 | 0.702 | 0.673 | 0.674 | 0.674 | 0.674 | 0.674 |
| L | 0.987 | 0.929 | 0.792 | 0.971 | 0.971 | 0.971 | 0.971 | 0.971 |
| U | 0.987 | 0.929 | 0.946 | 0.972 | 0.972 | 0.972 | 0.972 | 0.972 |

### Catalyst count, primary window

| arm | B = 0 | B = 2 | B = 4 | B = 6 | B = 8 | B = 10 | B = 12 | B = 16 |
|---|---|---|---|---|---|---|---|---|
| D | 0 | 0 | 115 | 480 | 543 | 551 | 553 | 553 |
| L | 0 | 0 | 166 | 386 | 388 | 389 | 389 | 390 |
| M | 0 | 0 | 166 | 386 | 388 | 389 | 389 | 390 |

### R1. Extinct worlds (of seeds run)

| arm | B = 0 | B = 2 | B = 4 | B = 6 | B = 8 | B = 10 | B = 12 | B = 16 |
|---|---|---|---|---|---|---|---|---|
| D | 20 of 20 | 20 of 20 | 12 of 20 | 0 of 20 | 0 of 20 | 0 of 20 | 0 of 20 | 0 of 20 |
| L | 20 of 20 | 20 of 20 | 11 of 20 | 0 of 20 | 0 of 20 | 0 of 20 | 0 of 20 | 0 of 20 |

### R2. Key against neutral marker, arm L, end of run

Mean Hamming distance to the lock (key) and to a random fixed target (marker). Marker drift is the neutral baseline.

| B | key distance | marker distance | marker − key |
|---|---|---|---|
| 0 | extinct | extinct | n/a |
| 2 | extinct | extinct | n/a |
| 4 | 0.03 | 11.65 | 11.63 [9.89, 13.40] |
| 6 | 0.02 | 11.92 | 11.90 [10.96, 12.78] |
| 8 | 0.02 | 11.99 | 11.97 [11.04, 12.79] |
| 10 | 0.03 | 11.46 | 11.43 [10.57, 12.28] |
| 12 | 0.03 | 11.82 | 11.80 [10.68, 12.84] |
| 16 | 0.03 | 12.10 | 12.07 [11.01, 13.10] |

### Equivalent library at B = 16 (secondary)

Mineral arms with 1x, 10x and 100x the matched count, against L.

| arm | σ | σ − L |
|---|---|---|
| M | 290 [283, 296] | -896 [-903, -889] |
| M10 | 927 [924, 930] | -259 [-262, -256] |
| M100 | 1174 [1174, 1174] | -12 [-12, -11] |

## Key length 32

### Verdicts, primary window

**Overall: life does better, but something else also opens the lock: 'nothing else does' fails.**

| | Test | Result | Verdict |
|---|---|---|---|
| H1 | D − N and L − N at B = 16, above 0 | 168.0 [71.7, 278.5]; 770.5 [533.2, 1007.6] | Supported |
| H2a | L − M and L − D at B = 16, above 0 | 726.3 [487.2, 964.0]; 602.5 [383.6, 817.4] | Supported |
| H2b | Slope over B of L − max(M, D), above 0 | 47.61 [32.83, 61.68] per kT | Supported |
| H2c | At B = 0, M, D, L within ±2% of N | M 0.0000 [0.0000, 0.0000]; D 0.0000 [0.0000, 0.0000]; L 0.0000 [0.0000, 0.0000] | Supported |
| H2d | L − U never above 0 | largest at B = 0: 0.0 [0.0, 0.0] | Supported |
| H2e | At B = 16, D/U and M/U below 0.10 | D 0.142 [0.060, 0.237] (inconclusive); M 0.038 [0.035, 0.040] (supported) | Not supported |

### Verdicts, secondary window

**Overall: life does better, but something else also opens the lock: 'nothing else does' fails.**

| | Test | Result | Verdict |
|---|---|---|---|
| H1 | D − N and L − N at B = 16, above 0 | 167.9 [72.0, 277.3]; 760.7 [522.0, 996.3] | Supported |
| H2a | L − M and L − D at B = 16, above 0 | 716.5 [476.0, 953.0]; 592.8 [382.0, 803.1] | Supported |
| H2b | Slope over B of L − max(M, D), above 0 | 45.41 [31.45, 58.71] per kT | Supported |
| H2c | At B = 0, M, D, L within ±2% of N | M 0.0000 [0.0000, 0.0000]; D 0.0000 [0.0000, 0.0000]; L 0.0000 [0.0000, 0.0000] | Supported |
| H2d | L − U never above 0 | largest at B = 0: 0.0 [0.0, 0.0] | Supported |
| H2e | At B = 16, D/U and M/U below 0.10 | D 0.142 [0.062, 0.236] (inconclusive); M 0.038 [0.035, 0.040] (supported) | Not supported |

### σ by arm and barrier, primary window

| arm | B = 0 | B = 2 | B = 4 | B = 6 | B = 8 | B = 10 | B = 12 | B = 16 |
|---|---|---|---|---|---|---|---|---|
| N | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 333 [333, 333] | 65 [65, 65] | 10 [10, 10] | 1 [1, 1] | 0 [0, 0] |
| M | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 341 [340, 341] | 87 [86, 89] | 40 [38, 42] | 52 [49, 54] | 44 [42, 47] |
| D | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 382 [333, 430] | 195 [108, 298] | 161 [64, 274] | 165 [67, 276] | 168 [73, 279] |
| L | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 546 [418, 716] | 513 [289, 738] | 539 [304, 774] | 889 [652, 1068] | 771 [533, 1008] |
| U | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 1144 [1144, 1144] | 1166 [1166, 1166] | 1170 [1170, 1170] | 1182 [1182, 1182] | 1179 [1179, 1179] |

### σ by arm and barrier, secondary window

| arm | B = 0 | B = 2 | B = 4 | B = 6 | B = 8 | B = 10 | B = 12 | B = 16 |
|---|---|---|---|---|---|---|---|---|
| N | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 333 [333, 333] | 65 [65, 65] | 10 [10, 10] | 1 [1, 1] | 0 [0, 0] |
| M | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 341 [340, 341] | 87 [86, 89] | 40 [38, 42] | 52 [49, 54] | 44 [42, 47] |
| D | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 382 [333, 431] | 196 [108, 298] | 161 [64, 273] | 165 [68, 275] | 168 [72, 278] |
| L | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 546 [418, 717] | 513 [289, 737] | 535 [300, 772] | 815 [577, 1028] | 761 [520, 997] |
| U | 1192 [1192, 1192] | 1160 [1160, 1160] | 899 [899, 899] | 1144 [1144, 1144] | 1166 [1166, 1166] | 1170 [1170, 1170] | 1182 [1182, 1182] | 1179 [1179, 1179] |

### Fuel spent, primary window

| arm | B = 0 | B = 2 | B = 4 | B = 6 | B = 8 | B = 10 | B = 12 | B = 16 |
|---|---|---|---|---|---|---|---|---|
| N | 0.987 | 0.929 | 0.646 | 0.199 | 0.032 | 0.005 | 0.001 | 0.000 |
| M | 0.987 | 0.929 | 0.646 | 0.204 | 0.045 | 0.019 | 0.025 | 0.022 |
| D | 0.987 | 0.929 | 0.646 | 0.234 | 0.119 | 0.102 | 0.104 | 0.106 |
| L | 0.987 | 0.929 | 0.646 | 0.392 | 0.408 | 0.440 | 0.728 | 0.631 |
| U | 0.987 | 0.929 | 0.646 | 0.907 | 0.938 | 0.944 | 0.964 | 0.960 |

### Catalyst count, primary window

| arm | B = 0 | B = 2 | B = 4 | B = 6 | B = 8 | B = 10 | B = 12 | B = 16 |
|---|---|---|---|---|---|---|---|---|
| D | 0 | 0 | 0 | 44 | 93 | 103 | 111 | 114 |
| L | 0 | 0 | 0 | 97 | 156 | 176 | 292 | 254 |
| M | 0 | 0 | 0 | 97 | 156 | 176 | 292 | 254 |

### R1. Extinct worlds (of seeds run)

| arm | B = 0 | B = 2 | B = 4 | B = 6 | B = 8 | B = 10 | B = 12 | B = 16 |
|---|---|---|---|---|---|---|---|---|
| D | 20 of 20 | 20 of 20 | 20 of 20 | 17 of 20 | 14 of 20 | 11 of 20 | 7 of 20 | 5 of 20 |
| L | 20 of 20 | 20 of 20 | 20 of 20 | 15 of 20 | 12 of 20 | 11 of 20 | 5 of 20 | 7 of 20 |

### R2. Key against neutral marker, arm L, end of run

Mean Hamming distance to the lock (key) and to a random fixed target (marker). Marker drift is the neutral baseline.

| B | key distance | marker distance | marker − key |
|---|---|---|---|
| 0 | extinct | extinct | n/a |
| 2 | extinct | extinct | n/a |
| 4 | extinct | extinct | n/a |
| 6 | 0.03 | 16.51 | 16.48 [14.21, 18.79] |
| 8 | 0.04 | 16.68 | 16.64 [14.58, 18.73] |
| 10 | 0.03 | 15.90 | 15.86 [14.16, 17.31] |
| 12 | 0.03 | 15.12 | 15.08 [13.74, 16.41] |
| 16 | 0.04 | 16.29 | 16.25 [14.38, 18.01] |

### Equivalent library at B = 16 (secondary)

Mineral arms with 1x, 10x and 100x the matched count, against L.

| arm | σ | σ − L |
|---|---|---|
| M | 44 [42, 47] | -726 [-964, -487] |
| M10 | 319 [314, 323] | -452 [-691, -212] |
| M100 | 952 [950, 953] | 181 [-57, 420] |

