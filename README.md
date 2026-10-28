# agency-from-gradients

<p align="center"><img src="docs/banner.png" alt="Banner: agency-from-gradients. Can agency arise without a built-in objective? Simulate, ablate, measure. A torus world with low, medium and high energy reservoirs, and agents that move, consume, invest, reproduce and die." width="100%"></p>

<sub><i>The banner is an illustration. Its example charts are mock-ups, not results, and its design table is a sketch: the ablations actually implemented are food scarcity, heredity, mortality and succession (see below), and there is no memory ablation.</i></sub>

**agency-from-gradients** is a simulation suite built on one design hypothesis: if we want artificial agency, we should reproduce the conditions under which it arose on Earth, not hand agents an objective.

The argument starts from first principles. Structures that drain energy gradients persist, and each new structure feeds on what the last left unexhausted, from stars to supernovae to life. Life is the one case we know where this succession produced agents. The suite asks which of its conditions are load-bearing: a ladder of gradients, finite and contested resources, heredity with variation, a real cost of death, and succession.

Selection is by persistence and reproduction only. Entropy production is measured and never rewarded. Each condition is switched on and off in a factorial design, with hypotheses and falsifiers pre-registered.

> **This repo makes no novelty claim and proves nothing about Earth.** These are toy worlds. A positive result shows that a pattern is robust to ablation in an abstract setting. Whether the abstraction captures what mattered in reality is the central assumption, and we state it openly.

## Status: what exists and what doesn't

| Piece | State |
|---|---|
| World engine (gradient ladder, asynchronous population, closed energy ledger) | Implemented, 29 tests |
| S0: re-analysis of earlier Study 2 genome trajectories | Implemented against an **assumed** JSON schema; never run on the real files |
| S1: selection criterion comparison | Implemented; pilot only (4 seeds) |
| S2: 16-condition factorial ablation | Implemented; **not yet run** |
| S3: passive baseline, no-ladder control, accounting check | Implemented; **not yet run** |
| S4: agency probe (viability restoration) | Implemented; **not yet run** |
| Positive control (hand-coded forager) | Implemented; pilot only |
| S5: Barrow counter-test (efficiency pathway) | **Not implemented** |
| Predictive-information probe | **Not implemented** |
| Confirmatory results | **None.** Nothing in this repo is a finding yet |

## The world, briefly

A torus with a population that lives, eats, invests, reproduces and dies, with no generations and no scoring step.

- **Tier 0, the commons:** a diffuse, renewable, patchy energy field. Weak gradient, so directed foraging can be selected in small steps.
- **Tier 1:** 12 reservoirs that stay open only while agents keep investing in them.
- **Tier 2:** 4 large reservoirs that need several agents investing at once to open fully.
- **Succession (when on):** a Tier 2 site forms only where a Tier 1 site has been drained.
- **Agents** are small policies with a heritable genome. Their actions are move, stay and invest. Nothing tells them what to maximise.

Full details, the metrics and the accounting caveats are in [`docs/DESIGN.md`](docs/DESIGN.md).

## Try it live

`webapp/index.html` is a single self-contained file. Open it in any browser, no install and no server. It runs the same world in JavaScript, in real time, and explains what you are seeing in plain language: a headline that narrates the current state, a "sunshine used or wasted" bar, where the creatures' energy comes from, and a panel of the creatures' average instincts. To host it, enable GitHub Pages on the `/webapp` folder.

Four presets: **Natural selection** (random creatures; those with spare energy have children), **Random parents** (a control), **Reward burning energy** (entropy used as the reward), and **A hand-coded expert** (fixed rules we wrote, to show what success could look like).

<p align="center"><img src="docs/screenshots/01-early-random-creatures.png" alt="Web app at day 60: creatures wander at random and get 98% of their energy from grass" width="100%"></p>

**Day 60, natural-selection world.** Every creature starts with random instincts. 98% of their energy is grass, and the instinct bars hover near zero. Large amounts of energy are still wasted.

<p align="center"><img src="docs/screenshots/02-hand-coded-expert.png" alt="Web app with the hand-coded expert at day 2,500: 50% of energy from big deposits" width="100%"></p>

**Hand-coded expert, day ~2,500.** Rules we wrote by hand walk toward food and glow and pay energy to open deposits. Here 50% of their energy comes from big deposits, and several creatures stand on each big deposit keeping it open. This is the positive control: it shows the world has headroom. Nothing evolves here.

<p align="center"><img src="docs/screenshots/03-natural-selection-evolved.png" alt="Web app after 30,000 days of natural-selection evolution: some creatures have learned to open deposits" width="100%"></p>

**Natural-selection, day ~30,000.** In this run, inheritance has shifted the instincts: the "opens big deposits" bar moved right and 9% of energy now comes from big deposits. This is one stochastic example. In other runs, evolved creatures never use the deposits (we saw this in an earlier capture of the same preset), which is exactly why the confirmatory experiments use 30 seeds per condition rather than a picture.

<p align="center"><img src="docs/screenshots/04-random-parents-control.png" alt="Web app, random-parents control at day 30,000: all energy from grass" width="100%"></p>

**Random-parents control, day ~30,000.** Children are born to randomly chosen living creatures, so having more energy gives no advantage in having children. All energy is grass. Caveat: this is not a fully neutral control. Starving still removes some genomes, so viability selection remains and only fecundity selection is removed. See the note in the [pre-registration](PREREGISTRATION.md#deviation-log).

<p align="center"><img src="docs/screenshots/05-phone.png" alt="Web app at phone width" width="320"></p>

Reading the screenshots: they are single seeded runs chosen to illustrate the interface. They are not evidence for the thesis. The evidence, such as it is, is the preregistered experiments.

## Hypotheses and falsifiers

Written down before any confirmatory run: [`PREREGISTRATION.md`](PREREGISTRATION.md).

## Quick start

```bash
pip install -e ".[dev]"
pytest -q                                   # ~10 s

# plumbing check (tiny runs)
python -m agency_gradients.experiments.s2_ablation --smoke

# pilot on held-out seeds (>=1000); do NOT use these for confirmatory claims
python -m agency_gradients.experiments.s_control   --seeds 4 --seed0 1000
python -m agency_gradients.experiments.s1_selection --seeds 4 --seed0 1000

# confirmatory (seeds 0..29, 20000 steps) - roughly 30-60 min per experiment on 2 cores
python -m agency_gradients.experiments.s1_selection
python -m agency_gradients.experiments.s2_ablation
python -m agency_gradients.experiments.s3_succession
python -m agency_gradients.experiments.s4_agency

# S0 needs your saved files
python -m agency_gradients.experiments.s0_reanalysis 'data/evo_*.json' --tier2-threshold 0.6
```

Each experiment writes a CSV of every run and a Markdown report to `results/` (git-ignored).

## What a pilot has and hasn't shown (seeds 1000-1003, not confirmatory)

- The ledger closes and the world is not degenerate. A hand-coded forager reaches Tier 2 in every run and gets about 40% more entropy production than the random-parents control (35.8 vs 25.3).
- Evolved-from-random populations land in between (30.2), with Tier 2 reached in 2 of 4 runs. The confidence intervals overlap heavily at 4 seeds. This is a reason to run the real experiment, not a result.
- Entropy-as-reward did **not** produce more entropy than persistence in the pilot (27.4 vs 30.2, overlapping CIs). I had expected it might breed "furnaces"; the pilot doesn't support that, and the preregistration doesn't claim it.
- The world went through ten design changes because early pilots showed null results. They are listed in [`docs/DESIGN.md`](docs/DESIGN.md#design-history-forced-by-pilots). Readers should weigh that: a design tuned until selection beats drift tends to make selection beat drift.

## Known limitations

1. **Toy world, one abstraction.** Whether these five features are what mattered on Earth is assumed, not tested.
2. **The default policy has a strong prior.** The `equivariant` policy (about 27 parameters, shared weights across directions) is chemotaxis-shaped. A generic MLP policy did not evolve useful behaviour in the available budget. So "agency emerged" here means "a small, well-shaped policy was tuned by selection", which is a much weaker claim than emergence from nothing.
3. **Capture Ratio is largely an accounting identity.** It depends on an assumed `kappa` (entropy per unit energy for agents vs passive leakage). S3 includes a `kappa = 1` row as a sanity check. The empirical quantities are the capture fraction and tier shares.
4. **Viability restoration is not prediction.** And the raw evolved-vs-random gap is inflated by survivorship; only the full-vs-no-heredity contrast is interpretable (see the S4 docstring).
5. **The gradient ladder is held fixed** in the factorial design, because removing it would make tier ascent false by construction. Its necessity is only probed by the S3 no-ladder control, which is not a test of agency.
6. **The drift control is not fully neutral.** Parents are random among survivors, so starvation still filters genomes. Only fecundity selection is removed. H1 therefore measures the effect of fecundity selection on top of viability selection.
7. **The extrinsic death hazard** (needed for enough generations) is itself a built-in selection pressure.

## Roadmap

- Run S1 to S4 confirmatory, publish the report whatever it says.
- S5: add an efficiency pathway and deplete gradients, to see whether populations go thermodynamically quiet (Barrow's miniaturisation counter-argument).
- Predictive-information probe, which needs the MLP policy to evolve (or a memory-bearing equivariant variant).
- Run S0 on the real Study 2 trajectories.

## Layout

```
src/agency_gradients/
  config.py        every knob; a run is fully described by (Config, seed)
  world.py         the engine and its energy ledger
  controls.py      hand-coded positive control
  probes.py        viability-restoration probe
  stats.py         bootstrap helpers (numpy only)
  runner.py        parallel job runner and CSV output
  experiments/     s0 ... s4, plus the positive control
webapp/            browser version of the world (index.html is generated by build.py)
analysis/          figure scripts
tests/
docs/DESIGN.md
docs/screenshots/
PREREGISTRATION.md
```

## License

Apache-2.0. See [`LICENSE`](LICENSE).
