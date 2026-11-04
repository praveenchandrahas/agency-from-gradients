# S1 to S5: the main run

30 seeds per cell. 20,000 steps. Exactly as preregistered. Intervals are 95% bootstrap CIs.

!!! abstract "The headline"
    The thesis, as preregistered, is **only partly supported** in this world. Its central ablation prediction, **H2, failed**.

## The scorecard

| | Prediction | Result | Verdict |
|---|---|---|---|
| **H1** | Persistence selection raises entropy production over random parents | +2.34 [1.08, 3.66] (27.3 vs 24.9) | **Supported**, small effect |
| **H2** | Scarcity, heredity and mortality are each needed for big-deposit access | See below | **Falsified** for all three |
| **H3** | Heredity contributes to recovery from displacement | Full minus no-heredity: +0.220 [0.189, 0.249] | **Supported**, with a caveat |
| **H4** | Rewarding entropy directly does not beat persistence on big-deposit access | -0.10 [-0.30, 0.10] | **Not falsified** |
| **H5** | Accounting check: capture ratio at kappa = 1 in 0.7 to 1.15 | 1.080 [1.017, 1.143] | **Passes**, barely |

**H2 in numbers.** All-on minus factor-off, for access to the big deposits:

| Factor removed | Effect |
|---|---|
| Scarcity | -0.27 [-0.50, -0.03] |
| Heredity | -0.73 [-0.90, -0.57] |
| Mortality | -0.53 [-0.73, -0.33] |
| Succession | -0.10 [-0.33, 0.13], not shown |

Read the sign. Negative means: with the factor *off*, access was *higher*. Removing any of the three made evolved populations reach big deposits *more* often.

![H2 leave-one-out: every removable condition has a negative effect](../figures/s2_leave_one_out.png)

## Is the world broken?

First question I asked. If even a hand-coded expert cannot do well, the world is just bad.

It is not.

- **The hand-coded forager** reaches big deposits in 100% of runs. It gets 50% of its energy from them. Its entropy rate is 37.1.
- **Evolved populations** reach big deposits in 27% of runs, and get 2% of their energy from them. Their entropy rate is 27.3.

So there is headroom. Selection moved things a little. It left most of the available gain unused.

## What the results do and do not say

### H1 is weaker than it looks

Two reasons.

- The random-parents control still has viability selection. So H1 measures fecundity selection *on top of* it.
- Rewarding plain grass-eating (26.5) also appears to beat random parents. I did not compute an interval for that contrast. So the gain is not specific to persistence.

"Persistence versus a task reward" was not a preregistered contrast. I cannot claim it either way.

### H2 failed. Why? A guess.

My explanation is a **free-rider problem**. And I want to be clear: it is post hoc and untested.

Opening a deposit costs the investor energy. The payoff is shared with everyone on the square. When starvation is fatal and genomes are inherited, evolution seems to select *against* paying the cost. In the one evolved world I inspected, the creatures avoided deposits.

The data are consistent with this.

- With scarcity and mortality on, fresh random genomes reach big deposits in 100% of runs. Inherited ones, 27 to 37%.
- Removing mortality, which means bailouts, lifts the tier-2 energy share from about 4% to 30 to 35% under scarcity.

But be careful. `t2_reached` only means a site was *ever* fully open. It does not mean anyone used it steadily. The tier-2 energy share is low in *every* mortal cell, 1.4 to 5.9%.

So treat the mechanism as a hypothesis. [S6](s6.md) is the test. It came back negative.

### Entropy rate is not comparable across S2 cells

Abundant-food and no-mortality cells fill the population cap of 200. Their entropy rates run 90 to 130. The scarce, mortal cells sit at 27 to 33.

That is population size. It is not agency. Do not rank the cells by it.

### H3 is narrower than "agency"

Recovery needs heredity. Full minus no-heredity is 0.22.

But random-parents selection gives almost the same gain: 0.259, against 0.270 for persistence. So what is inherited is mostly *better grass-foraging, filtered by starvation*. It does not need selection by surplus.

The raw evolved-minus-random gap is also inflated by survivorship. That is why the preregistered quantity is the *contrast*.

### Succession did not help

The ladder without succession had a *higher* entropy rate (33.0) than the full ladder (27.3). Its big-deposit rate was also nominally higher (0.37 against 0.27).

The preregistered succession effect on `t2_reached` is not shown, because its interval includes zero.

### Not tested

- Whether any of this transfers to Earth.
- Whether a less-biased policy class would behave differently. The generic neural net did not evolve.
- Barrow's miniaturisation counter-argument (S5).
- Prediction.

## The figures

![S1: four selection rules compared](../figures/s1_selection.png)

![Entropy production and big-deposit share over time](../figures/trajectories.png)

![All 16 combinations of the four conditions](../figures/s2_heatmap.png)

![S4: recovery after displacement](../figures/s4_recovery.png)

![S3: accounting and ladder controls](../figures/s3_accounting.png)

![World snapshots](../figures/world_snapshots.png)

## Notes from the pilot

Seeds 1000 to 1003. Not confirmatory.

- The pilot suggested entropy-as-reward would not breed more entropy than persistence. The confirmatory run agrees. H4 was not falsified.
- The world went through ten design changes because early pilots showed nulls. A world tuned until selection beats random parents tends to make selection beat random parents. Weigh H1 with that in mind.
