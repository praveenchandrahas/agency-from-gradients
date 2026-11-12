# Pre-registration S14: before the replicator. Does a driven soup start copying itself?

**Status: FROZEN.** Written and committed to `main` BEFORE the confirmatory run. Pilots (seeds 1000 and above) are not evidence. They were seen before freezing and are described below.

The engine is `src/agency_gradients/soup/`. The script is `src/agency_gradients/experiments/s14_soup.py`. Any place where the code departs from this file goes in the deviation log before results are reported.

**On the number.** There is no S13. `H13` is already taken: `docs/thesis.md` uses it for the static-versus-variable hypothesis. That one is still a candidate and still untested. This file is S14 so the two cannot be confused.

The reasoning that led here is in `docs/before-life.md`.

## Why

S1 to S10 all start with agents, genomes, birth and death. I built those in by hand.

So the suite has tested what selection does once it exists. It has never tested where selection comes from.

S14 moves the start line back. No agents. No genomes. No birth rule. No fitness. Only chemistry, a heat bath, and a source of free energy.

The question is the first rung, and only the first rung. **Does anything in such a soup start to copy itself?**

## What S14 is not

- **It is not early Earth.** Nobody knows the starting conditions well enough to recreate them. There is no standard model of the origin of life. Vents and hot springs are both live candidates, and they are chemically different places. So S14 does not model a place. It keeps only what every candidate shares: a steady source of free energy, a heat bath, a way for material to arrive and leave.
- **It is not real chemistry.** The molecules are strings. The energies are drawn at random. Work that uses real prebiotic reactions exists (Wolos et al. 2020) and S14 does not compete with it.
- **It does not test agency.** Agency is not measured here at all. S14 is one rung of four: copying, then heredity, then selection, then agency. Each later rung gets its own preregistration, and only if the rung below holds.
- **It cannot say anything about how likely life is.** Earth is one success, observed by the success. A hit here shows a possibility in a toy chemistry. A miss shows nothing about Earth.

## The design rule, restated

Entropy production is **measured**. It is **never imposed**.

S8 rewarded entropy and got a furnace. S10 wrote England's bias in as an acceptance rule, so its headline effect was true by construction.

S14 does neither. Every reaction is reversible. The forward and backward rates obey detailed balance against a heat bath. Given that, the second law is not a rule in the code. It is something the code has to *exhibit*. If it does not, the engine is wrong and nothing is reported.

Schrödinger conceded in his note to Chapter 6 that the right ledger is free energy, not "negative entropy". S14 keeps its books in free energy.

## Decisions settled before freezing

Decided by the author:

- **S14 runs before H13.**
- **Cycling is exploratory**, not a primary factor.

Taken as drafted. The author did not change them and asked for the run:

- **Catalysis is random only.** No template arm.
- **The emergence thresholds** stay as drafted, and so does the bound of 0.05 in H14a.
- **Size:** two letters, maximum length 6.

## The model

Energies are in units of kT. The temperature is fixed. That is the heat bath. Time is in residence times (one over the dilution rate).

### Species

- **Polymers.** Every string over the alphabet {a, b} of length 1 to 6. That is 126 species.
- **Fuel F and waste W.** F carries free energy. W is what is left when it is spent.
- **Food.** The monomers `a` and `b`, and F. Food arrives from outside. Nothing else does.

### Free energies

- A monomer has free energy 0.
- A polymer's free energy is the sum of its bond energies. There are four bond types (aa, ab, ba, bb). Each has an energy drawn once per chemistry from a normal distribution, mean +4, spread 1.
- So joining two pieces is uphill, as condensation is in water. With no drive the soup sits near all-monomer. That is Schrödinger's decay to equilibrium.
- F sits above W by Δμ. **That gap is the drive.**
- Free energies are quoted at a reference count of 1,000 molecules. That is also the level at which each monomer is fed.

### Reactions

There are 516 join sites: every way of cutting every polymer in two.

| | Reaction | Free energy change |
|---|---|---|
| 1 | x + y ⇌ xy (join or cut) | the energy of the new bond |
| 2 | x + y + F ⇌ xy + W (fuel-coupled join) | the bond energy minus Δμ |
| 3 | F ⇌ W (leak) | minus Δμ |

Every reaction runs both ways. For each, the forward rate constant over the backward one equals exp(−ΔG). That is the whole of the thermodynamics. Nothing else is added.

**How the ratio is split.** A step that goes downhill is attempted at the full rate. A step that goes uphill is slowed by exp(−ΔG). Either way the ratio is exp(−ΔG).

### Catalysis

- A catalyst speeds a reaction **in both directions by the same factor**. It never shifts an equilibrium.
- Only polymers of length 3 or more can catalyse. Food never does.
- Which polymer catalyses which reaction is drawn at random, once per chemistry. One draw for plain joins, a separate draw for fuel-coupled joins. The probability is 1 in 516 per polymer per site, so a polymer catalyses about one reaction of each kind on average.
- The speed-up grows in proportion to how much catalyst there is.
- Without a catalyst, a fuel-coupled join is a thousand times slower than a plain one.

That last line is an assumption, and I want it on the table. **The drive is hard to reach.** Fuel flows past and mostly leaves unspent, unless something in the soup learns to tap it. This is the gradient ladder of the pond world, restated as chemistry. Horowitz and England made the same design choice.

### The reactor

- Well mixed. Fixed volume.
- Food flows in at a fixed rate. Everything flows out at the same dilution rate.
- Washout is the only removal. There is no death rule.
- **At zero drive the feed carries F and W in equal parts.** That is their equilibrium ratio, so the feed itself holds no free energy. At any positive drive the feed is pure F.
- The run starts with the feed mixture and nothing else.
- Simulated molecule by molecule, by tau-leaping. Reaction counts are Poisson, washout is binomial. A step that would make any count negative is halved and redrawn, so every count stays a whole number and every ledger is exact. The exact (Gillespie) method is in the code and is used to check the leaping.

Why molecule by molecule? Because in a smooth model every possible product exists at once, in some tiny amount. Nothing ever has to *happen first*. Schrödinger's first chapter is about exactly this: with few molecules, chance rules. The first catalyst is a rare event, and I want it to be one.

### One chemistry, one seed

A "seed" here is a whole chemistry: its bond energies and its catalysis table. The randomness that matters is which chemistry you got, not which run of it.

## Parameters (frozen)

| Parameter | Value |
|---|---|
| Alphabet, maximum length | {a, b}, 6 |
| Bond energy: mean, spread | +4, 1 |
| Drive Δμ | 0, 4, 8, 12 |
| Reference count | 1,000 |
| Feed level: each monomer, fuel | 1,000 and 2,000 |
| Dilution rate | 1 (this sets the unit of time) |
| Base attempt rate of a plain join or cut | 0.1 per residence time |
| Catalytic speed-up | 1,000 times, per catalyst at the reference count |
| Uncatalysed fuel-coupled join, relative to plain | 10^-3 |
| Leak, F to W | 0.01 per residence time |
| Catalysed reactions per polymer, per kind | 1 on average (probability 1/516 per site) |
| Run length | 400 residence times |
| Late window | the last 100 |
| Tau-leap accuracy, largest step | 0.03, 0.05 |

**Why these values.** Each was set by arithmetic or by the control arms. None was set by looking at arm R.

- *Bond energy +4.* With +2, a no-drive soup would hold a large share of its mass in polymers at equilibrium. With +4 the equilibrium share in polymers of length 3 or more is about 0.4%. "No drive, no structure" then means something.
- *Drive 4, 8, 12.* One, two and three times the mean cost of a bond. At 4 the fuel just pays for a bond. At 12 it pays three times over.
- *Rate 0.1 and speed-up 1,000.* Together they mean one catalyst molecule, with food at its feed level, turns over about 100 times per residence time. That is enough for the designed copier in arm P to grow from a few molecules. And with no catalysis the background makes any given trimer roughly once in 170 residence times: often enough that a run will try it, rarely enough that a wiped copier stays wiped for a while.
- *The draft said speed-up 10^4 and bond energy +2.* Both changed, for the reasons above.

## Arms

| Arm | What it is | Runs |
|---|---|---|
| **R** | Random chemistries. The treatment | chemistries 0 to 199, at each of the four drives: 800 |
| **N** | The same chemistries with all catalysis deleted | chemistries 0 to 199, at each drive: 800 |
| **P** | Positive control. A hand-built chemistry with one designed self-copier | 10, top drive |
| **M** | Mineral control. The same designed reactions, but catalysed from outside | 10, top drive |
| **C** | *Exploratory.* Arm R's chemistries under a day-and-night feed | chemistries 0 to 199, top drive: 200 |

**Arm P in detail.** All four bond energies are +4. The copier is the tetramer `aabb`. It catalyses the three fuel-coupled joins that build it: a + a, then aa + b, then aab + b. Nothing else is catalysed. The run is seeded with 20 copies of it. Without the seed it would almost never arise by chance within a run. So P shows that copying is *possible* here and that my detector can see it. It does not show that copying *arises*.

**Arm M in detail.** The same three joins, catalysed by an outside species held at a fixed level of 200. The soup cannot make it and cannot lose it.

P is the hand-coded forager of this world. M is the hurricane. It is driven. It builds polymers. It dissipates. It does not copy. My detector must say so.

S9 taught me this the hard way. A probe with no positive control cannot tell "nothing there" from "probe too weak".

Seeds 1000 and above are for plumbing only and are never reported as evidence.

## The tuning rule

The pond world went through ten design changes, each forced by a pilot that showed a null. That biased the design toward the thesis. I do not want to repeat it.

So:

- Parameters were chosen using **arms P, M and N and the gates only**.
- Arm R pilots were allowed for crashes, runtime and the ledger. **The emergence detector was not run on arm R before the confirmatory run.**
- Arm R runs once.

## Gates

If any gate fails, no S14 result is reported.

1. **Detailed balance.** A closed box, no flow, fuel and waste at their equilibrium ratio, at drive 0 and at drive 8. The dimer count must settle within 10% of the Boltzmann prediction. Entropy production in the late window must be zero within noise (|z| below 4).
2. **Ledger.** Monomer mass in, out and held must balance exactly. So must fuel: every F that enters is captured, leaked or washed out unspent. The free-energy books must close to 10^-6.
3. **Second law, exhibited.** Three parts.
   (a) For every reaction channel and for single events, the log of forward rate over backward rate must equal the drop in the soup's free-energy function. Error below 10^-8. This is the precise statement that the rates are thermodynamically consistent.
   (b) In the control arms, entropy production computed from the reaction fluxes must agree with the free-energy books within 5%.
   (c) In no run may the late-window entropy production be significantly negative (z above −4).
4. **No drive, no structure.** At Δμ = 0, the late polymer fraction in arm R must not exceed the equilibrium prediction, within noise. Tested two ways: the mean excess over the 200 chemistries is not above zero by more than 3 standard errors, and no single run exceeds twice its equilibrium value plus 0.005.
5. **The detector works.** It fires in at least 8 of 10 runs of arm P. It fires in at most 2 of 10 runs of arm M.

## Measures

- **Capture fraction, C.** Of the fuel that flows in, the share spent through fuel-coupled reactions. The rest leaks or leaves unspent. This is "sunshine used or wasted" for the soup.
- **Entropy production rate.** The drop in the soup's free-energy function caused by reactions, per residence time, in k_B. No kappa. No accounting weight. This fixes limitation 3 of the pond world.
- **Polymer fraction.** The share of monomer mass held in polymers of length 3 or more.

All three are taken over the late window.

### The emergence criterion, E (per run)

Both parts must hold.

**(i) Closure.** Take the reactions and species actually active in the late window. A join site counts as active if its net flux is at least one event per residence time, and it is taken in its net direction. A catalyst counts if its mean count is at least one molecule. The active, catalysed reactions must contain a self-sustaining autocatalytic set, in the sense of Hordijk and Steel: every reaction in the set is catalysed by a member of the set, and every member can be built from food through the set. The set must include at least one fuel-coupled join running forward.

**(ii) History.** At the start of the late window, copy the run. In the copy, delete every polymer of length 2 or more. Keep the food and the waste. Let it run on for 100 residence times with a fresh random stream. Call it the **sterilised twin**. The twin's polymer fraction must stay below half the intact run's late-window value for at least 10 residence times.

Why the second part? Because it is what separates a copier from a hurricane. Wipe a hurricane's products and they are back at once, because the cause is outside. Wipe a copier and it stays gone until chance makes the first one again. Its presence now depends on its presence before. That is the smallest thing I am willing to call copying.

The thresholds are judgements. So I also report E with the activity cut-offs halved and doubled, with the twin fraction at 0.25 and 1.0, with the lag at 5 and 20, and by closure alone.

## Hypotheses

Intervals are 95% percentile bootstraps over chemistries, 4,000 resamples. Where a chemistry contributes more than one run, whole chemistries are resampled. A hypothesis is *supported* only if its interval excludes the stated bound in the stated direction.

**H14a. Copying appears.**
In arm R at the top drive, the E rate has a lower bound above 0.05. More than one random chemistry in twenty.
*Why this bound:* a judgement. I also report against 0.01 and 0.10.

**H14b. More drive, more copying.**
The E rate at drive 12 minus the E rate at drive 4 is above 0. Paired by chemistry.
*Why:* the conditional thesis says the flux matters. This is the nearest thing here to the S12 sweep.

**H14c. Copiers spend the fuel. (Check, expected by construction.)**
For arm R runs at a positive drive that meet E: C in the intact run minus C in its sterilised twin, over the twin's lag, is above 0.
*Why it is only a check:* bonds are uphill. Nothing can hold polymers away from equilibrium without spending fuel. That is the second law, and Schrödinger's point. It is not evidence for anything of mine.

**H14d. Copiers are tuned to the drive.**
For each arm R run at a positive drive that meets E, take its mean late-window counts. Shuffle them among polymers of the same length, 1,000 times. Each shuffle keeps the mass and the length profile and scrambles *which* polymers are there. Compute the instantaneous fuel-spending rate for the real state and for each shuffle. Let q be the real state's percentile.
Supported if the mean q is above 0.5. I also report the share with q above 0.95 and below 0.05.
*Why:* this is the claim that can hurt. "Life is a better entropy engine" predicts q high. Horowitz and England found driven networks settling at *both* extremes, strongly coupled and weakly coupled. A mean q below 0.5 would say the copiers that arise here are the ones that shelter from the drive.
*A caveat I can see already:* criterion (i) requires a fuel-coupled reaction in the set. That tilts q upward. So a high q is weaker evidence than a low one.

**If fewer than 5 runs meet E, H14c and H14d are declared not run.**

## My expectations

Written after the pilots below and before the confirmatory run.

- **H14a: leaning not supported.** This changed from "open" in the draft. The reason is arithmetic, not data. A closed set here needs at least a trimer and the dimer under it. That is two or more fuel-coupled joins, each catalysed by a member of the same set. With one catalysed join per polymer out of 516, that coincidence is rare. And the set has to be lit by chance: trimers do turn up unaided, about 18 times a run, but longer catalysts practically never do. I have not checked any of this against arm R.
- **H14b: not supported, if H14a is not.** Zero minus zero.
- **H14c: supported if it runs.** By construction.
- **H14d: open, leaning high if it runs,** for the reason in the caveat.

So I expect the null I warned about in `docs/before-life.md`. I am running it anyway because a guess is not a result, and because the two descriptive numbers below will say *why*, if it is a null.

## Descriptive, fixed in advance

- **Could it close at all?** For each arm R chemistry, whether its catalysis table contains any self-sustaining set, ignoring counts and dynamics. This is computed in the confirmatory run, not before. It separates "no closed set was possible" from "one was possible and never lit".
- **Closure without history.** How many runs meet criterion (i) and fail (ii).

## Exploratory (not preregistered as tests)

- **Cycling, arm C.** Fuel arrives at twice the usual rate for 5 residence times, then not at all for 5. The mean is unchanged. Same chemistries as arm R, top drive, same detector. I report the E count beside arm R's and conclude nothing from it.
- **Wet-and-dry cycling is not run.** It would change bond energies in time. That does work on the soup and needs its own books.
- **Not in this run:** waiting time to first emergence, repeat runs of one chemistry, recovery from a sudden washout. Each is a later question.
- **Arm M against arm R** on capture. The mineral's level is a free choice, so the contrast is arbitrary. I report it and conclude nothing from it.

One thing I expect to see, and will report either way: the mineral control is *more* persistent than any copier. Sterilise it and it is back at once. A copier can be killed. Copying buys history at the price of mortality.

## Pilots (seeds 1000 and above; not evidence)

Everything I saw before freezing.

- **Gates.** The single-event identity held to 2 × 10^-11. Closed box on plumbing chemistry 1000: dimers 73.8 at drive 0 and 74.0 at drive 8, against a prediction of 70.8. Late entropy production z = 0.30 and −0.10. A longer closed run (2,700 residence times) put monomers, dimers and trimers within 0.5% of prediction. The exact method agreed.
- **Arm P**, six runs. The detector fired in all six. Capture about 0.61. The twin never recovered in 100 residence times. Shuffle percentile 0.96 to 0.97.
- **Arm M**, six runs. No closure in any. The twin was back within one residence time. Capture about 0.59. Shuffle percentile 0.47 to 0.50.
- **Arm N**, chemistries 1000 to 1005, all four drives. Capture about 0.0004. Leak about 1%. Polymer fraction about 0.0001. A trimer is present about 5% of the time.
- **Arm R**, chemistries 1000 to 1003, all four drives, **detector off**. I looked at wall time, step counts, the ledgers and the sign of entropy production. Nothing else.

**A leak in my blinding, recorded.** Run time tracks activity. All 16 arm R pilot runs took about as long as arm N's. So I can infer that nothing took off in those four chemistries. It is a small leak. It did not change any parameter.

## What would change my mind

- **H14a not supported.** Copying is rare or absent in this family of chemistries, at this size and run length. That says nothing about Earth. And the next step is **not** to tune until it appears. One follow-up is allowed, as a new preregistration: a chemistry where a polymer helps assemble its own complement.
- **H14a supported.** Then my arithmetic above was wrong, and I should find out where.
- **H14d below 0.5.** The copiers that arise are tuned *away* from the drive. Then, in this model, "structures that capture more persist more" is false at the first rung.
- **A gate fails.** Then I have learned something about my engine and nothing about the world.

## Known weaknesses, stated before the run

1. **The abstraction is assumed.** Driven, bathed, fed and flushed. Whether that is what mattered on Earth is not tested.
2. **Random catalysis is a strong assumption.** Real catalysis depends on shape and chemistry. A random table is neutral, not realistic.
3. **Washout is a pressure.** It is physical, not a fitness rule. But it removes whatever does not rebuild itself, the way the extrinsic hazard did in the pond (limitation 9).
4. **A rare-drive world is a choice.** If uncatalysed fuel-coupling were fast, polymers would simply form and nothing would need to be found.
5. **A null is close to uninformative.** Wrong chemistry, too few species, too short a run, or wrong idea. S14 cannot tell these apart.
6. **Six-letter strings are small.** 126 species is a toy. Work on evolvability in such networks (Vasas, Szathmáry and Santos 2010) suggests they may copy and still not evolve. That is the next rung's problem, and it may be where this road ends.
7. **The history criterion is narrow.** A set that relights within 10 residence times is closed but does not count as copying here. It is reported under "closure alone".
8. **Tau-leaping is an approximation.** It is checked against the exact method at equilibrium, not in every regime.
9. **The catalyst rule is linear.** Twice the catalyst, twice the rate, with no saturation. Real catalysts saturate.

## Cost

Measured in pilots on one laptop core. A quiet run takes 2 to 4 seconds. A run where polymers are abundant takes 30 to 50. The whole set is 1,820 runs plus twins.

## References

- Schrödinger, E. (1944). *What Is Life?* Chapters 1 and 6, and the note to Chapter 6.
- Horowitz, J. M. and England, J. L. (2017). Spontaneous fine-tuning to environment in many-species chemical reaction networks. *PNAS* 114, 7565. doi:10.1073/pnas.1700617114
- Hordijk, W. and Steel, M. (2004). Detecting autocatalytic, self-sustaining sets in chemical reaction systems. *Journal of Theoretical Biology*.
- Rao, R. and Esposito, M. (2016). Nonequilibrium thermodynamics of chemical reaction networks: wisdom from stochastic thermodynamics. *Physical Review X*. arXiv:1602.07257
- Vasas, V., Szathmáry, E. and Santos, M. (2010). Lack of evolvability in self-sustaining autocatalytic networks constraints metabolism-first scenarios for the origin of life. *PNAS*.
- Wolos, A. et al. (2020). Synthetic connectivity, emergence, and self-regeneration in the network of prebiotic chemistry. *Science* 369. doi:10.1126/science.aaw1955
- Agüera y Arcas, B. et al. (2024). Computational Life: how well-formed, self-replicating programs emerge from simple interaction. arXiv:2406.19108

## Deviation log

(none yet)

## Outcome

(not run)
