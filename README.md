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
| S1: selection criterion comparison | **Confirmatory run done** (30 seeds per cell) |
| S2: 16-condition factorial ablation | **Confirmatory run done** (30 seeds per cell) |
| S3: passive baseline, no-ladder control, accounting check | **Confirmatory run done** |
| S4: agency probe (viability restoration) | **Confirmatory run done** |
| Positive control (hand-coded forager) | **Confirmatory run done** |
| S5: Barrow counter-test (efficiency pathway) | **Not implemented** |
| Predictive-information probe | **Not implemented** |

## Try it live

`webapp/index.html` is a single self-contained file. Open it in any browser, no install and no server. It runs the same world in JavaScript, in real time, and explains what you are seeing in plain language: a headline that narrates the current state, a "sunshine used or wasted" bar, where the creatures' energy comes from, and a panel of the creatures' average instincts. To host it, enable GitHub Pages on the `/webapp` folder.

Four presets: **Natural selection** (random creatures; those with spare energy have children), **Random parents** (a control), **Reward burning energy** (entropy used as the reward), and **A hand-coded expert** (fixed rules we wrote, to show what success could look like).

<p align="center"><img src="docs/screenshots/01-early-random-creatures.png" alt="Web app at day 60: creatures wander at random and get 98% of their energy from grass" width="100%"></p>

**Day 60, natural-selection world.** Every creature starts with random instincts. 98% of their energy is grass, and the instinct bars hover near zero. Large amounts of energy are still wasted.

<p align="center"><img src="docs/screenshots/02-hand-coded-expert.png" alt="Web app with the hand-coded expert at day 2,500: 50% of energy from big deposits" width="100%"></p>

**Hand-coded expert, day ~2,500.** Rules we wrote by hand walk toward food and glow and pay energy to open deposits. Here 50% of their energy comes from big deposits, and several creatures stand on each big deposit keeping it open. This is the positive control: it shows the world has headroom. Nothing evolves here.

<p align="center"><img src="docs/screenshots/03-survival-only-evolved.png" alt="Web app after 30,000 days of natural-selection evolution: some creatures have learned to open deposits" width="100%"></p>

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

## Confirmatory results (seeds 0-29, 20,000 steps, as preregistered)

Raw per-run CSVs and the generated reports are in [`docs/results/`](docs/results/). The commit and environment are in `RUN_INFO.txt`. Intervals are 95% bootstrap CIs. **The headline: the thesis as preregistered is only partly supported in this world, and its central ablation prediction (H2) failed.**

| | Prediction | Result | Verdict |
|---|---|---|---|
| **H1** | Persistence selection raises entropy production over random parents | +2.34 [1.08, 3.66] (27.3 vs 24.9) | **Supported**, small effect |
| **H2** | Scarcity, heredity and mortality are each needed for big-deposit access | All-on minus factor-off: scarcity -0.27 [-0.50, -0.03], heredity -0.73 [-0.90, -0.57], mortality -0.53 [-0.73, -0.33], succession -0.10 [-0.33, 0.13] | **Falsified** for all three: removing any of them *raised* big-deposit access. Succession: not shown |
| **H3** | Heredity contributes to recovery from displacement | Full minus no-heredity: +0.220 [0.189, 0.249] | **Supported**, with a caveat below |
| **H4** | Rewarding entropy directly does not beat persistence on big-deposit access | -0.10 [-0.30, 0.10] | **Not falsified** (absence of a difference is not evidence of none) |
| **H5** | Accounting check: capture ratio with kappa = 1 in 0.7-1.15 | 1.080 [1.017, 1.143] | **Passes**, barely inside at the upper CI |

<p align="center"><img src="figures/s2_leave_one_out.png" alt="H2 leave-one-out: every removable condition has a negative effect" width="100%"></p>

### What the results do and do not say

- **The world is not degenerate, and there is headroom.** The hand-coded forager reaches big deposits in 100% of runs and gets 50% of its energy from them, with an entropy rate of 37.1. Evolved populations reach big deposits in 27% of runs, get 2% of their energy from them, and reach 27.3. Selection moved things a little way (H1), and left most of the available gain unused.
- **H1 is weaker than it looks.** The random-parents control still has viability selection (see limitation 6), so H1 measures fecundity selection on top of it. Rewarding grass-eating (26.5) also appears to beat random parents (no interval computed for that contrast), so the gain is not specific to persistence. Persistence versus task reward was not a preregistered contrast.
- **H2 failed, and the likely reason is a free-rider problem. This explanation is post hoc and untested.** Opening a deposit costs the investor energy, and the payoff is shared with everyone on the square. When starvation is fatal and genomes are inherited, evolution appears to select against paying that cost: in the one evolved world we inspected, the instincts avoided deposits. The data are consistent with this: with scarcity and mortality on, fresh random genomes reach big deposits in 100% of runs versus 27-37% for inherited ones. Removing mortality (bailouts) lifts the tier-2 energy share from about 4% to 30-35% under scarcity. But `t2_reached` only means a site was ever fully open, not that it was used steadily, and the tier-2 energy share is low in every mortal cell (1.4-5.9%). Treat the mechanism as a hypothesis for the next experiment, not a finding.
- **Entropy rate is not comparable across S2 cells.** Abundant-food and no-mortality cells fill the population cap (200) and so have entropy rates of 90-130 against 27-33 in the scarce, mortal cells. That is population size, not agency.
- **H3 is narrower than "agency".** The recovery gain needs heredity (full minus no-heredity = 0.22). But random-parents selection gives almost the same gain (0.259 vs 0.270 for persistence): what is inherited is mostly better grass-foraging filtered by starvation. It does not require selection by surplus. The raw evolved-minus-random gap is also inflated by survivorship, which is why the contrast is the preregistered quantity.
- **Succession did not help.** The ladder without succession had a higher entropy rate (33.0) than the full ladder (27.3) and a nominally higher big-deposit rate (0.37 vs 0.27), though the preregistered succession effect on `t2_reached` is not shown (CI includes zero).
- **Not tested:** whether any of this transfers to Earth, whether a less-biased policy class would behave differently (the generic MLP did not evolve), Barrow's miniaturisation counter-argument (S5), or prediction.

### S6: testing the free-rider explanation (preregistered in [`PREREGISTRATION_S6.md`](PREREGISTRATION_S6.md))

If opening a deposit were a public good that selection punishes, making the benefit private should help. In the `contributor` rule the harvest on a deposit is split by each agent's recent investment. Result (30 seeds): **not supported at this power**.

- H6a, contributor minus equal sharing (heredity on): tier-2 energy share +0.024 [-0.023, 0.075]; reached big deposits +0.13 [-0.10, 0.37]. The direction is as predicted, the interval includes zero.
- H6b, heredity minus no heredity (contributor): tier-2 share -0.017 [-0.059, 0.032]; reached big deposits -0.60 [-0.77, -0.43]. Heredity still does not help, and random fresh genomes still reach big deposits in 100% of runs.

So the simple free-rider story is not confirmed. Something else makes inherited policies avoid, or fail to sustain, the big deposits. Candidates (untested): the policy class is too constrained to learn a conditional, cooperative "invest only when others are nearby" rule; the cost and the payoff arrive too far apart for 27 genes to link; or the extrinsic hazard dominates. This is why the next step is a richer world and genome (below).

<p align="center"><img src="figures/s1_selection.png" alt="S1: four selection rules compared" width="100%"></p>
<p align="center"><img src="figures/trajectories.png" alt="Entropy production and big-deposit share over time" width="100%"></p>
<p align="center"><img src="figures/s2_heatmap.png" alt="All 16 combinations of the four conditions" width="100%"></p>
<p align="center"><img src="figures/s4_recovery.png" alt="S4: recovery after displacement" width="100%"></p>
<p align="center"><img src="figures/s3_accounting.png" alt="S3: accounting and ladder controls" width="100%"></p>
<p align="center"><img src="figures/world_snapshots.png" alt="World snapshots" width="100%"></p>

## Notes from the pilot (seeds 1000-1003, not confirmatory)

- The world went through ten design changes because early pilots showed null results. They are listed in [`docs/DESIGN.md`](docs/DESIGN.md#design-history-forced-by-pilots). A design tuned until selection beats random parents tends to make selection beat random parents, so weigh H1 with that in mind. H2 failing despite this tuning is some evidence the tuning did not simply guarantee the thesis.
- The pilot suggested entropy-as-reward would not breed more entropy than persistence. The confirmatory run agrees (H4 not falsified).

## Known limitations

1. **Toy world, one abstraction.** Whether these five features are what mattered on Earth is assumed, not tested.
2. **The default policy has a strong prior.** The `equivariant` policy (about 27 parameters, shared weights across directions) is chemotaxis-shaped. A generic MLP policy did not evolve useful behaviour in the available budget. So "agency emerged" here means "a small, well-shaped policy was tuned by selection", which is a much weaker claim than emergence from nothing.
3. **Capture Ratio is largely an accounting identity.** It depends on an assumed `kappa` (entropy per unit energy for agents vs passive leakage). S3 includes a `kappa = 1` row as a sanity check. The empirical quantities are the capture fraction and tier shares.
4. **Viability restoration is not prediction.** And the raw evolved-vs-random gap is inflated by survivorship; only the full-vs-no-heredity contrast is interpretable (see the S4 docstring).
5. **The gradient ladder is held fixed** in the factorial design, because removing it would make tier ascent false by construction. Its necessity is only probed by the S3 no-ladder control, which is not a test of agency.
6. **The drift control is not fully neutral.** Parents are random among survivors, so starvation still filters genomes. Only fecundity selection is removed. H1 therefore measures the effect of fecundity selection on top of viability selection.
7. **The extrinsic death hazard** (needed for enough generations) is itself a built-in selection pressure.

## Roadmap

- Test the free-rider explanation for H2 directly (for example, make deposit benefits private or kin-shared, and see whether big-deposit access recovers under heredity and mortality).
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
