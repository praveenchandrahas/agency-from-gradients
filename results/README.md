# Results

The initial GitHub Actions exploratory run uploads an artifact named `ega-initial-exploratory-results`.

Expected contents:

- `replicates.csv`: one row per design × barrier × paired seed × arm.
- `summary.json`: per-arm means, standard deviations and bootstrap percentile intervals.
- `paired_contrasts.json`: paired L−M, L−D, L−A, L−U and L−N contrasts.
- `trajectories.jsonl.gz`: compressed time series for every run.
- `manifest.json`: parameters, seed count, designs and uncertainty method.
- `figures/`: contrast plots when the analysis step is enabled.

The first run is exploratory, not confirmatory. The current model's material matching and thermodynamic boundary limitations are documented in [MODEL_LIMITATIONS.md](../MODEL_LIMITATIONS.md). Do not interpret the outputs as empirical evidence or a complete physical entropy budget.
