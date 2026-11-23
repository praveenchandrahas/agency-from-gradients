# Research and simulation architecture

**Status:** Proposed architecture, version 0.1  
**Guiding rule:** Each model should answer one well-defined causal question. Do not combine all stages into a single simulation before their mechanisms and accounting are independently defensible.

## 1. Layered architecture

Research hypotheses and null models  
↓  
Definitions, operational measures and system boundaries  
↓  
Thermodynamic ledger + literature and empirical constraints  
↓  
Local chemical disequilibrium  
↓  
Driven chemical networks and non-equilibrium organization  
↓  
Self-maintenance and replication  
↓  
Evolution and ecology  
↓  
Information processing and agency  
↓  
Planetary consequences  
↓  
Validation, null tests and robustness analysis

The layers are coupled through explicit interfaces, not shared hidden assumptions.

## 2. Model modules

### A. Stellar–planetary thermodynamic ledger

**Exists:** first zero-dimensional implementation in src/thermodynamic_emergence/model.py.

Responsibilities:
- Intercepted, reflected, absorbed and emitted power.
- Energy imbalance and storage.
- Radiation entropy flux under explicit spectral/angular assumptions.
- Approximate exergy with a declared reference environment.

Non-responsibilities:
- Climate reconstruction, local habitability, chemistry, life or agency.

Required validation: analytic limits, numerical convergence, energy closure and comparison with published radiation-entropy calculations under matching assumptions.

### B. Local chemical disequilibrium

**Next model family.**

Responsibilities:
- Define a local control volume and its reservoirs.
- Specify chemical species, stoichiometry, chemical potentials and reaction rates.
- Represent redox, pH, thermal or photochemical driving where relevant.
- Calculate reaction free-energy changes, fluxes and entropy production consistently.
- Explore gradients and material constraints without assuming life.

Non-responsibilities:
- Treating a high reaction rate or high entropy production as proof of life or adaptation.

### C. Driven reaction networks and organization

Responsibilities:
- Reaction kinetics and nonlinear coupling.
- Catalytic and autocatalytic motifs.
- Reaction-diffusion or transport where needed.
- Finite substrates, products, inhibitors and waste.
- Formation, lifetime, perturbation response and flux dependence of structures.

A pattern is not self-maintaining merely because it persists for a finite simulation window.

### D. Self-maintenance and replication

Responsibilities:
- Explicit regeneration and repair loops.
- Compartment or boundary maintenance where mechanistically justified.
- Replication chemistry and resource costs.
- Parent–descendant continuity, inheritance fidelity and variation.

A population algorithm that copies an entity is an evolutionary abstraction, not a model of abiogenesis.

### E. Evolution and ecology

Responsibilities:
- Lineage dynamics, competition and finite resources.
- Differential persistence and reproduction.
- Ecological feedback, spatial dispersal and extinction.
- Independent fitness and thermodynamic ledgers.

No global entropy-production bonus in fitness.

### F. Information and agency

Responsibilities:
- Physical or algorithmic sensing channels with noise and costs.
- Memory and state estimation.
- Prediction under uncertainty.
- Decision policies and action costs.
- Counterfactual tests showing that information-guided action changes outcomes.
- Comparison against reactive, random, fixed and passive strategies.

Intelligence should be measured through a set of declared task and generalization metrics, not a single arbitrary trait multiplier.

### G. Planetary coupling

Responsibilities:
- Couple biological and chemical activity to planetary optical, atmospheric, hydrological and thermal properties only when mechanisms are specified.
- Maintain matched abiotic controls under identical external forcing.
- Aggregate local energy, exergy and entropy flows without double-counting.
- Test whether the net planetary effect increases, decreases or redistributes entropy production.

## 3. Shared interfaces and data contracts

Every module should declare:

- System boundary and control-volume geometry.
- State variables, units and reference conditions.
- External forcing and boundary fluxes.
- Internal processes and rate laws.
- Energy storage and transfer terms.
- Entropy storage, entropy transfer and entropy generation terms.
- Material inputs, outputs and conservation residuals.
- Initial conditions and random seeds.
- Parameters, provenance and uncertainty.
- Outputs, diagnostics and known omissions.

Use SI units internally. Store configuration and run metadata alongside results. A downstream model may consume an upstream model's outputs only with the assumptions and uncertainties attached.

## 4. Experiment architecture

Each experiment should include:

1. A named hypothesis and prediction.
2. A baseline and at least one relevant null.
3. Matched forcing and initial conditions where comparison requires them.
4. A predeclared primary outcome.
5. Independent measures of energy, exergy, entropy production and fitness.
6. Replicates and uncertainty summaries.
7. Sensitivity analysis and parameter provenance.
8. A machine-readable run manifest.
9. A report distinguishing model result, interpretation and limitation.

Parameter sweeps are useful only after the model's causal structure is defensible. They cannot rescue an incorrect mechanism.

## 5. Target repository structure

- theory/: definitions, thermodynamic foundations, core hypothesis and causal model.
- src/thermodynamic_emergence/: reusable scientific implementations.
- models/stellar_planet/: source–receiver accounting.
- models/local_chemical/: local disequilibrium and reaction energetics.
- models/driven_networks/: reaction kinetics and organization.
- models/replication/: self-maintenance, copying and heredity.
- models/evolution/: population and ecological dynamics.
- models/agency/: information, decisions and control.
- experiments/: protocols, configurations and results.
- tests/: analytic limits, conservation checks and regression tests.
- references/: annotated bibliography and evidence map.
- papers/: manuscripts and supplementary material.

This is a target structure, not a mandate to create empty directories or premature abstractions. Add a module only when a defined experiment needs it.

## 6. Relationship to dissipative-agency-simulation

Keep dissipative-agency-simulation as a downstream, separate project. It studies selection among already-existing coarse-grained entities with specified energy-acquisition and behavioural mechanisms.

Its results can inform the evolution/agency layer, particularly the distinction between individual advantage and aggregate planetary throughput. They cannot establish the origin of self-maintenance or replication.

Cross-reference the projects and exchange only clearly defined outputs and assumptions. Do not merge the repositories or retrofit the earlier simulation into an abiogenesis model.

## 7. Development sequence

1. Validate the existing stellar–planetary ledger and its limits.
2. Build a minimal local chemical disequilibrium model with a closed reaction and energy ledger.
3. Add driven reaction-network dynamics and flux-off controls.
4. Test formation and persistence of organization from unstructured initial conditions.
5. Introduce self-maintenance only through explicit mechanisms.
6. Add replication and heredity only when a physical copying mechanism is specified.
7. Study selection and information-use costs.
8. Couple local results to planetary consequences only when aggregation and boundary accounting are justified.

Do not skip stages because a later-stage simulation is visually compelling.
