# Where the hypothesis stands

!!! warning "Status: a record, as of 2026-11-23"
    This page reads every result so far against the hypothesis, one link at a time. It adds no new numbers. Each number comes from a results page linked beside it.

    It ends with a **proposed** revision of the hypothesis. The proposal is not adopted. The hypothesis is the author's to change.

## Why this page

The hypothesis is spread across several pages. [The idea](idea.md) tells it as a story in four steps. [Starlight](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/starlight/README.md) breaks it into a chain of five links. [Locks](locks.md) went underneath both and tested the claim they rest on.

Results have piled up since each page was written. Some links held. Some didn't. One was never true in the form I wrote it.

So here is the whole chain, with the evidence next to each link.

## The chain, link by link

| | Link | Verdict now |
|---|---|---|
| **1** | Free energy flows from stars | **Corrected.** Mostly from gravity and fusion. Starlight is one source, and an unlocked one |
| **2** | Structures that drain gradients persist | **Holds, in the weak form.** Structures persist when they pay their bills. A good-enough drain survives, not the best |
| **3** | Life drains energy that nothing else can | **Failed in its testable form.** Life does best, but not alone. What only life does is improve |
| **4** | Such structures evolve to capture more | **Holds for one lineage. Fails for the whole.** Individual gain can shrink the total |
| **5** | The behaviour that captures more is agency | **Conditional.** Behaviour evolves only when the world moves |
| **6** | Because more capture means more entropy, and the Universe favours that | **Rejected as a cause.** Entropy follows. It is not selected |
| **7** | Any structure that lowers local entropy eventually raises global entropy more | **True in flow settings, by bookkeeping. Not a general law** |

### Link 1. Where the free energy comes from

I used to say starlight. That was wrong.

Black holes shine on gravity, not starlight. Infalling matter heats up and radiates. That releases roughly 6 to 40% of its rest mass as energy. Fusion releases about 0.7%. Stars themselves run on gravity switching fusion on.

Both trace back to the low-entropy start of the universe. Matter began almost perfectly smooth, which for gravity is low entropy. And most of it was left as unfused hydrogen. Those are the two great locked gradients.

On Earth, too, not everything is sunlight. Hydrothermal vents run on the planet's internal heat.

There is a second problem with starlight. It is an *unlocked* gradient. Any dark rock absorbs it and turns it into heat. So it is the worst place to look for something only life can do. [S15](results/s15.md) confirmed it: with no lock, life added nothing.

### Link 2. Structures that drain gradients persist

This holds. But in a weaker form than "each exists *because* it is a good drain."

- In [S15](results/s15.md), a fire with a fixed key persisted on cold fuel, as long as its starting key was good enough. It never got better. It didn't need to.
- In [S14](results/s14.md), a mineral-catalysed structure persisted while driven, and came back at once after being wiped.
- [Horowitz and England](before-life.md) found driven networks settling at *both* extremes: some coupled strongly to the drive, some sheltered from it.

So persistence asks for a drain that pays its bills. Not the best drain. Survival is a threshold, not a ranking.

### Link 3. Life drains energy that nothing else can

This is the claim underneath everything. It was tested directly in [S15](results/s15.md).

**The broad version was already false.** Stars and black holes are not passive, and they produce far more entropy than any biosphere. [S11](results/s11.md) found the same: in a lifeless universe, the entropy-maximal structure is a black hole.

**The narrow version also failed.** "In cold, locked gradients, life opens the lock, and nothing else does."

| At the coldest barrier | Key length 24 | Key length 32 |
|---|---|---|
| Life beats the fire | +262 [214, 311] | +603 [384, 817] |
| Life's lead grows with the barrier | Yes | Yes |
| Fire, as a share of the best possible | 0.78 | 0.14 (inconclusive) |
| A mineral bed 100 times bigger | Matches life | Matches life |

Life did best. But a fire and a big enough rock surface opened the lock too.

The [S14 re-check](results/s14.md#addendum-2026-11-23-mixing-entropy) points the same way. With mixing counted, the copier out-dissipates the mineral by about 3%. Better, but not in a different class.

**What survives is narrower:**

- **Only life improved its key.** The fire kept exactly its best starting key, in all 20 worlds. Life climbed to the perfect key in every world it survived.
- **Life needs a foothold.** At key length 32, life never survived where the fire died. Not once in 20.

Both of those were seen after the run. They are leads, not findings.

### Link 4. Such structures evolve to capture more

This holds for a single lineage. It fails for the whole.

- **For a lineage, yes.** In [Starlight](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/starlight/RESULTS.md), the absorber converged to the best capture from both starts. In S15, life drove a locked fuel to 97% spent, the same as the designer.
- **But not always.** In Starlight, where sensing was optional, lineages that could sense captured slightly *less*. Selection did not maximise capture there.
- **And not for the whole.** In Planet (draft PR #7), agents carrying agency took over from 50/50, and the planet's throughput fell: 43.9 TW in the mixed world, against 134.7 for non-carriers alone. The winner shrank the pie.
- **Not in the ladder world.** In S1 to S4, evolved populations reached the big deposits in 27% of runs and took 2% of their energy from them. A hand-coded forager took 50%.

That last link matters for the Kardashev framing. Kardashev is about the total. The only experiment that measured the total found individual advantage lowering it.

### Link 5. The behaviour that captures more is agency

Conditional.

- **Behaviour evolves when it is needed, and only then.** In Starlight, movement evolved once the light moved (+0.80). Sensing evolved when the light moved fast (0.71), and was purged when it didn't (0.10).
- **When it isn't needed, it isn't kept.** Same experiment.
- **Sensing paid without steering.** In Planet, carriers picked the best neighbour 95 to 99% of the time with almost no sensing. Sensing paid through a bonus, not through better choices.
- **Agency was weak in the ladder world.** H2 failed in the wrong direction, and S6 to S10 did not rescue it. See the [thesis](thesis.md).

So "behaviour that captures more" appears when the source of energy moves. In a still world, there is nothing to behave about.

### Link 6. Because the Universe favours entropy

Rejected as a cause. Five times.

| | What it showed |
|---|---|
| [S8](results/s8.md) | Rewarding entropy directly made a furnace: 35.8 against the forager's 29.0, with less use of the big deposits |
| [Starlight](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/starlight/RESULTS.md) E3 | A heritable heat-wasting furnace drifted when free (0.50) and was purged when it cost something (0.13). Selection gave up 32 units of heat per step to save a small running cost |
| [S10](results/s10.md) | Imposing dissipation made the system absorb more. It did not climb |
| [S11](results/s11.md) | A pure entropy maximiser builds black holes, not life |
| [S15](results/s15.md) | Entropy tracked fuel spent, by bookkeeping. Life won by spending, not by dissipating as such |

Entropy is what happens when a structure pays its bills. It is not what the structure is selected for.

### Link 7. Lowering local entropy eventually raises global entropy more

True in the setting we tested. Not a general law.

In a flow reactor with a locked fuel, every structure that spent fuel raised total entropy production above the passive world. [S15](results/s15.md) showed it for the fire and for life, and the S14 re-check for the copier and the mineral. Once mixing is counted, more fuel spent means more entropy. That is bookkeeping, and it holds.

But two things limit it.

- **Boundary conditions.** Under a fixed flow of energy, like sunlight on a planet, structure can *lower* entropy production. Convection does: it carries heat faster, so the temperature difference shrinks. No experiment here tests that case.
- **Counting.** In S15 and S14, counting reactions alone ranked better catalysts *lower*. A claim about "more entropy" is only as good as its books.

## A pattern across the results

Three results from three different worlds point at one variable.

- **Starlight:** behaviour evolved only when the light moved.
- **S15:** what only life did was *improve* its key. In a static lock, improving pays little: a fire with a decent key, or a big enough rock, gets most of the way.
- **The ladder world:** the [thesis](thesis.md) already proposes H13. Restoration is selected only when the selection environment contains the disturbances.

The common thread: **what heredity with variation adds pays off when the world changes.**

I saw this after the fact, across experiments not designed to test it. So it is a lead. Two preregistered tests can check it:

- **S15 H3a, the drifting lock.** A fixed key goes stale. Life's key should follow.
- **H13, static against variable selection,** in the ladder world.

## Lessons for method

These are now part of how every experiment here is built.

1. **The passive baseline must absorb.** Starlight's lifeless world was a mirror, so life beat a mirror. A dark rock is the honest baseline.
2. **Count all the entropy.** In a flow system, that means mixing as well as reactions. Leaving it out reversed the copier-against-mineral comparison in S14, and ranked 500 perfect catalysts below 100 in S15's pilot.
3. **Match the controls.** S14's mineral level was a number I chose, so its comparison meant nothing. S15 matched the mineral to life's catalyst count.
4. **Write the expectations down first, from arithmetic.** S15's outcome was visible in the arithmetic before anything ran. That is good for the engine. It is also a warning about how much a toy model can tell us.
5. **Report two horizons.** Planet's generation 220 was the bottom of a dip.

## A proposed revision

!!! note "Proposed. Not adopted."
    This rewrites the chain to fit the evidence above. Whether to adopt it is the author's decision. If adopted, [the idea](idea.md), the [Starlight README](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/starlight/README.md), the repo README and the paper would change to match.

> Free energy is locked up in gradients, mostly by gravity and unfused hydrogen.
>
> Structures persist when they drain a gradient well enough to pay their bills. Living and non-living structures both do this. Entropy production follows. It is a consequence, not the thing selected.
>
> What heredity with variation adds is **improvement**. A lineage can refine how it drains a gradient. A fire or a rock cannot.
>
> Improvement pays most when the world changes. Agency-like behaviour is what improvement looks like when the gradient moves.

What this drops:

- "Life drains energy that nothing else can."
- "The Universe favours entropy."
- "Starlight is the source."

What it keeps:

- Persistence selection, with entropy measured and never rewarded.
- Succession, in a smaller form: life gets in where something non-living already holds the lock slightly open.

What it adds, to be tested:

- Change in the environment as the load-bearing condition.

## Not yet updated

- **The paper.** It lives in its own repository, `dissipative-agency-simulation`, outside this one. Its claims about capture, succession and the Kardashev scale should be read against links 3, 4 and 6.
- **Planet** (draft PR #7) is still open. Its results are cited here from the draft.
- **S14's other arms** (random, no-catalysis, day/night) still count reactions only.
- **The blog post** "Did starlight make us smart?" predates S15.

## What would change this page

- **H3a.** If life's key does not track a drifting lock better than the fixed arms, the "improvement" reading weakens badly.
- **An aggregate test.** If a population-level experiment shows heredity raising *total* capture, link 4 recovers.
- **A fixed-flux test.** If structure raises entropy production under a fixed energy flow too, link 7 is broader than stated.
