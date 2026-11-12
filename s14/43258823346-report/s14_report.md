# S14 results

runs: R=800, N=800, P=10, M=10, C=200

## Gates (all must pass, or nothing below is reported as a result)

- Gate 1 detailed balance (closed box): PASS
- Gate 3a detailed-balance identity: PASS
- Gate 2 ledgers (mass, fuel exact; free-energy books to 1e-6): PASS
- Gate 3b flux entropy production agrees with the books in the controls (5%): PASS
- Gate 3c entropy production is not negative in any late window (z > -4): PASS
- Gate 4 no drive, no structure: PASS
- Gate 5 detector: P fires in 10/10 (need >= 8 of 10), M in 0/10 (need <= 2 of 10): PASS
  - closed box, drive 0: dimers 73.8 vs equilibrium 70.8; late entropy production z = 0.30
  - closed box, drive 8: dimers 74.0 vs equilibrium 70.8; late entropy production z = -0.10
  - detailed-balance identity, worst error: 2.02e-11
  - no drive: mean polymer fraction minus equilibrium = -0.00892 (max run -0.00032)

**All gates pass: YES**

## Arms (late window; mean [95% bootstrap interval])

| arm | drive | runs | capture | entropy rate (k_B per residence time) | polymer fraction | E rate | closure alone |
|---|---|---|---|---|---|---|---|
| R | 0 | 200 | 0.0000 [0.0000, 0.0000] | 24.2 [22.1, 26.5] | 0.0002 [0.0002, 0.0003] | 0.000 | 0.000 |
| R | 4 | 200 | 0.0003 [0.0003, 0.0004] | 200.9 [198.6, 203.2] | 0.0002 [0.0002, 0.0003] | 0.000 | 0.000 |
| R | 8 | 200 | 0.0005 [0.0004, 0.0006] | 286.6 [283.9, 289.3] | 0.0002 [0.0002, 0.0003] | 0.000 | 0.000 |
| R | 12 | 200 | 0.0004 [0.0004, 0.0005] | 370.5 [368.1, 373.1] | 0.0002 [0.0002, 0.0003] | 0.000 | 0.000 |
| N | 0 | 200 | 0.0000 [0.0000, 0.0000] | 24.1 [22.0, 26.4] | 0.0002 [0.0002, 0.0003] | 0.000 | 0.000 |
| N | 4 | 200 | 0.0003 [0.0003, 0.0003] | 200.6 [198.4, 203.0] | 0.0002 [0.0002, 0.0003] | 0.000 | 0.000 |
| N | 8 | 200 | 0.0004 [0.0004, 0.0004] | 285.0 [282.7, 287.5] | 0.0002 [0.0002, 0.0003] | 0.000 | 0.000 |
| N | 12 | 200 | 0.0004 [0.0004, 0.0004] | 368.9 [366.5, 371.4] | 0.0002 [0.0002, 0.0003] | 0.000 | 0.000 |
| C | 12 | 200 | 0.0004 [0.0004, 0.0005] | 371.7 [369.1, 374.4] | 0.0003 [0.0002, 0.0003] | 0.000 | 0.000 |
| P | 12 | 10 | 0.6114 [0.6107, 0.6122] | 8070.0 [8060.7, 8080.0] | 0.6852 [0.6841, 0.6860] | 1.000 | 1.000 |
| M | 12 | 10 | 0.5856 [0.5841, 0.5870] | 8077.4 [8067.7, 8087.1] | 0.6512 [0.6504, 0.6521] | 0.000 | 0.000 |

## Preregistered hypotheses

- **H14a** copying appears. E rate in arm R at the top drive: 0.000 [0.000, 0.000] (0 of 200 chemistries). Lower bound above 0.05: NOT supported. Against 0.01: no; against 0.10: no.
- **H14b** more drive, more copying. E rate at drive 12 minus at drive 4, paired by chemistry: 0.000 [0.000, 0.000] -> NOT supported.
- **H14c**, **H14d**: NOT RUN. Only 0 arm-R runs met the emergence criterion (fewer than 5).

## Sensitivity of the emergence criterion (arm R, top drive)

- as registered: 0 of 200
- activity cut-offs halved: 0 of 200
- activity cut-offs doubled: 0 of 200
- twin fraction 0.25: 0 of 200
- twin fraction 1.0: 0 of 200
- lag 5 residence times: 0 of 200
- lag 20 residence times: 0 of 200
- closure alone: 0 of 200

## Descriptive (not preregistered as tests)

- Chemistries where a closed set is possible at all (structural, from the catalysis table): 0 of 200; of those, 0 include a fuel-coupled join.
- Arm R, drive 0: closure in 0, E in 0 of 200.
- Arm R, drive 4: closure in 0, E in 0 of 200.
- Arm R, drive 8: closure in 0, E in 0 of 200.
- Arm R, drive 12: closure in 0, E in 0 of 200.
- Exploratory, day/night feed (arm C, period 10, same mean, same chemistries as arm R at the top drive): E in 0 of 200 under cycling against 0 under a steady feed; closure alone 0 against 0.
- Arm P: twin lag (residence times, censored at 100) [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]; mean q 0.964; mean capture 0.611.
- Arm M: twin lag (residence times, censored at 100) [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; mean q 0.494; mean capture 0.586.
