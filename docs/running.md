# How to run

## Install

```bash
pip install -e ".[dev]"
pytest -q          # about 10 seconds
```

The only runtime dependency is `numpy`. Python 3.10 or newer.

## The seed rule

This one matters more than any command.

| Seeds | Use |
|---|---|
| **0 to 29** for S1 to S6. **0 to 19** for S7, S9, S10 and S11. **0 to 4** for S8's optimisation runs | Confirmatory. Report these. |
| **1000 and above** | Pilots and debugging. **Never** report as evidence. |

Why? A pilot that looks good tempts you to tune. Tune on the seeds you will report, and you have fooled yourself. So the two sets never mix.

## Run an experiment

=== "Smoke test"

    A plumbing check. Tiny runs.

    ```bash
    python -m agency_gradients.experiments.s2_ablation --smoke
    ```

=== "Pilot"

    Held-out seeds. Not for confirmatory claims.

    ```bash
    python -m agency_gradients.experiments.s_control    --seeds 4 --seed0 1000
    python -m agency_gradients.experiments.s1_selection --seeds 4 --seed0 1000
    ```

=== "Confirmatory"

    Seeds 0 to 29, 20,000 steps. Roughly 30 to 60 minutes per experiment on two cores.

    ```bash
    python -m agency_gradients.experiments.s1_selection
    python -m agency_gradients.experiments.s2_ablation
    python -m agency_gradients.experiments.s3_succession
    python -m agency_gradients.experiments.s4_agency
    ```

=== "Later experiments"

    ```bash
    python -m agency_gradients.experiments.s6_private_benefit
    python -m agency_gradients.experiments.s7_complex_world --seeds 4 --seed0 1000      # pilot
    python -m agency_gradients.experiments.s8_entropy_objective --seeds 2 --seed0 1000  # pilot
    ```

    S7 pilots run 100,000 steps per run.

    S9 and S10 live in `src/agency_gradients/experiments/` and take the same `--seeds`, `--seed0` and `--steps` flags. S11 is different. It is organised by arm and horizon, with `--arm`, `--horizon`, `--es-seed` and `--n-es`. Check each module's `--help` before you start. The confirmatory S9 to S11 runs were dispatched through GitHub Actions.

=== "S0"

    S0 re-analyses your saved genome trajectories. It was written against an **assumed** JSON schema and has never run on the real files.

    ```bash
    python -m agency_gradients.experiments.s0_reanalysis 'data/evo_*.json' --tier2-threshold 0.6
    ```

## Where the output goes

Each experiment writes a CSV of every run and a Markdown report to `results/`. That folder is git-ignored.

## Run it on GitHub Actions

You do not need local compute. Every long run can start from the repo's **Actions** tab.

| Workflow | Runs |
|---|---|
| `confirmatory-runs` | S1 to S4 and the control |
| `complex-world-runs` | S6 and the five S7 variants |
| `s7-custom` | Free-form S7 pilots, scaled worlds |
| `s8-entropy-objective` | S8 |
| `ci-publish-test` | A tiny check of the results-publishing step |
| `pages` | Publishes the explainer, the grid view, and this site |

Each one uploads its results as artifacts. It also commits them to the [`ci-results` branch](https://github.com/praveenchandrahas/agency-from-gradients/tree/ci-results), so you can read them without downloading anything.

## Reading the results

Each run's CSV has one row per run. Reports are Markdown. The metrics are defined on [the world page](world.md#how-i-measure-things).

Remember the reading rules. Intervals are 95% bootstrap. An interval that includes zero is *not shown*, not *no effect*.

## Work on these docs

This site is built with [MkDocs Material](https://squidfunnel.github.io/mkdocs-material/).

```bash
pip install -r requirements-docs.txt
mkdocs serve          # live preview at http://127.0.0.1:8000
mkdocs build --strict # what CI runs: any broken link fails the build
```

Pages live in `docs/`. Add one, then list it under `nav:` in `mkdocs.yml`.

Math is written with `\( ... \)` for inline and `\[ ... \]` for display.

The `pages` workflow rebuilds the site on every push to `main` that touches `docs/` or `mkdocs.yml`. It publishes it at `/docs/`, next to the explainer and the live grid view. Nothing already published moves.

## Rebuild the explainer and film

Both are single self-contained files with the fonts inlined.

```bash
python3 learn/build.py
```

The sources are in `learn/src/`. The build needs the three `@fontsource` npm packages listed in `build.py`. The MP4 is rendered by stepping the film's canvas frame by frame into ffmpeg.

## Repository layout

```text
src/agency_gradients/
  config.py        every knob; a run is fully described by (Config, seed)
  world.py         the engine and its energy ledger
  controls.py      hand-coded positive control
  world_v2.py      the richer world
  policies_v2.py   v2 policies and heritable traits
  probes.py        viability-restoration probe
  stats.py         bootstrap helpers (numpy only)
  runner.py        parallel job runner and CSV output
  cosmos/          the S11 cosmic ledger
  experiments/     s0 ... s11, plus the positive control
webapp/            browser version of the world
explainer/         plain-language page with a live pond
learn/             the film and the long-form explainer site
analysis/          figure scripts
tests/
docs/              this site, plus DESIGN.md and screenshots
PREREGISTRATION*.md
```
