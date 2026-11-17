# Protocol 05 — Catalyst-removal recovery under continuous driving

## Objective

Test whether an open, continuously driven mutually catalytic network returns toward its pre-perturbation catalytic abundance after physical removal of X and Y, and quantify how recovery depends on residual catalysts and the post-event catalyst feed reservoir.

## Design

1. Run the open reactor from its baseline feed composition until the chosen intervention time.
2. Remove a specified fraction of X and Y from the reactor.
3. Continue the same dilution and reaction network while varying only the post-event feed activity of X and Y.
4. Compare the perturbed trajectory with an unperturbed run under the original feed and flow conditions.

The pre-intervention history is held fixed across post-event feed conditions. This prevents the confound seen in the earlier finite-batch pilot, where changing background kinetics before intervention also changed the state and remaining resources at intervention.

## Baseline settings

The default reactor uses the open-reactor baseline configuration:
- Duration: 300 s.
- Intervention time: 150 s.
- Dilution rate: 0.05 s⁻¹.
- Catalytic strength: 10.
- Pre-event X/Y feed activity: 1e-8.
- Removal fractions: 90%, 99%, 99.9%.
- Post-event X/Y feed activities: 1e-8, 1e-6, 1e-4.

These are illustrative parameters, not empirical chemical measurements.

## Primary metrics

- Fraction of removed X+Y recovered.
- Fraction of pre-perturbation X+Y restored.
- Final X+Y relative to the unperturbed final state.
- Time to cross 90% of the pre-perturbation X+Y abundance.
- Whether the post-event trajectory satisfies the operational NESS criterion over its terminal window.
- Reaction and reservoir-exchange entropy production after the intervention, reported separately.

Recovery time is reported as null if the threshold is not crossed within the remaining observation interval.

## Controls and interpretation

The pre-event state is identical across post-event catalyst-feed conditions. The post-event feed changes only the trace X/Y reservoir activity; A/B feed, waste/product feed, dilution and reaction parameters remain fixed.

The removal operation is a physical material outflow. Its separation work is not modelled. The post-event catalyst feed is an explicit seed source, so recovery at higher trace feed must not be described as autonomous self-repair.

A successful result demonstrates only recovery in this abstract continuously driven reactor. It does not establish biological repair, replication, heredity or evolution.

## Commands

- `open-reactor --post-catalyst-feed 1e-6 --removal 0.99 --perturbation-time 150 --json`
- `open-reactor --perturb-sweep --json`

For a short smoke test, use a short duration and set the perturbation time strictly inside that duration.
