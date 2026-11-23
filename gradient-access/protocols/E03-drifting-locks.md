# E03 — Drifting gradients

## Question
Can evolutionary adaptation sustain access when catalytic targets change over time?

## Factor
Per-time target-bit flip hazard; converted to a per-step probability using the integration interval. The exploratory map uses slow, medium and fast drift rates of 0.005, 0.02 and 0.05 per residence-time unit over a 100-unit horizon.

## Outcomes
Late-window throughput, cumulative dissipation, key–target distance, adaptation lag, extinction and time spent below a declared accessibility threshold.

## Controls
M and D experience the same target history as L. Paired seeds must share the same initial target and drift sequence. Report the full distribution of target changes, not only the mean.

## Interpretation
An intermediate drift window may favour evolution; very rapid drift may outrun adaptation. Neither outcome is assumed.
