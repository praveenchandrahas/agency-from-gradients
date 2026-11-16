# Research roadmap

**Current phase:** Foundations and problem formulation.

**Guiding rule:** Do not build the next simulation until the question, system boundary, state variables, mechanisms and measurable outcomes are specified.

## Phase 0 — Establish scientific foundations

**Objective:** Define the language and physical framework.

Work:
- Define system boundaries: star, planet, atmosphere, surface, subsurface, biosphere and radiative sink.
- Distinguish energy, exergy/free energy, entropy, entropy flow and entropy production.
- Establish a consistent reference environment for exergy calculations.
- Review non-equilibrium thermodynamics, dissipative structures, origin-of-life research, autocatalytic chemistry, information theory and evolutionary theory.
- Map competing interpretations, including maximum entropy production and maximum power hypotheses, without assuming either is universally valid.

Deliverables: a glossary with operational definitions; a thermodynamic accounting note; a literature map separating established theory, active debate and speculative proposals; and a list of physical constraints and unresolved questions.

**Exit criterion:** Energy and entropy balances can be written for the chosen system boundaries and every term is defined.

## Phase I — Thermodynamic environment

**Objective:** Represent the energy source, receiver and sink with defensible physics.

First model:
- A stellar radiation source with specified spectrum and luminosity.
- A planetary receiver with geometry, rotation/orbit or simplified forcing, reflectance and radiative properties.
- An outgoing radiative sink at a specified effective temperature.
- Spatial and temporal distributions where they materially affect the question.

Measure separately:
- Incident, reflected, absorbed and emitted energy.
- Radiation spectrum and energy quality/exergy relative to the relevant environment.
- Entropy carried by incoming and outgoing radiation.
- Internal entropy production where the model includes irreversible processes.

Controls: no internal organization; alternative albedo and atmospheric assumptions; different forcing regimes and planet parameters.

**Exit criterion:** Energy and entropy budgets close to declared tolerances; approximations and omitted processes are documented.

## Phase II — Dissipative organization

**Objective:** Investigate whether simple structures can form and persist under sustained flows without starting with organisms.

Candidate model families:
- Reaction-diffusion systems.
- Driven chemical reaction networks.
- Autocatalytic or collectively autocatalytic networks.
- Compartmentalization and catalytic cycles.
- Systems with competing pathways and finite resources.

A visually ordered pattern is not evidence of self-maintenance. Test whether organization is dynamically sustained, what it consumes and exports, and how it responds when the driving flux is interrupted.

Controls: flux-off and resource-depletion controls; passive pattern-formation models; random or non-catalytic network controls; perturbation, recovery and extinction experiments.

**Exit criterion:** At least one specified mechanism produces persistent organization whose maintenance and material/energy costs can be accounted for.

## Phase III — Replication, heredity and selection

**Objective:** Investigate the transition from maintained organization to systems that replicate with heritable variation.

Requirements:
- A physically specified replication mechanism.
- A material and energy budget for replication and maintenance.
- A definition of parent/descendant continuity and inheritance fidelity.
- Sources of variation and measurable mutation/error rates.
- Competition for finite resources and environmental constraints.

Separate two problems: (1) how replication first becomes possible and (2) how populations evolve once replication already exists. Do not claim to solve the first by simulating the second.

**Exit criterion:** Replication and heritable variation are not merely abstract population operations; their mechanisms and costs are explicit enough for the level of claim being made.

## Phase IV — Evolution of agency

**Objective:** Determine when information processing and action can evolve as costly mechanisms.

Possible trait dimensions: sensing and signal reliability; memory and state estimation; prediction; decision policies; actuation and control; learning, where an explicit physical or algorithmic mechanism is provided.

Tests:
- Matched no-information and no-action controls.
- Cost and reliability sweeps.
- Stable versus changing environments.
- Predictable versus noisy signals.
- Passive, random and informed policies.
- Individual fitness and aggregate energy flows measured separately.

**Exit criterion:** A claimed agency advantage can be traced to a specified information-to-decision-to-action pathway and survives relevant ablations.

## Phase V — Planetary consequences

**Objective:** Assess how evolved systems affect planetary thermodynamic flows.

Compare abiotic baseline; non-replicating dissipative structures; replicating but non-agentic structures; and agentic populations.

Measure energy capture and transformation; stored energy and material reservoirs; radiative output and spectral changes; entropy flows and internal entropy production; and sensitivity to albedo, atmosphere, chemical cycling and system boundary.

**Exit criterion:** Claims about planetary dissipation follow from a complete and transparent accounting model, not a proxy such as population size or biological throughput.

## Immediate tasks

1. Complete the thermodynamics glossary and define system boundaries.
2. Build a literature map with competing positions and open problems.
3. Write the minimal star–planet–space energy and entropy balance.
4. Select a tractable physical model family for Phase II only after the balance and assumptions are clear.

## What should not happen yet

- Do not make navigation-policy experiments in the old model the main research direction.
- Do not start a large agent-based simulation of abiogenesis.
- Do not equate complexity with entropy production.
- Do not use entropy production as a fitness function.
- Do not call an entity intelligent because it has a numerical cognition trait.
- Do not interpret an emergent simulation pattern as a physical prediction without validation.

The existing [dissipative-agency-simulation](https://github.com/praveenchandrahas/dissipative-agency-simulation) remains a useful downstream study of evolutionary energy-acquisition strategies. It is not the Phase II foundation.
