# Planet: predictions, written before the runs

Written on 2026-11-16, before any run of the experiments below.
The file's SHA-256 and a timestamp are recorded in `results/RUN_INFO.txt` at run time.

## Why this folder exists

The paper "Energy Capture, Agency, and Planetary Entropy" reports a spatial model, v0.2.
Its code lives in `dissipative-agency-simulation`. It is copied here unchanged, as `planet/v0_2.py`.

A consistency review of the paper left three gaps open.

1. **Individual advantage was never shown between individuals.** Agency carriers and non-carriers lived on separate planets. They never competed.
2. **There was no neutral baseline.** Agency traits rose from 0.07 to about 0.2. Nobody measured how far a trait that does nothing would rise.
3. **The headline state did not follow from the stated rules.** High energy per entity should mean growth. The populations stayed small.

This folder closes the three gaps. One experiment each.

Predictions marked **paper** restate what the paper's reading needs to be true.
Predictions marked **review** come from the review.
Predictions marked **guess** are Claude's own guesses, written here before the runs, with the confidence stated.

## What had been seen when this was written

- The paper, its tables and figures.
- The three summary CSVs in `dissipative-agency-simulation/results/`.
- The v0.2 source code.
- Unit tests. They run short worlds (60 generations or fewer) for mechanics only, mixed worlds included. Two published runs were repeated in full to check bit-for-bit equality. Their numbers were compared with the published ones and nothing else.
- A smoke run of both experiment scripts: 30 generations, two replicates. Only file shapes were looked at.

No mixed-world outcome, no marker value and no net-energy distribution had been looked at.

## What reading the code already settles

Five facts. None is in the paper.

1. **There is no hidden loss term.** Survival, births and a ceiling of 20,000 are the only demographic rules. The ceiling is never near. So one of the review's three explanations for gap 3 is already out.
2. **Growth is additive.** Next population = survivors + births = N × (mean survival + birth rate).
3. **The scored field ignores crowding.** A carrier moves toward the neighbouring patch with the most absorbed starlight. It does not look at who is already there.
4. **Sensing noise is small in the field's own units.** The noise is about 0.42. The field is about 240 W/m² and neighbouring patches differ by several W/m². So sensing, processing and prediction should barely change where a carrier goes. This is tested as P3e.
5. **The review used too small a number.** Equation 4 pays agency in proportion to the spread of light across the whole grid. That spread includes the equator-to-pole gradient. It is about 0.28 even in the "weakly variable" scenario. The review assumed 0.05 to 0.1 there, and called agency "roughly break-even". With 0.28, the stipulated benefit is about two to three times the cost at a trait value of 0.2. P2c tests whether the review's conclusion survives its own arithmetic error.

## What is true by construction

- **The controls sit at the ceiling.** The resource pool is fixed at 0.1% of absorbed power. The paper's own numbers show the controls capture about 99% of it. Agency can tie or lose on aggregate throughput. It cannot win.
- **The entropy diagnostic is a function of global albedo alone.** Nothing here adds to that.
- **Equation 4 is a stipulation.** It pays agency traits directly, in every environment where light is uneven.
- **Markers are fully linked to the rest of the genome.** There is no recombination. A marker can hitch a ride on a successful lineage. That is the right null: same lineages, same number of mutations, same clipping.

## Design

- 20 replicates per cell, numbered 0 to 19. Replicates 0 to 5 use the paper's seeds.
- 660 generations. The first 220 of every pure run equal the paper's run, bit for bit.
- **Endpoint**: the mean over generations 201 to 220. That is the paper's endpoint, smoothed over 20 generations. A second endpoint, 641 to 660, is reported beside it.
- 95% bootstrap intervals on replicate means, 10,000 resamples.
- A world that goes extinct is counted and reported. Its trait values are left out.

## E1. Competition: do carriers beat non-carriers on the same planet?

Each entity carries a heritable flag. Carriers follow the cognition-enabled rules. Non-carriers follow the cognition-disabled rules. The flag does not mutate.
Both types start with the same collector, cooperation and technology values.

**F** is the fraction of carriers at the endpoint.

Three arms:

- **full**: carriers get the Equation 4 bonus and directed movement. Starts at 10%, 50% and 90% carriers.
- **bonus**: carriers get the Equation 4 bonus only. They move at random. Starts at 50%.
- **movement**: carriers get directed movement only. No bonus. Starts at 50%.

| | Source | Prediction | Fails if |
|---|---|---|---|
| **P1a** | paper | From a 50/50 start, carriers gain share in the volatile and strong environments: F > 0.5 | Either interval includes 0.5 or lies below it |
| **P1b** | guess, low confidence | In the strong environment carriers gain early and lose later: mean F passes 0.5 at some generation up to 40, and F < 0.5 at the endpoint | Either half fails |
| **P1c** | guess, moderate confidence | The stipulated bonus does the work, the modelled movement does not: F(bonus) > F(movement) in all four environments | Any interval of the difference includes zero |
| **P1d** | guess, moderate confidence | Directed movement alone loses in the strong environment: F(movement) < 0.5 | Interval includes 0.5 or lies above it |

No prediction for the 10% and 90% starts. They are reported, to show whether the outcome depends on who is common.

Also reported, without a prediction: the aggregate throughput of every mixed world, beside the pure worlds.
If carriers take over and throughput falls, that is the paper's counterexample inside one world. If non-carriers take over, the paper's premise fails.

## E2. Neutral markers: how far does a trait rise if it does nothing?

Every entity carries five markers. They start with the same means and spread as the five agency traits.
They mutate with the same step and clip at 0 and 1 the same way. They cost nothing and do nothing.

The runs are the six published scenarios, unchanged.

**A** is the agency composite. **M** is the marker composite. Both at the endpoint, in the same run.

| | Source | Prediction | Fails if |
|---|---|---|---|
| **P2a** | review | Mutation and clipping alone lift a trait: M rises by at least 0.05 from its start, in each of the six scenarios | Mean rise below 0.05 in any scenario |
| **P2b** | paper | Agency is selected in the strong environment: A − M > 0 | Interval includes zero |
| **P2c** | review | In the weakly variable environment, at least half of the rise in agency is matched by the markers: (rise in M) / (rise in A) ≥ 0.5 | Interval lies entirely below 0.5 |

The ratio in P2c is reported for all four environments.
Given fact 5 above, P2c is less safe than the review made it sound.

## E3. Demography: why do populations stay small when each entity has plenty?

Same runs as E2.

**Mean-field growth** is what the review computed: survival at the mean net energy, plus the birth rate.
**Realised growth** is what happened: the 50-generation geometric mean of N(t+1)/N(t).
**Entity-weighted crowding** is the number of entities sharing a patch, averaged over entities. It answers "how crowded is it where a typical entity lives?"

| | Source | Prediction | Fails if |
|---|---|---|---|
| **P3a** | review | The mean does not describe a steady state. In cognition-enabled volatile and strong, mean-field growth exceeds 1.10. In the two controls it is below 1.06 | Any of the four is on the wrong side |
| **P3b** | guess, moderate confidence | The gap is inequality, not a transient. Realised growth to generation 220 lies between 0.99 and 1.01 in cognition-enabled volatile and strong. And the share of entities below the survival threshold is higher in cognition-enabled strong than in its control | Realised growth outside the band, or the interval of the difference in shares includes zero |
| **P3c** | review, now doubted | The review said cognition-enabled populations are sparser, not crowded. It compared ratios of means: 10 per occupied patch against 22. The fair measure is entity-weighted. The review holds if entity-weighted crowding is lower in cognition-enabled strong than in its control | Difference is zero or positive |
| **P3d** | review | The headline contrast outlasts the paper's endpoint. At 641 to 660, aggregate throughput is still lower and throughput per entity still higher in both cognition-enabled worlds than in their controls | Any of the four intervals of the difference includes zero |
| **P3e** | review | Sensing barely matters to movement. In generations 0 to 20, when sensing is near 0.08, carriers still pick the truly best neighbour at least 80% of the time, in all four environments. A blind pick would be 11% | Below 0.80 in any environment |

On P3c: after reading the movement rule (fact 3), Claude's guess is that the review's claim **fails**. Carriers pile onto a few bright patches. Low to moderate confidence.

Checked, not predicted, because the paper's numbers already imply it: the two controls capture at least 97% of the resource pool at the endpoint.

## Deviation log

(empty at freeze)
