# Why the next experiment starts before life

!!! warning "Status: a decision record"
    This page records a decision and the reasoning behind it. It reports no result. The experiment it leads to, S14, is a [draft preregistration](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/PREREGISTRATION_S14.md). No engine exists yet. Nothing has been run.

## The proposal

Life arose in one place that we know of.

So here was my proposal. Recreate the starting conditions of that one place: the early Earth. Apply the same constraints. Apply the statistical constraint of entropy. Then watch what happens.

It sounds like the obvious next step. Is it?

Half of it is. The other half does not survive a close look.

## What the proposal gets right

Look at what S1 to S10 start with.

Agents. Genomes. A birth rule. A death rule.

I put every one of those in by hand.

So the suite never tested where selection comes from. It tested what selection does *once it already exists*. [S10](results/s10.md) took selection away, but then I wrote England's bias in as a rule. Its main effect was true by construction.

That is the gap. Everything interesting was already in the box before the run began.

The proposal goes straight at it. Start earlier. Start before the replicator.

That part stays.

## Where it breaks

### 1. Nobody knows the starting conditions

"Recreate early Earth" assumes we know what to recreate. We do not.

There is no standard model of the origin of life. There are competing hypotheses. Deep-sea alkaline vents are one candidate. Freshwater hot springs on volcanic land are another. A review that compares them says the differences between the two settings far outweigh the similarities.

So I would not be recreating a known place. I would be choosing a scenario. That is a hypothesis stacked on a hypothesis.

### 2. We could not afford them anyway

Suppose we did know.

Earth had an ocean and hundreds of millions of years. I have a CI runner.

So the model must be abstract. And here is the trouble. Every abstraction is a place where the answer can slip in unnoticed. That is exactly what happened in S10.

Moving the start line back does not remove this problem. It moves it.

### 3. One success is weak evidence

Earth shows that life can start. It does not show how likely that is.

We are here only because it worked here. A planet where it failed has no one asking the question.

There is one careful attempt to get past this. Kipping's Bayesian analysis uses how early life appears in Earth's record. It finds odds of about three to one that life starts quickly under Earth-like conditions. He calls that a nudge, not a conclusion.

I believe life arose elsewhere too. That is a belief. It has no evidence behind it, so it stays out of the design.

This has a practical cost. Suppose the simulation produces nothing. What have I learned?

Wrong conditions? Too little time? Too small a soup? Wrong idea?

I could not tell these apart. **A null from this kind of experiment is close to uninformative.** I should know that before I start, not after.

### 4. Entropy is not a constraint you add

This one matters most.

My wording was: apply "the statistical constraint of entropy". But the second law is not an extra rule to bolt on.

I have tried bolting it on. Twice.

- [S8](results/s8.md) made entropy the objective. It produced a furnace.
- [S10](results/s10.md) made dissipation an acceptance rule. It produced its own assumption.

The second law is what you get when the small-scale rules are right. Make every reaction reversible. Tie the forward and backward rates to a heat bath. Conserve energy. Supply a source of free energy from outside.

Then entropy production is something you *measure*. If the engine is honest, it comes out non-negative without being told to.

So the design rule of this repo survives, and gets stricter. Entropy is measured, never rewarded. And now, never imposed either.

One more correction, from the source. Schrödinger said organisms feed on "negative entropy". Physicists objected. In his note to Chapter 6 he concedes he should have said *free energy*. So the books should be kept in free energy.

## What already exists

Before building anything, what has been done?

**Real chemistry, no energy bill.** Wołos and colleagues encoded about 500 known prebiotic reactions and six starting molecules. Their program mapped what can be made. Self-regenerating cycles and soap-like molecules showed up within a few steps. It is a map of what is possible, not a run of what happens.

**Copying from nothing, no physics.** Agüera y Arcas and colleagues filled a soup with random programs. No fitness function. Self-replicating programs arose anyway. In one of their languages, replicators are possible and have not been seen to arise. So the substrate matters. And computation there is free. Nothing pays for anything.

**Physics, no copying.** Horowitz and England wired a chemical network at random and drove it. No replication. No selection. The network settled into rare states that were tuned to the drive. Tuned *both ways*: some coupled to it unusually strongly, some unusually weakly.

That last finding cuts against my thesis. I have been saying life is a better entropy engine. Their result says a driven system can just as well settle where it dissipates less.

Three pieces, then. I have not found work that joins them: copying that arises unaided, in a soup where every step pays an energy bill. I have not searched hard enough to say it does not exist.

## The decision

Three things were decided.

**1. Keep the move. Drop the wording.**
The next experiment starts before the replicator. It does not claim to recreate early Earth. It keeps only what every origin scenario shares: a steady source of free energy, a heat bath, material arriving and leaving.

Call it Earth's thermodynamic skeleton. Whether the skeleton is what mattered is assumed, not tested. That is limitation 1 of this repo, and it has not gone away.

**2. One rung at a time.**
The road from soup to agency has at least four rungs.

| Rung | Question |
|---|---|
| Copying | Does anything start to make more of itself? |
| Heredity | Are there different kinds, and do they breed true? |
| Selection | Do some kinds displace others? |
| Agency | Does anything restore itself after a disturbance? |

S14 asks about the first rung only. It does not measure agency at all. Each later rung gets its own preregistration, and only if the one below holds.

**3. Park S12.**
[S12](https://github.com/praveenchandrahas/agency-from-gradients/pull/2) was a sweep of the pond world's physical parameters. It starts from replicators that already exist. That is the very assumption now in question. So it is parked as a draft. It is not withdrawn.

## A note on numbering

There is no S13.

The [rebuilt thesis](thesis.md) already names a candidate hypothesis **H13**: selection produces restoration only when the selection environment contains the disturbance. An experiment called S13 would collide with it. So the new one is S14.

H13 is not replaced. It is still a candidate, and still untested.

## The case against this decision

I should write this part too.

**S14 is expensive.** It needs a new engine. The pond world cannot be reused.

**Its null tells me almost nothing.** See point 3 above.

**H13 is cheap, and it can fail cleanly.** The pond exists. The test is two arms and a common probe. A clear result either way would teach me something.

**The first rung may be the easy one.** Work on small autocatalytic networks suggests they can copy and still fail to evolve. If so, S14 could succeed and the road could still end one rung up.

So the fair summary is this. S14 asks the deeper question and risks the emptier answer. H13 asks a narrower question and risks far less.

I chose to preregister S14 first. I did not choose to run it first. That is still open.

## What would reverse it

- **A gate fails.** If the engine cannot show detailed balance, or the books do not close, there is no S14.
- **The cost is out of reach.** Then the pond experiments come first, starting with H13.
- **Someone has already done it.** Then I should read their paper, not rebuild it.

## How S14 guards against my own bias

Three rules, written into the preregistration.

1. **A positive control.** A hand-built chemistry that I know can copy. If my detector misses it, a null from the random chemistries means nothing. S9 had no such control, and paid for it.
2. **A hurricane control.** A hand-built chemistry that is driven, builds structure, dissipates, and does *not* copy. If my detector fires on it, a hit means nothing.
3. **Blind tuning.** The pond world was redesigned ten times after null pilots. Here, parameters are set using the controls only. The detector is not run on the random chemistries until the design is frozen.

## What I leaned on

- Schrödinger, [*What Is Life?*](https://en.wikipedia.org/wiki/What_Is_Life%3F) (1944), Chapter 6 and its note.
- Wolchover, "A New Physics Theory of Life", *Quanta Magazine* (2014), on England. His mathematics is generally accepted. His reading of it is the open question.
- [Entropy and life](https://en.wikipedia.org/wiki/Entropy_and_life), Wikipedia, on the absence of a standard model. Its [Talk page](https://en.wikipedia.org/wiki/Talk:Entropy_and_life) is thin at present. One comment there calls the article outdated pop science. I take that as a warning for this page too.
- Longo and Damer (2020), [Factoring origin of life hypotheses into the search for life](https://doi.org/10.3390/life10050052), *Life* 10, 52.
- Kipping (2020), [An objective Bayesian analysis of life's early start and our late arrival](https://arxiv.org/abs/2005.09008), *PNAS*.
- Wołos et al. (2020), [Synthetic connectivity, emergence, and self-regeneration in the network of prebiotic chemistry](https://doi.org/10.1126/science.aaw1955), *Science* 369.
- Agüera y Arcas et al. (2024), [Computational Life](https://arxiv.org/abs/2406.19108).
- Horowitz and England (2017), [Spontaneous fine-tuning to environment in many-species chemical reaction networks](https://doi.org/10.1073/pnas.1700617114), *PNAS* 114.
- Vasas, Szathmáry and Santos (2010), [Lack of evolvability in self-sustaining autocatalytic networks](https://pmc.ncbi.nlm.nih.gov/articles/PMC2824406), *PNAS*.

The one-line version:

> Start before life, but do not pretend to rebuild the Earth. Build a soup that pays its energy bills, and ask one small question of it.
