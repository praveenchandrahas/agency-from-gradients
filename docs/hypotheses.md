# Hypotheses and falsifiers

## Why write them down first?

Here is the thing about simulations.

You can always tune one until it agrees with you. Change a parameter. Re-run. Change another. Eventually the world does what you hoped.

The only defence is to commit *in advance*. Write the predictions. Write what would count as failure. Freeze the design. Then run.

That is what the preregistration files are.

!!! note "The canonical files live in the repo"
    I do not copy them here. They are frozen records, and a copy can drift. This page summarises them and links to the originals.

    - [`PREREGISTRATION.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/PREREGISTRATION.md): H1 to H5
    - [`PREREGISTRATION_S6.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/PREREGISTRATION_S6.md) to [`S11`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/PREREGISTRATION_S11.md): the follow-ups

The rebuilt argument is in [The thesis, rebuilt from the hypothesis](thesis.md). It reads the results against the hypothesis, separates the sufficiency and necessity claims, and treats the later experiments as diagnostics rather than confirmatory evidence.

What came next is in [Why the next experiment starts before life](before-life.md). S14 is preregistered in [`PREREGISTRATION_S14.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/PREREGISTRATION_S14.md). It was frozen on `main` before its confirmatory run. [The result](results/s14.md) is a null.

S15 goes underneath all of these. It tests the core claim directly: in cold, locked gradients, does life open the lock when nothing else does? It is preregistered in [`locks/PREREGISTRATION.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/locks/PREREGISTRATION.md), frozen on `main` before its run. The plain-language version is [Locks (S15)](locks.md). [The result](results/s15.md).

!!! success "The hypothesis was revised on 2026-11-23"
    After S15, the chain the hypotheses rest on was rewritten to fit the results. The revised version, and the evidence for each link, is on [where the hypothesis stands](standing.md). The preregistrations below are frozen records and are not changed.

## The protocol

- **Confirmatory seeds:** 0 to 29, 20,000 steps, default configuration.
- **Pilot seeds:** 1000 and above. Free to use for debugging. **Never** reported as evidence.
- **Intervals:** 95% percentile bootstrap, 4,000 resamples.
- **Decision rule:** a hypothesis is *supported* only if its interval excludes zero in the stated direction.
- **Deviations** must be logged, with the reason, before results are reported.

!!! warning "A null is not an absence"
    `t2_reached` is a binary outcome. With 30 runs per cell, a difference smaller than about 0.25 is unlikely to be detected.

    So when an interval includes zero, the right reading is *not shown at this power*. It is not "no effect".

## The five main hypotheses

| | Prediction | Falsified if | Outcome |
|---|---|---|---|
| **H1** | Persistence-only selection raises entropy production, without rewarding it | The CI of persistence minus drift includes 0 or is below it | **Supported**: +2.34 [1.08, 3.66] |
| **H2** | Access to the big deposits needs scarcity, heredity *and* mortality | Removing a factor does not lower access | **Falsified** for all three |
| **H3** | Heredity contributes to recovery from displacement | The CI of full minus no-heredity includes 0 | **Supported**: +0.220 [0.189, 0.249] |
| **H4** | Rewarding entropy directly does *not* beat persistence on big-deposit access | The entropy arm is clearly better | **Not falsified**: -0.10 [-0.30, 0.10] |
| **H5** | Accounting check: capture ratio at kappa = 1 lies in 0.7 to 1.15 | It falls outside the range | **Passes**: 1.080 [1.017, 1.143] |

Two of these deserve a second look.

**H2 is the one that matters.** It was the central ablation claim. It failed, and not by a hair. Every removable factor had a negative effect, with intervals below zero. [The results page](results/main.md) works through why.

**H5 is not evidence.** It is a sanity check on my own bookkeeping. If it had failed, I would have reported no S3 numbers at all.

## The follow-up hypotheses

These came after the main run. That changes their status.

!!! info "H1 to H5 are blind predictions. The later ones are not."
    The follow-ups were written *after* I had seen earlier results, and sometimes after pilots. Each file says so. Weigh them accordingly.

| | Asks | Preregistered as | Outcome |
|---|---|---|---|
| **S6** | Is the H2 failure a free-rider problem? | H6a, H6b | Neither supported |
| **S7-v3** | Does a bundle of fixes let a 5,300-gene genome beat the small policy? | H7a, H7b, H7c | None supported |
| **S8** | What does an explicit entropy objective produce? | H8a, H8b, H8c | H8a and H8c supported, H8b not |
| **S9** | Does a learned private reward produce agency? | H9a to H9d | None supported |
| **S10** | Does dissipative adaptation, with no selection, climb the ladder? | H10a to H10e | H10a to c supported by construction, H10d and H10e not |
| **S11** | What best raises the entropy of a lifeless universe? | H11a to H11h | Mostly supported. H11b and H11d not |
| **S14** | With no agents, genomes or fitness, does a driven soup start copying itself? | H14a to H14d | H14a and H14b not supported. H14c and H14d not run. A later re-check corrected one descriptive number: with mixing counted, the copier out-dissipates the mineral by about 3% |
| **Starlight** | In a minimal world, does persistence selection raise capture, and does behaviour evolve only when needed? | P1a to P1d, P2a to P2e, P3a and P3b, in `starlight/PREREGISTRATION.md` | 11 of 11 supported. Its lifeless world was a mirror, so it could not test the claim underneath |
| **S15** | In cold, locked gradients, does life open the lock when nothing else does? | H1, H2a to H2e, in `locks/PREREGISTRATION.md` | H1 and H2a to H2d supported. H2e not: a fire and a large mineral bed opened the lock too |

## Two lines folded in on 2026-11-23

Two separate repositories had grown their own registers. Both now live here, and this page is the only register. Their old files are kept, frozen, with a note that points here.

- **S16, gradient access** (`gradient-access/`, formerly `evolutionary-gradient-access`). The successor to S15. Its job is the comparison S15 did not make: evolving against non-evolving catalysts **at equal energy and material investment**.
- **The chemistry line** (`chemistry/`, formerly `thermodynamic-emergence`). Seeded autocatalysis, mutual catalysis, and a driven open reactor with recovery. It belongs with S14: before the replicator.

Their hypothesis numbers clashed with the ones above. They are renamed here: **H16-x** for S16, **C-x** for the chemistry line.

!!! warning "Nothing below is preregistered"
    Neither line froze a preregistration before its runs. Every result below is exploratory.

### S16, gradient access

| | Prediction | Status |
|---|---|---|
| **H16-0** | Gates: conservation, detailed balance, non-negative entropy production, convergence | v0.1 **failed its own audit** ([`VALIDATION_AUDIT.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/gradient-access/VALIDATION_AUDIT.md)): reproduction cost never added up, reproductive energy from a constant instead of the actual affinity, waste species missing from exchange entropy, populations at the cap within two steps. v0.2 closes its free-energy identity |
| **H16-1** | No catalytic advantage at zero barrier; catalysis helps at high barriers | Holds in v0.1 throughput, which the audit leaves standing. Zero-barrier invariance is exact |
| **H16-2** | Evolving catalysts beat fixed and standing-variation controls matched to their size | **Not supported at comparable cost** (v0.2, exploratory). Under drift, a fixed library with the same catalyst material converted about 6.6% *more* fuel, with about 20% less work. Same direction as S15's H2e |
| **H16-3** | If oracle-assisted search matches evolution at equal cost, the advantage is adaptive search, not inheritance | Not tested at equal cost yet |
| **H16-4** | A range of drift rates exists where evolution holds access and fixed controls lose it | Partly: mutation helps late adaptation against a *small* copying population; the gap closes against a rich standing library (v0.2). **Overlaps S15's H3a.** Run once, in S16 v0.3 |
| **H16-5** | Evolution holds more of a multi-lock landscape | Not established in v0.1 |
| **H16-6** | Cumulative dissipation rises only once all costs are counted | Not tested: needs v0.3 accounting |

Next: the v0.3 equal-investment design ([`MODEL_V03_EQUAL_BUDGET_DESIGN.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/gradient-access/MODEL_V03_EQUAL_BUDGET_DESIGN.md)), preregistered before it runs.

### The chemistry line (S14 line)

| | Claim | Status |
|---|---|---|
| **C-1** | Sustained gradients support structures that would not persist without the flow | Model demonstration only. A driven open reactor holds a steady state; so does its uncatalysed null, at lower abundance |
| **C-2** | Some structures maintain themselves and recover from damage | Model demonstration only. After 99% catalyst removal the open reactor restores about 99.9% of abundance, but 1% of the catalyst survives and every species is fed continuously |
| **C-3** | Replication with heredity can arise from self-maintaining chemistry | Not tested. Same question as S14's H14a and H14b, which found no closed set possible in 0 of 200 chemistries |
| **C-4, C-5** | Information processing, then agency, become selectable | **Superseded** by links 5 and 6 on [where the hypothesis stands](standing.md) |
| **C-6** | Evolved organization changes planetary dissipation | **Superseded** by link 7 and the Planet albedo result |

The chemistry line's evidence hierarchy is worth keeping: conceptual consistency, then mechanism, model demonstration, robustness, empirical support, generalization. Evidence at one level must not be reported at a higher one. Everything in this repository is at model demonstration or below.

## Things I chose not to claim

The preregistration lists what is *exploratory*, so that no one, me included, treats it as a finding:

- That entropy-as-reward breeds "furnaces". The pilot did not show it.
- Absolute values of the capture ratio.
- Anything about prediction or world-modelling. It was not measured.
- Interactions between factors, beyond what the per-condition table shows.

## What would change my mind

I wrote this down before the run too.

- **H1 falsified.** Then the "no objective needed" claim fails in this world.
- **H2 with no factor load-bearing.** Then the grid cannot tell the conditions apart, and the next step is a harder or longer world, not a conclusion.
- **H3 falsified.** Then whatever the evolved agents have, it is not heritable. That would undercut the agency reading of the whole suite.

H1 and H3 held. H2 did not.

But notice what kind of failure it was. The second case above describes a *null*: no factor shown to matter. That is not what happened. Every factor had a *negative* effect, with its interval below zero. Removing it made big-deposit access go up.

So H2 did not land in a case I had planned for. It landed past them. S6 was built to test one explanation of it, the free-rider story. The later experiments came from related questions: whether a bigger genome helps, what an explicit entropy goal does, and whether England's argument holds in this world.

## Deviations, in the open

Two are worth knowing.

1. **The "neutral" control was not fully neutral.** In the random-parents control, parents are chosen at random among survivors. But starvation still removes genomes. So viability selection remains, and only *fecundity* selection is removed. H1 has to be read accordingly. No code changed. Comments in `src/` were corrected after the confirmatory run, in a comment-only commit.
2. **H10e was never coded into the analysis script.** I preregistered it, then did not wire it in. The number I report comes from the script's descriptive line. I recorded the omission in the file.

Neither changes a verdict. Both are the sort of thing a reader should be able to find. So they are logged, not buried.
