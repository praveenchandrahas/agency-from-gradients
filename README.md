# Thermodynamic Emergence

**From cosmic energy flows to dissipative organization, life and intelligence.**

This repository investigates whether — and under what conditions — persistent planetary free-energy flows can support increasingly organized dissipative structures, and whether self-maintenance, replication, information processing and agency can emerge as contingent developments within those systems.

This is a **research hypothesis**, not an established consequence of the second law. The project does not assume that entropy maximization is an evolutionary objective, that life or intelligence is inevitable, or that greater energy capture necessarily means greater entropy production.

## Central research question

Can persistent planetary free-energy flows give rise to increasingly organized dissipative structures, and under what conditions can these structures evolve information processing, agency and intelligence as mechanisms for exploiting those flows?

A companion question asks how such structures alter energy capture, transformation and dissipation at planetary scale.

## Research principles

1. Separate thermodynamic law from proposed organizing principles.
2. Keep energy, exergy, fitness, throughput and entropy production distinct.
3. Do not build the conclusion into the model. Planetary entropy production is an outcome to measure, not a fitness bonus.
4. Model dissipative organization, self-maintenance, replication, evolution and agency as separate explanatory steps.
5. Use controls, null models and competing hypotheses.
6. Treat inevitability as an open question; prefer conditional, probabilistic claims.

## Research programme

| Stage | Question |
|---|---|
| I. Thermodynamic environment | What energy and exergy flows, gradients and boundary conditions are present? |
| II. Dissipative organization | Which structures can form and persist under sustained flows? |
| III. Replication and evolution | Under what conditions can heritable replication arise and selection operate? |
| IV. Agency | When can sensing, memory, prediction and action evolve despite their costs? |
| V. Planetary consequences | How do these systems alter energy transformation and entropy production? |

## Research documents

- [Research charter](RESEARCH_CHARTER.md) — governing question, propositions and scientific boundaries.
- [Hypotheses](HYPOTHESES.md) — candidate hypotheses, predictions, nulls and proposed tests.
- [Roadmap](ROADMAP.md) — staged research and modelling plan.
- [Thermodynamic foundation: star–planet–space](theory/01-stellar-planetary-thermodynamics.md) — first energy, exergy and entropy accounting.
- [Initial bibliography](references/README.md) — starting literature and reading priorities.\n- [Local chemical disequilibrium](theory/04-local-chemical-disequilibrium.md) — first single-autocatalyst model.\n- [Collective autocatalysis](theory/05-collective-autocatalysis.md) — finite-resource mutually catalytic RAF-like model.
- [Contributing](CONTRIBUTING.md) — standards for research contributions.

## First executable model

The first model is a transparent zero-dimensional stellar–planetary ledger. It calculates intercepted, reflected, absorbed and emitted power; an approximate Petela solar-exergy estimate; and spectrally integrated Planck radiation-entropy fluxes under explicit Lambertian-reflection and graybody-emission assumptions. It deliberately does not model climate, chemistry, life or agency.

- [Model guide and run instructions](models/stellar_planet/README.md)
- [Source code](src/thermodynamic_emergence/model.py)
- [Earth-like baseline output](results/earth_like_baseline.json)
- [Albedo sensitivity data](results/albedo_sensitivity.csv)

Run locally with python -m pip install -e . followed by python -m thermodynamic_emergence.

## Second executable model: finite-resource mutual catalysis\n\nA second chemical model represents a small RAF-like network with food set {A, B}, reciprocal catalysts X and Y, finite food resources, explicit stoichiometry and reversible loss pathways. It compares finite-time conversion against an uncatalysed null. Catalysis accelerates kinetics but does not change equilibrium composition; the closed batch relaxes toward equilibrium and does not sustain a non-equilibrium steady state.\n\n- [Model and assumptions](theory/05-collective-autocatalysis.md)\n- [Experiment protocol](experiments/protocols/02-raf-batch-network.md)\n- Run: `raf-network --compare`\n\n## Relationship to the earlier simulation

The related repository [dissipative-agency-simulation](https://github.com/praveenchandrahas/dissipative-agency-simulation) investigates evolutionary energy-acquisition strategies in populations of already-existing entities. Its experiments on sensing, movement, competition and agency remain useful as a downstream research line.

It does **not** model the origin of life or spontaneous emergence of replicators. This repository provides the broader thermodynamic research framework; it does not replace or erase that work.

## Current status

**Phase: research foundations.** The immediate priority is to clarify definitions, formulate competing hypotheses, establish thermodynamic accounting and identify what the literature already supports. No claim of a validated new theory or completed origin-of-life model is being made.

## Contributing

Contributions should state a question or claim, assumptions, evidence, limitations and a way to test or challenge the claim. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

To be selected once the intended reuse and contribution model are decided.
