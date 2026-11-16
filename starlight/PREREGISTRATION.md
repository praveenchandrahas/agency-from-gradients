# Starlight: predictions, written before the runs

Written on 2026-11-16, before any evolving run at these settings.
The file's SHA-256 and timestamp are recorded in `results/RUN_INFO.txt` at run time.

## The hypothesis, as a chain

1. Free energy flows from a star into space.
2. Structures that feed on that flow appear and persist. Life is one.
3. Such structures evolve to capture more of the flow.
4. The behaviour that captures more is what we call agency or intelligence.
5. Why? More capture means more entropy produced, and the Universe statistically favours that.

Links 1 and 2 are prior art. This model assumes them. It starts with copiers already present.

Links 3 and 4 are tested here.

Link 5 is the weak one. Physics has no law that says entropy production is maximised.
So the model does not assume it. It asks a narrower question:
**is entropy production what gets selected, or is it a side effect of what gets selected?**

## The world

A ring of 256 sites. Four patches of light fall on it.
Light that no organism absorbs escapes, undegraded. Absorbed light ends up as heat.

Organisms absorb light, pay running costs, split in two at energy 2, and die by starvation or by a constant hazard.
Children copy their parent's traits with small mutations.

There is no fitness function. Nothing rewards capture, heat or entropy. Selection is by persistence alone.

Four heritable traits, each with a cost:

| Trait | What it does | Cost per step |
|---|---|---|
| `a` absorber | captures light, shared with neighbours by shading | 0.05 a² |
| `m` motility | chance of moving one site | 0.02 per move |
| `g` sensing | chance that a move goes up the light gradient | 0.01 g |
| `f` furnace | absorbs a second band of light and makes heat. Nothing else. | 0 or 0.01 f |

## What is true by construction

I should say this before any result.

- **Capture and entropy production are the same number here.** Every unit captured becomes heat. Uncaptured light escapes undegraded. So "more capture" equals "more entropy" by bookkeeping, not by discovery.
- **The lifeless world is a perfect mirror.** Real bare rock absorbs most sunlight and makes heat anyway. This model gives life the most headroom it could have. It is the friendly case for the hypothesis.
- **Sensing is hand-shaped.** `g` is a ready-made gradient sensor with a dial. Evolution tunes it. Evolution does not invent it.
- **Copying is given.** Where the first copier comes from is not asked.

## Measurements

- **Capture fraction C**: light absorbed in the usable band, divided by light emitted. Mean over the last 5,000 steps.
- **Trait means** over living organisms, same window.
- **Directed-move rate**: sensed, deliberate moves per organism per step.
- Extinct worlds count as C = 0. Their traits are undefined and are left out, with the count reported.
- 20 seeds per cell (0 to 19). 95% bootstrap intervals on seed means, 10,000 resamples.
- The energy ledger must close at every step of every run, or the run is void.

## E1. Does persistence selection raise capture?

Static light. Only `a` mutates. Two starts: far too small (0.08) and far too big (2.0).
A grid of frozen-`a` controls maps the capture curve the world allows.

A back-of-envelope argument says selection should settle where cost per unit of absorber is lowest:
`a* = sqrt((c_base + hazard × mean energy) / c_abs)`, roughly 0.8.
The same value should also maximise total capture. That is a prediction, not a certainty: the argument assumes dense crowding, and patch edges are not dense.

| | Prediction | Fails if |
|---|---|---|
| **P1a** | Both starts converge. Late `a` differs by less than 0.15 between them | Interval of the difference leaves ±0.15 |
| **P1b** | Late `a` lies within 25% of `a*`, with mean energy measured from the runs | Outside that band |
| **P1c** | Capture rises from both starts: evolved C exceeds frozen C at the same start | Either interval includes zero |
| **P1d** | Evolved C is within 0.02 of the best frozen-`a` C | Gap larger than 0.02 |

## E2. Does behaviour evolve, and only when needed?

The patches accelerate from rest to a final speed `v` over the first 20,000 steps, then hold.
Every organism starts with no behaviour: `m = g = 0`.
Three arms: only `a` can mutate; `a` and `m`; `a`, `m` and `g`.
Speeds: 0, 0.1, 0.2, 0.3, 0.5, 0.8 sites per step.

| | Prediction | Fails if |
|---|---|---|
| **P2a** | Moving evolves with speed: late `m` at v = 0.3 exceeds late `m` at v = 0 (arm `am`) | Interval includes zero |
| **P2b** | Sensing evolves with speed: late directed-move rate at v = 0.5 exceeds that at v = 0 (arm `amg`) | Interval includes zero, or `amg` is extinct at 0.5 in most seeds |
| **P2c** | Moving buys capture: at v = 0.3, C(`am`) exceeds C(`a`) | Interval includes zero |
| **P2d** | Sensing buys capture: at v = 0.5, C(`amg`) exceeds C(`am`) | Interval includes zero |
| **P2e** | Unneeded behaviour is not kept: at v = 0, late `g` is below 0.25 and below late `g` at v = 0.5 | Either fails |

No prediction at v = 0.8. I expect extinction there but do not know.

## E3. The furnace: is entropy itself selected?

Static light, plus a second band that only the furnace absorbs.
`a` and `f` mutate. Every population starts at `f = 0.5`, mid-range, so drift has no built-in direction.

A population that keeps its furnace roughly doubles its entropy production. It gains nothing else.

If link 5 is read literally, the furnace should spread.
If persistence is the only thing selected, it should not.

| | Prediction | Fails if |
|---|---|---|
| **P3a** | Costly furnace is purged: late `f` below 0.15 | Mean or upper bound above 0.15 |
| **P3b** | Free furnace only drifts: late `f` not different from 0.5 | Interval excludes 0.5 |

**This is a control, not a discovery.** In a world where energy feeds copying and nothing else does, the outcome follows from the rules. Its job is to stop E1 being misread as "entropy was maximised".

## Pilots and what they changed

Pilots used seed 1000 and **frozen traits only**. No evolving run was looked at before this file was written. Unit tests do run short evolving worlds, for mechanics only.

What the pilots showed:

- The frozen-`a` capture curve is flat-topped near 0.93 for `a` between 0.5 and 0.8. It falls to 0.56 at 0.08 and 0.81 at 2.0. Below `a = 0.05` the population dies.
- Frozen sessile populations die once patches move at 0.2 or faster.
- Frozen blind movers (`m` = 0.5) survive to 0.3 and die at 0.5.
- Frozen perfect climbers (`m = g = 1`) capture only about 0.15 at every speed. They pile onto the peak and waste the flanks. A half-climber (`m` = 0.5, `g` = 1) reaches 0.53 at v = 0.5.

Changes made after pilots: the E1 starts (0.08 and 2.0), the E2 speed grid and the E2 start `a0 = 0.65` were chosen from these curves. No cost, rate or rule was changed.

## Deviation log

(empty at freeze)
