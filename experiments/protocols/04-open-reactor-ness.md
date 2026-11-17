# Protocol 04 — Continuously driven open-reactor NESS test

## Objective

Determine whether the abstract mutually catalytic network can maintain a non-zero catalytic population in a continuously fed and diluted reactor, and quantify how this depends on catalytic strength and dilution rate.

## Model

Use `thermodynamic_emergence.open_reactor.OpenReactorConfig` and `simulate_open_reactor`.

The reactor is well mixed. All species exchange with finite-activity reservoirs at one dilution rate. A and B have feed activity 1; all other species, including X and Y, have a small positive feed activity (default 1e-8). The latter avoids undefined ideal chemical potentials but means that the system receives continuous trace seeds.

The internal network is:
- A ⇌ X + W_X, catalysed by Y.
- B ⇌ Y + W_Y, catalysed by X.
- X ⇌ D_X.
- Y ⇌ D_Y.

## Baseline settings

- Temperature: 298.15 K.
- Feed activities: A = B = 1; all other species = 1e-8.
- Dilution rate: 0.05 s⁻¹.
- Production forward rate: 0.02 s⁻¹.
- Production equilibrium constant: 10.
- Loss forward rate: 0.001 s⁻¹.
- Loss equilibrium constant: 1e-4.
- Mutual catalytic strength: 10.
- Uncatalysed background factor: 0.01.
- Duration: 300 s.
- RK4 time step: 0.002 s.

These are illustrative numerical values, not measured prebiotic parameters.

## Procedure

1. Run `open-reactor --json` and retain the complete output.
2. Run `open-reactor --compare` to compare catalytic and uncatalysed reactors under matched feed and flow conditions.
3. Run `open-reactor --sweep --json` to cross catalytic strengths 0, 1, 10 and 100 with dilution rates 0.01, 0.05 and 0.1 s⁻¹.
4. Record final X+Y, operational NESS classification, endpoint drift, maximum window coefficient of variation, reaction entropy production and reservoir-exchange entropy production.
5. Repeat at longer durations and alternative NESS windows before interpreting a NESS flag as robust.
6. Vary trace X/Y feed in a separate sensitivity experiment before making any statement about seed independence.

## NESS diagnostic

The model flags an operational NESS only when both maximum relative endpoint drift and maximum species coefficient of variation over the terminal window are below 1e-3 by default. This is a numerical criterion, not proof of unique or global stability.

## Thermodynamic accounting

Reaction entropy production and reservoir-exchange entropy production are reported separately. The exchange term is:
`c° R Σ_i J_i ln(c_i_feed/c_i)`.

It is non-negative for the specified ideal exchange law. It does not include mechanical pumping, mixing, reservoir construction/regeneration or temperature-control work. Do not call it a complete chemostat-maintenance cost.

## Controls

The uncatalysed null sets catalytic strength to zero and leaves all other settings unchanged. A valid comparison must keep feed composition, dilution, integration horizon and numerical settings identical.

## Interpretation

A NESS result demonstrates only stationary chemical activity under this model's imposed feed and dilution. It does not demonstrate spontaneous assembly, seed-free emergence, self-repair, replication, heredity, evolution or life.

A non-NESS result is conditional on the tested parameter regime and observation horizon. Report it as such.
