# Contributing

Contributions should identify the hypothesis, causal mechanism, system boundary, control, primary outcome, assumptions and falsifier.

## Scientific requirements
- Do not put entropy production into fitness.
- Preserve paired seeds and matched forcing.
- Add tests for equilibrium, detailed balance, conservation and non-negative entropy production when changing kinetics.
- Distinguish rate quantities from integrated quantities.
- Report all negative and null outcomes.
- Do not describe a toy-model result as an empirical finding.

## Code requirements
- Keep simulation parameters in explicit configuration objects.
- Save seeds, parameters, source revision and output metadata.
- Add deterministic tests for analytic limits.
- Avoid opaque post-processing and undocumented parameter tuning.
