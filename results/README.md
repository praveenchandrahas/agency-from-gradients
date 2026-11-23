# Results

The GitHub Actions workflow for the matched 16-bit exploratory run uploads an artifact named `ega-matched-key16-results`.

Expected contents:

- `replicates.csv`: one row per design × barrier × paired seed × arm.
- `summary.json`: per-arm means, standard deviations and bootstrap percentile intervals.
- `paired_contrasts.json`: paired L−M, L−Mmatched, L−D, L−A, L−Amatched, L−U, L−Umatched and L−N contrasts.
- `trajectories.jsonl.gz`: compressed time series for every run.
- `manifest.json`: parameters, seed count, designs and uncertainty method.
- `figures/`: contrast plots.

Mmatched, Amatched and Umatched are fixed controls whose catalyst counts match the paired L run's rounded late-window mean abundance. This is abundance matching, not yet complete energetic-investment matching.

The initial 8-bit pilot artifact is retained separately as `ega-initial-exploratory-results`. The matched 16-bit experiment is a follow-up designed to reduce the chance that the initial random library already contains near-perfect keys.

Both runs are exploratory, not confirmatory. See [MODEL_LIMITATIONS.md](../MODEL_LIMITATIONS.md).
