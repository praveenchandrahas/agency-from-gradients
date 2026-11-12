# Known limitations

If you read one page of this site critically, make it this one.

I list these because I would rather you find them here than discover them later and wonder what else I left out.

## The nine

### 1. A toy world, with one abstraction

Whether these five features are what mattered on Earth is **assumed, not tested**. Everything else rests on that.

### 2. The default policy has a strong prior

The default policy has about 27 parameters, with shared weights across directions. It is shaped like chemotaxis. A generic neural net did not evolve useful behaviour in the available budget.

So "agency emerged" here means *a small, well-shaped policy was tuned by selection*. That is a much weaker claim than emergence from nothing.

### 3. The capture ratio is largely an accounting identity

It depends on an assumed kappa. Roughly, it is \(1 + (\kappa - 1)f\). S3 includes a \(\kappa = 1\) row as a sanity check. The empirical quantities are the capture fraction and the tier shares.

### 4. Viability restoration is not prediction

And the raw evolved-versus-random gap is inflated by survivorship. Only the full-versus-no-heredity contrast is interpretable. S9 added a second confound: the random baseline moves when the learning rule changes.

### 5. The ladder is held fixed

Removing it would make climbing it false by construction. Its necessity is only probed by the S3 no-ladder control, and that is not a test of agency.

### 6. The drift control is not fully neutral

Parents are random among survivors, so starvation still filters genomes. Only fecundity selection is removed. H1 therefore measures the effect of fecundity selection on top of viability selection.

### 7. S8's objective is an assumption wearing a measurement's clothes

Entropy counts agent dissipation at kappa times passive leakage. So capturing energy is rewarded by construction. And a shared controller sidesteps the cooperation problems that individual selection faces.

### 8. World v2 is untested at scale

The large-genome pilots, and then the S7 run, did not show the behaviour the thesis predicts. I do not know whether that is the world, the mutation model, the population size, or the number of generations. The S7 package also bundled five changes, so it cannot say which.

### 9. The extrinsic death hazard is a built-in selection pressure

It was needed to get enough generations per run. But it is itself pressure, not neutral background.

## Five more, from later work

### 10. S7-v3 extinction

Most big-genome runs died out, so their metrics come from truncated runs. My preregistration did not say how to treat extinct runs. That is a gap.

### 11. The S9 predictive probe has no positive control

A null result cannot separate "no predictive information" from "the probe is too weak".

### 12. S11 excludes life by assumption

So it cannot say whether life raises entropy. And the result is a consistency check on published formulas, not a discovery.

### 13. S14's null is structural

In none of its 200 random chemistries was a closed catalytic set even possible. So S14 says nothing about whether copying would arise where one is possible. The catalysis density was my choice, and it sat just under the threshold.

### 14. S14's soup is a toy

Strings of at most six letters. A random catalysis table. Catalysts that never saturate. Tau-leaping, checked against the exact method only at equilibrium.

## Design bias, stated plainly

The world went through ten design changes, each forced by a pilot that showed a null. That makes the final design friendlier to selection than a blind one would have been.

H2 failing *anyway* is some evidence the tuning did not simply guarantee the thesis. Some. Do not lean on it.

## Not done

- **S5**, Barrow's counter-test for an efficiency pathway. Not implemented.
- **S0** on the real earlier genome trajectories. Never run on the real files.
- **A predictive-information probe** with a positive control.
- **Kin sharing, larger populations and sexual recombination** as fixes for the big deposits, if they are still not found under individual selection.
- **A gentler v3.** Viable seeding, an easier start, or a curriculum from v1 to v3. Each would be a new preregistered test.
