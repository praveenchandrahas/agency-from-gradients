# Roadmap

## Completed: executable exploratory suite

- Reversible lock kinetics with barrier-dependent catalysis.
- Passive, fixed random, faithful-copying, evolving, oracle-search and designer arms.
- Paired-seed initial libraries for D and L.
- Matched-size Mmatched, Amatched and Umatched controls.
- Static, slow/medium/fast drift and multi-lock experiments.
- Independent reaction and fuel-exchange entropy diagnostics.
- Construction, reproduction, maintenance, mutation and adaptive-search cost records.
- Automated tests, paired bootstrap summaries, compressed trajectories and plots.

## In progress: v0.2 thermodynamically coupled prototype

- Added a reversible fuel-to-work reaction, explicit ATP/ADP-like currency, autocatalytic replication, mutation kernel and maintenance hydrolysis.
- Added fuel/waste and monomer/polymer exchange entropy terms.
- Derived all reaction affinities from one standard-potential ledger.
- Added a differential free-energy identity check for the declared reactor boundary.
- Added BDF integration without clipping and analytic validation tests.
- Prototype assumptions and limits are documented in [MODEL_V02_IMPLEMENTATION.md](MODEL_V02_IMPLEMENTATION.md).

This prototype remains abstract and deterministic. The pleiotropic assumption that genotype-dependent catalytic efficiency also affects self-replication must be stress-tested. The deterministic parameter grid is implemented in `analysis/run_v02_pilot.py`; its dedicated workflow uploads an artifact for analysis. It is not a confirmatory result.

## Next: scientific validation (blocking; v0.1 findings are provisional)

The v0.1 audit found omitted reproduction expenditure, an uncoupled reproductive energy proxy, incomplete binary-mixture exchange entropy and a control-matching ambiguity. The prior energetic-cost comparison is invalid until these are corrected. See [VALIDATION_AUDIT.md](VALIDATION_AUDIT.md) and the proposed [MODEL_V02_DESIGN.md](MODEL_V02_DESIGN.md).



1. Derive a full multicomponent fuel/waste/reservoir ledger from explicit stoichiometry and chemical potentials.
2. Eliminate clipping in production runs and demonstrate conservation residuals across the complete parameter grid.
3. Compare explicit Euler with a higher-order integration scheme and test step-size convergence at the long horizon.
4. Add equal cumulative-investment comparisons, not only equal catalyst abundance.
5. Sweep key lengths, mutation rates, mismatch scales, population caps and smooth/rugged/epistatic landscapes.
6. Test longer horizons and multiple initial genotype libraries.
7. Freeze primary outcomes, parameter ranges and falsifiers before confirmatory experiments.

## Interpretation rule

Do not infer a universal thermodynamic law from a toy-model result. Distinguish the advantage of selection on standing variation, ongoing mutation, generic adaptive search and ideal design. A null or negative result is a valid outcome.
