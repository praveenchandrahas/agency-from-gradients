# Results

## Read these as a set

Ten experiments. Mostly negative. That is the finding.

If you only read one result, read H2 on the [main run page](main.md). It failed, and everything after it is an attempt to understand why, or to ask a related question.

## The map

| Page | What it covers | Seeds | Headline |
|---|---|---|---|
| [S1 to S5, the main run](main.md) | H1 to H5, the factorial ablation | 30 per cell | Partly supported. **H2 falsified** |
| [S6](s6.md) | The free-rider explanation | 30 per cell | Not supported at this power |
| [S7](s7.md) | Bigger genomes, recombination, a richer world | 20 per arm | Not supported. 90% extinction |
| [S8](s8.md) | Entropy as an explicit objective | 5 runs per kappa | A furnace, not agency |
| [S9](s9.md) | A learned private reward | 20 per arm | Not supported |
| [S10](s10.md) | Dissipative adaptation, no selection | 20 per arm | Not supported |
| [S11](s11.md) | The best entropy raiser in a lifeless universe | 20 parameter draws | A black-hole engineer |

S5, Barrow's counter-test, is **not implemented**. S0, the re-analysis of earlier genome trajectories, is implemented against an *assumed* data format and has never run on the real files.

## Where the raw data is

Honesty about provenance matters, so here it is.

- **S7-v3, S8, S9, S10, S11:** per-run CSVs are on the [`ci-results` branch](https://github.com/praveenchandrahas/agency-from-gradients/tree/ci-results).
- **S1 to S4 and S6:** those CSVs are **not** in the repo. Reproduce them with the [commands here](../running.md). Seeds 0 to 29 take roughly 30 to 60 minutes per experiment on two cores.

Numbers on these pages are copied from the README results tables, which in turn come from the generated reports.

## How to weigh each result

Three questions, every time.

1. **Was it blind?** H1 to H5 were written before any confirmatory run. The follow-ups were not. Each says what had already been seen.
2. **Is the contrast the right one?** Several raw gaps are inflated by survivorship or by a confounded baseline. The preregistered contrast is the one reported, even when a better one exists.
3. **What does the interval include?** If it includes zero, the answer is *not shown at this power*. Not "no effect".
