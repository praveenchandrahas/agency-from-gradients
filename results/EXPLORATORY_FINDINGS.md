> **Additional trajectory qualification:** A further trajectory audit found that D/L populations reach the 500-catalyst cap within one or two integration steps in nearly all runs. There are 200 trajectories per arm (400 D/L trajectories total). Across all barriers and designs, 80% of D and 80% of L trajectories are already at or above 400 catalysts after the first step; all D and L trajectories are at or above 400 after the second step. At the highest barrier (12 kT), 100% of D and 80% of L runs are at or above 400 after the second step. This means the configured reproductive costs do not produce a meaningful resource-limited growth regime over most of the tested grid. The late-window results therefore describe near-capacity populations, not persistence under a tight energy budget. This is an additional reason not to interpret v0.1 as a test of energy-limited evolutionary access.


> **Validation status (2026-11-23):** A subsequent code audit found that reproduction expenditure is not accumulated in the investment ledger, the reproductive energy proxy is not the actual reaction free-energy release and is not coupled through an explicit work-producing reaction, and the fuel-exchange entropy omits the complementary waste species. Dmatched is also only initial-abundance-matched, not population-trajectory-matched. Therefore the throughput outputs remain exploratory model results, but the energetic-cost and complete-entropy interpretations are not validated. See [VALIDATION_AUDIT.md](../VALIDATION_AUDIT.md). Do not cite this report as evidence of an advantage at comparable total energetic investment until a corrected model passes the validation gates.

# Exploratory findings — long-horizon 16-bit run

**Run:** GitHub Actions run 45132922728  
**Artifact:** `ega-long-horizon-key16-results`  
**Design:** 10 paired seeds × 5 environment designs × 4 barriers × 10 arms = 2,000 simulation runs.  
**Horizon:** 100 residence-time units, 300 integration steps, 16-bit keys.  
**Uncertainty:** paired-seed bootstrap percentile intervals (95%, 5,000 resamples).

This is an exploratory result from the current abstract model. It is not a preregistered confirmatory experiment and does not establish a real-world thermodynamic law.

## Validation checks

- All 12 unit tests passed in the workflow.
- The zero-barrier control is exact in this implementation: across every paired seed and design, the range of late throughput and cumulative implemented entropy across all ten arms is zero.
- Environmental drift histories are identical across arms within every paired design/barrier/seed group. The drift process uses an independent random-number stream.
- Maximum absolute fuel-balance residual across the 2,000 runs: approximately (3.82\times10^{-14}).
- No negative values were found in the implemented reaction, fuel-exchange or combined entropy-production diagnostics.
- No D, L or Dmatched population extinctions occurred. N is the deliberately catalyst-free baseline, not an extinct population.

These checks validate specific numerical invariants. They do not validate the full thermodynamic boundary: waste-reservoir exchange, heat transfer, pumping, catalyst chemistry and apparatus costs remain outside the model. See [MODEL_LIMITATIONS.md](../MODEL_LIMITATIONS.md).

## What the comparisons show

### 1. Evolving populations beat fixed random catalyst libraries

L exceeds Mmatched in late-window throughput and cumulative implemented entropy at barriers 4, 8 and 12 kT across all five environment designs; the paired 95% intervals are positive.

Mmatched is a fixed random catalyst library initialized at the same catalyst abundance as the paired L run's late-window mean. This is the clearest result in the current model: selection, reproduction and ongoing variation together outperform a static random library at matched catalyst abundance.

### 2. The advantage over faithful copying depends on the control

D begins from the same 80-member random library as L and reproduces faithfully without new mutation. L outperforms D in the static and slow-drift, one-lock experiments across the tested cold barriers. The advantage weakens as drift becomes faster; in the three-lock experiment, L−D intervals generally include zero.

Dmatched is the stronger control. It begins with a random standing library sized to L's late-window abundance, can reproduce and select, but cannot create new mutations. L does **not** robustly outperform Dmatched in the static or slow-drift experiments: the paired intervals include zero at the tested barriers. A positive L−Dmatched result appears at the highest barrier under medium drift, but this is one conditional region, not a general pattern. In the fast-drift and multi-lock designs, Dmatched is competitive and sometimes has a higher mean.

This distinction matters. The current results do not establish that ongoing mutation is generally superior to a sufficiently large initial pool of heritable variation followed by selection.

### 3. Generic adaptive search is a meaningful competitor

A and Amatched are oracle-assisted search controls: they evaluate candidate keys directly against the model's target landscape and pay a declared candidate-evaluation cost.

L tends to outperform Amatched in static and slow-drift one-lock conditions on late throughput, but cumulative-entropy intervals are less consistently separated. Under fast drift and multiple locks, Amatched is competitive or better. Because A has privileged target information and an abstract cost model, this is an algorithmic comparison, not a physical non-living chemistry result.

### 4. The ideal designer remains an upper bound

Umatched uses target-matched catalysts at L's late-window abundance. It outperforms L throughout the tested conditions. This is expected: the experiment does not claim evolution can outperform an ideal externally specified solution.

### 5. The advantage is conditional, not monotonic or universal

The strongest signal appears in static and slow-drift, one-lock environments. The advantage narrows under medium and fast drift and is not established in the three-lock environment. The current drift map contains only three rates, and the multi-lock model is still highly simplified.

## Interpretation

The evidence supports this limited statement:

> In this bit-string flow-reactor model, evolving populations can outperform fixed random catalyst libraries, and can outperform a faithful-copying population that starts from the same small library in static and slowly drifting one-lock environments.

It does **not** yet support the stronger statement that ongoing mutation and selection reliably outperform a large standing library of non-mutating replicators at comparable total energetic investment. Dmatched is specifically designed to test that alternative, and it is not consistently beaten.

The results therefore point to a more precise next question: under what combinations of landscape ruggedness, barrier height, environmental drift, population size and mutation/maintenance cost does ongoing variation outperform selection on standing variation?

## Important qualifications

1. Catalyst count is matched for Mmatched, Dmatched, Amatched and Umatched, but total investment is not exactly equalized. The separate cost ledger is a first step, not a complete physical energy budget.
2. The adaptive control has oracle access to target scores.
3. The key–lock mapping is a chosen abstraction; robustness across alternative genotype–phenotype landscapes remains untested.
4. Replication and mutation are algorithmic population operations. The model does not explain the origin of replicators or represent validated prebiotic chemistry.
5. The entropy diagnostic includes reaction and fuel-reservoir exchange terms only. It is not the complete entropy production of an organism, reactor or planet.
6. No inference about inevitability of life, intelligence or agency follows.

## Reproducibility

The artifact contains:

- `replicates.csv` — per-run outcomes and declared investment costs.
- `summary.json` — per-arm means and bootstrap intervals.
- `paired_contrasts.json` — paired L-minus-control contrasts.
- `trajectories.jsonl.gz` — complete compressed trajectories and exact shared drift events.
- `manifest.json` — run design and parameters.
- `figures/` — paired contrast plots.

The artifact is available from [GitHub Actions run 45132922728](https://github.com/praveenchandrahas/evolutionary-gradient-access/actions/runs/45132922728).
