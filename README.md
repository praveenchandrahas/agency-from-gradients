# Evolutionary Gradient Access

Computational experiments investigating whether heritable variation and natural selection enable evolving systems to access and sustain dissipative pathways that passive and non-evolving structures cannot exploit at comparable energetic and material costs.

**This is a model-based research programme, not an established thermodynamic law.** The project studies evolutionary search and catalytic gradient access. It does not claim that life is uniquely capable of dissipation, that entropy production is a fitness objective, or that life and intelligence are inevitable.

## Governing hypothesis

> In sufficiently constrained environments containing kinetically inaccessible free-energy gradients, systems with heritable variation and selection can sustain access to dissipative pathways that passive and non-evolving dissipative structures cannot access at comparable energetic and material costs.

The subject is **evolutionary advantage**, not a unique property of life.

## Experimental arms

- **N:** uncatalysed passive baseline.
- **M:** fixed random catalyst library.
- **D:** self-maintaining catalytic population with faithful inheritance and no new mutation; selection can sort standing variation.
- **L:** heritable variation and selection.
- **U:** ideal designer benchmark with target-matched catalysts.
- **A:** bounded, oracle-assisted non-replicating adaptive search control.
- **Mmatched:** fixed random catalyst library matched to L's late-window population size.
- **Amatched:** adaptive-search control matched to L's late-window population size.
- **Umatched:** ideal target-matched catalyst population at L's late-window population size.

D and L begin from the same random key library under paired seeds. Catalysts multiply forward and reverse reaction rates equally; they do not change the equilibrium constant. Selection uses usable chemical free energy after declared costs. Entropy production is recorded independently and is never included in fitness.

## First executable model

The initial implementation is an abstract flow-reactor model with configurable activation barriers, catalyst key landscapes, mutation, environmental drift and multiple locks. It is deliberately coarse and does not represent validated prebiotic chemistry.

Install and run:

```bash
python -m pip install -e ".[dev]"
pytest -q
ega-run --out results/matched-key16 --seeds 10 --steps 300
```

The current runner executes E01 (static locks), E03 (drifting locks) and E04 (multiple locks), using 16-bit keys. It includes matched-size Mmatched, Amatched and Umatched controls, with each fixed control matched to the paired L run's late-window population. A is an oracle-assisted adaptive-search control. Cumulative dissipation is reported from the same trajectories.

## Interpretation limits

1. A positive result supports only a conditional mechanism in this model.
2. The bit-string key/lock landscape is a modelling choice; sensitivity to geometry is required.
3. The population algorithm assumes replicators already exist. It does not model abiogenesis.
4. The energy and entropy accounting is provisional and requires analytic and numerical validation before confirmatory claims.
5. Initial runs are exploratory; no confirmatory preregistration has yet been frozen.
6. The model does not include complete reactor engineering costs, spatial transport or finite-molecule stochastic extinction.

## Research standards

- Measure entropy production; never reward it through fitness.
- Keep throughput, free-energy consumption, entropy production, stored energy and reproductive success distinct.
- Use paired seeds, matched resource boundaries and uncertainty estimates.
- Report extinction and negative outcomes.
- Treat controls as causal comparisons, not decorative baselines.

See [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md), [HYPOTHESES.md](HYPOTHESES.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md) and [MODEL_LIMITATIONS.md](MODEL_LIMITATIONS.md).
