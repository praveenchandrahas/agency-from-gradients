# World v2

## Why a second world?

The main run failed. Evolved populations mostly ignored the big deposits.

An obvious objection followed. A few dozen genes is too small. Agency will never evolve from that. Give it more.

Fair point. So I built v2.

!!! note "Nothing in v1 changed"
    v2 is off by default. `Config(world_v2=True)`, or the helper `v2_config()`, switches it on. A test confirms the default v1 results are unchanged, bit for bit. The first 37 observation channels are identical, so the hand-coded forager still runs.

## What v2 adds

| Addition | Detail |
|---|---|
| **A recurrent policy with memory** | About 2,070 genes. Also `mlp2` (about 1,400, feed-forward) and `equivariant2` (29 genes, the small control on the same world) |
| **Heritable body traits** | Body size, which scales metabolism and bite size. And a reproduction-threshold multiplier |
| **Seasons** | Commons regrowth rises and falls over time |
| **Walls** | Impassable line segments. A move into a wall is blocked. You still pay for it |
| **Danger zones** | Discs with extra death risk |
| **A pheromone channel** | A seventh action that leaves a signal. It decays and diffuses. Other agents can sense it. It costs energy |
| **Two-scale mutation** | Frequent small changes plus rare big ones |
| **Scaling** | `v2_config(scale=k)` multiplies the torus side by `k` and keeps density constant |

The pheromone is *information*, not energy. It is not in the ledger. The energy ledger still closes through every option, and the tests check it.

## v3: the combined package

v3 stacks more on top, for the S7 confirmatory run:

- A 96 by 96 arena (scale 3)
- A day and night cycle
- A drifting resource field
- Danger zones that wander
- **Recombination**, using block crossover with a nearby neighbour
- A **5x lower mutation rate**
- A larger genome of about 5,300 genes

Five changes at once. So if it worked, I could not say which part did the work. As it turned out, it did not work. [See S7](results/s7.md).

## What the pilots said first

Before the confirmatory run, two small pilots tried the 2,070-gene policy.

- **4 seeds, 100,000 steps.** About 650 generations. The big policy did not find the big deposits. It did worse than the 29-gene policy on the same world.
- **2 seeds, 200,000 steps, 4x area.** About 1,780 generations. Both policies reached big deposits. The recurrent policy still scored *below* the small one: tier-2 share 1.6% against 6.3%.

These are pilots. Two to four seeds. Mutation rates not tuned. They say nothing about the thesis.

They do say one thing. In this world, a 2,000-gene policy with no prior and about 1,800 generations is not enough to beat a 29-gene policy with a chemotaxis-shaped prior.

Candidate reasons, all untested:

1. About 40 point mutations per child, mostly harmful in a large recurrent net.
2. No recombination.
3. Selection pressure on any single gene is very weak.
4. A world where the payoff for investing cannot be learned by gradual mutation.

Items 1 and 2 are exactly what v3 tried to fix.
