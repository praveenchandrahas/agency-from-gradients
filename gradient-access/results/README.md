# Results

The GitHub Actions workflow for the long-horizon 16-bit exploratory run uploads an artifact named `ega-long-horizon-key16-results`.

Expected contents:

- `replicates.csv`: one row per design × barrier × paired seed × arm.
- `summary.json`: per-arm means, standard deviations and bootstrap percentile intervals.
- `paired_contrasts.json`: paired L−M, L−Mmatched, L−D, L−Dmatched, L−A, L−Amatched, L−U, L−Umatched and L−N contrasts.
- `trajectories.jsonl.gz`: compressed time series for every run.
- `manifest.json`: parameters, seed count, designs and uncertainty method.
- `figures/`: contrast plots.

Mmatched, Dmatched, Amatched and Umatched are initialized at the paired L run's rounded late-window mean abundance. Dmatched is a self-maintaining faithful-copying control with no new mutation; the other matched controls are fixed populations or bounded search. This is abundance matching, not yet complete energetic-investment matching.

The initial 8-bit pilot and short-horizon matched 16-bit pilot are retained separately as `ega-initial-exploratory-results` and `ega-matched-key16-results`. The long-horizon run uses 100 residence-time units and three environmental drift rates to allow substantially more turnover and mutational exploration.

The final paired-drift run's interpretation is in [EXPLORATORY_FINDINGS.md](EXPLORATORY_FINDINGS.md). All runs are exploratory, not confirmatory. See [MODEL_LIMITATIONS.md](../MODEL_LIMITATIONS.md).


## v0.2 coupled-reaction pilot

See [V02_PILOT_FINDINGS.md](V02_PILOT_FINDINGS.md) for the deterministic 240-run sensitivity pilot, thermodynamic closure diagnostics, mutation-versus-faithful-copying contrasts, and next validation gates. Raw CSVs and figures are attached to [the GitHub Actions run](https://github.com/praveenchandrahas/evolutionary-gradient-access/actions/runs/45165208194).


## v0.2 matched standing-variation controls

See [V02_STANDING_CONTROLS.md](V02_STANDING_CONTROLS.md) for the 160-run follow-up comparing mutation against fixed and faithful-copying libraries at matched total catalyst material. Raw CSVs and figures are in [the GitHub Actions artifact](https://github.com/praveenchandrahas/evolutionary-gradient-access/actions/runs/45166815441).
