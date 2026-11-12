# Pre-registration S14: before the replicator. Does a driven soup start copying itself?

**Status: DRAFT. Not frozen. No S14 run of any kind has been made, pilots included.**
It becomes a preregistration when the author approves it and the commit that adds it lands on `main`. The engine it describes (`src/agency_gradients/soup/`) and the script (`src/agency_gradients/experiments/s14_soup.py`) do not exist yet. They will be written to this specification. Any place where the code departs from this file goes in the deviation log before results are reported.

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

## The model

Energies are in units of kT. The temperature is fixed. That is the heat bath.

### Species

- **Polymers.** Every string over the alphabet {a, b} of length 1 to L.
- **Fuel F and waste W.** F carries free energy. W is what is left when it is spent.
- **Food.** The monomers `a` and `b`, and F. Food arrives from outside. Nothing else does.

### Free energies

- A monomer has free energy 0.
- A polymer's free energy is the sum of its bond energies. There are four bond types (aa, ab, ba, bb). Each has an energy drawn once per chemistry.
- Bonds cost free energy on average. Joining two pieces is uphill, as condensation is in water. So with no drive, the soup sits near all-monomer. That is Schrödinger's decay to equilibrium.
- F sits above W by Δμ. **That gap is the drive.**

### Reactions

| | Reaction | Free energy change |
|---|---|---|
| 1 | x + y ⇌ xy (join or cut) | the energy of the new bond |
| 2 | x + y + F ⇌ xy + W (fuel-coupled join) | the bond energy minus Δμ |
| 3 | F ⇌ W (leak) | minus Δμ |

Every reaction runs both ways. For each, the forward rate constant over the backward one equals exp(−ΔG). That is the whole of the thermodynamics. Nothing else is added.

### Catalysis

- A catalyst speeds a reaction **in both directions by the same factor**. It never shifts an equilibrium.
- Only polymers of length 3 or more can catalyse. Food never does.
- Which polymer catalyses which reaction is drawn at random, once per chemistry, with a fixed small probability. One draw for plain joins, a separate draw for fuel-coupled joins.
- Without a catalyst, a fuel-coupled join is very slow.

That last line is an assumption, and I want it on the table. **The drive is hard to reach.** Fuel flows past and mostly leaves unspent, unless something in the soup learns to tap it. This is the gradient ladder of the pond world, restated as chemistry. Horowitz and England made the same design choice.

### The reactor

- Well mixed. Fixed volume.
- Food flows in at a fixed rate. Everything flows out at the same dilution rate.
- Washout is the only removal. There is no death rule.
- Simulated molecule by molecule (Gillespie, or tau-leaping checked against it). Not as smooth concentrations.

Why molecule by molecule? Because in a smooth model every possible product exists at once, in some tiny amount. Nothing ever has to *happen first*. Schrödinger's first chapter is about exactly this: with few molecules, chance rules. The first catalyst is a rare event, and I want it to be one.

### One chemistry, one seed

A "seed" here is a whole chemistry: its bond energies and its catalysis table. The randomness that matters is which chemistry you got, not which run of it.

## Parameters

**Provisional.** These are fixed before the draft is frozen, using the tuning rule below. Until then they are placeholders, not commitments.

| Parameter | Provisional value |
|---|---|
| Alphabet, maximum length L | {a, b}, L = 6 (126 polymer species) |
| Mean bond energy, spread | +2, 1 |
| Drive Δμ | 0, 4, 8, 12 |
| Catalysis probability, plain / fuel-coupled | set so a polymer catalyses about one reaction of each kind on average |
| Catalytic speed-up | 10^4 |
| Uncatalysed fuel-coupled join, relative to plain | 10^-3 |
| Run length | 400 residence times |
| Late window | the last quarter |

## Arms

| Arm | What it is | Seeds |
|---|---|---|
| **R** | Random chemistries. The treatment | chemistries 0 to 199, at each drive level |
| **N** | The same chemistries with all catalysis deleted | chemistries 0 to 199, at each drive level |
| **P** | Positive control. A hand-built chemistry with one designed self-copier: a polymer that catalyses its own fuel-coupled assembly | 10 runs, top drive |
| **M** | Mineral control. The same designed reaction, but the catalyst is a fixed outside species that the soup cannot make | 10 runs, top drive |

P is the hand-coded forager of this world. It shows copying is *possible* here and that my detector can see it.

M is the hurricane. It is driven. It builds polymers. It dissipates. It does not copy. My detector must say so.

S9 taught me this the hard way. A probe with no positive control cannot tell "nothing there" from "probe too weak".

Seeds 1000 and above are for plumbing only and are never reported as evidence.

## The tuning rule

The pond world went through ten design changes, each forced by a pilot that showed a null. That biased the design toward the thesis. I do not want to repeat it.

So:

- Parameters are chosen using **arms P, M and N and the gates only**.
- Arm R pilots are allowed for crashes, runtime and the ledger. **The emergence detector is not run on arm R before the confirmatory run.**
- Once this file is frozen, arm R runs once.

## Gates

If any gate fails, no S14 result is reported.

1. **Detailed balance.** A closed box, no flow, no drive. The soup must relax to the Boltzmann distribution, and entropy production must fall to zero within noise.
2. **Ledger.** Monomer mass in, out and held must balance. So must fuel: every F that enters is captured, leaked or washed out unspent. Residual below 10^-6 of throughput.
3. **Second law, exhibited.** Entropy production computed from the reaction fluxes must agree with the free-energy books (in, out, stored) in every window.
4. **No drive, no structure.** At Δμ = 0, the late polymer fraction in arm R must not exceed the equilibrium prediction, within noise. If a soup with no free-energy source holds itself away from equilibrium, the engine is broken.
5. **The detector works.** It fires in at least 8 of 10 runs of arm P. It fires in at most 2 of 10 runs of arm M.

## Measures

- **Capture fraction, C.** Of the fuel that flows in, the share spent through fuel-coupled reactions. The rest leaks or leaves unspent. This is "sunshine used or wasted" for the soup.
- **Entropy production rate.** The sum over reactions of (forward flux minus backward flux) times the log of their ratio. In k_B per unit time. No kappa. No accounting weight. This fixes limitation 3 of the pond world.
- **Polymer fraction.** The share of monomer mass held in polymers of length 3 or more.

### The emergence criterion, E (per run)

Both parts must hold.

**(i) Closure.** Take the reactions and species actually active in the late window. They must contain a self-sustaining autocatalytic set, in the sense of Hordijk and Steel: every reaction in the set is catalysed by a member of the set, and every member can be built from food through the set. The set must include at least one fuel-coupled reaction.

**(ii) History.** At the start of the late window, copy the run. In the copy, delete every polymer of length 2 or more. Keep the food. Let it run on. Call it the **sterilised twin**. The twin's polymer fraction must stay below half the intact run's for at least 10 residence times.

Why the second part? Because it is what separates a copier from a hurricane. Wipe a hurricane's products and they are back at once, because the cause is outside. Wipe a copier and it stays gone until chance makes the first one again. Its presence now depends on its presence before. That is the smallest thing I am willing to call copying.

The thresholds (half, 10 residence times, the activity cut-offs) are judgements. So I also report E with each threshold halved and doubled, and E by closure alone.

## Hypotheses

Intervals are 95% percentile bootstraps over chemistries, 4,000 resamples. A hypothesis is *supported* only if its interval excludes the stated bound in the stated direction.

**H14a. Copying appears.**
In arm R at the top drive, the E rate has a lower bound above 0.05. More than one random chemistry in twenty.
*Why this bound:* a judgement. I also report against 0.01 and 0.10.

**H14b. More drive, more copying.**
The E rate at the top drive minus the E rate at the lowest non-zero drive is above 0. Paired by chemistry.
*Why:* the conditional thesis says the flux matters. This is the nearest thing here to the S12 sweep.

**H14c. Copiers spend the fuel. (Check, expected by construction.)**
For runs that meet E: C in the intact run minus C in its sterilised twin, over the twin's lag, is above 0.
*Why it is only a check:* bonds are uphill. Nothing can hold polymers away from equilibrium without spending fuel. That is the second law, and Schrödinger's point. It is not evidence for anything of mine.

**H14d. Copiers are tuned to the drive.**
For each run that meets E, shuffle the late-window counts among polymers of the same length, 1,000 times. Each shuffle keeps the mass and the length profile and scrambles *which* polymers are there. Compute the instantaneous fuel-spending rate for the real state and for each shuffle. Let q be the real state's percentile.
Supported if the mean q over emerged runs is above 0.5. I also report the share with q above 0.95 and below 0.05.
*Why:* this is the claim that can hurt. "Life is a better entropy engine" predicts q high. Horowitz and England found driven networks settling at *both* extremes, strongly coupled and weakly coupled. A mean q below 0.5 would say the copiers that arise here are the ones that shelter from the drive.
*A caveat I can see already:* criterion (i) requires a fuel-coupled reaction in the set. That tilts q upward. So a high q is weaker evidence than a low one.

## My expectations

- **H14a: open.** Autocatalytic sets are common in the classic no-thermodynamics version of this model. I do not know what the energy bill does to that.
- **H14b: supported, if H14a is.**
- **H14c: supported.** By construction.
- **H14d: open, leaning high, for the reason in the caveat.**

## Not preregistered (exploratory)

- **Waiting time** to the first emergence, by drive.
- **More than one outcome per chemistry.** Do repeat runs of one chemistry land in different self-sustaining states? This is the door to heredity, the next rung.
- **Recovery from a shock.** After a sudden 90% washout, does an emerged state come back? This is viability restoration, asked of a soup.
- **Cycling.** A day-and-night drive with the same mean. A wet-and-dry cycle. Each does work on the soup and needs its own books, so neither is in the primary design.
- **Arm M against arm R** on capture. The mineral's concentration is a free choice, so the contrast is arbitrary. I report it and conclude nothing from it.

One thing I expect to see, and will report either way: the mineral control is *more* persistent than any copier. Sterilise it and it is back at once. A copier can be killed. Copying buys history at the price of mortality.

## What would change my mind

- **H14a not supported.** Copying is rare or absent in this family of chemistries, at this size and run length. That says nothing about Earth. And the next step is **not** to tune until it appears. One follow-up is allowed, as a new preregistration: a chemistry where a polymer helps assemble its own complement.
- **H14d below 0.5.** The copiers that arise are tuned *away* from the drive. Then, in this model, "structures that capture more persist more" is false at the first rung.
- **A gate fails.** Then I have learned something about my engine and nothing about the world.

## Known weaknesses, stated before the run

1. **The abstraction is assumed.** Driven, bathed, fed and flushed. Whether that is what mattered on Earth is not tested.
2. **Random catalysis is a strong assumption.** Real catalysis depends on shape and chemistry. A random table is neutral, not realistic.
3. **Washout is a pressure.** It is physical, not a fitness rule. But it removes whatever does not rebuild itself, the way the extrinsic hazard did in the pond (limitation 9).
4. **A rare-drive world is a choice.** If uncatalysed fuel-coupling were fast, polymers would simply form and nothing would need to be found.
5. **A null is close to uninformative.** Wrong chemistry, too few species, too short a run, or wrong idea. S14 cannot tell these apart.
6. **Six-letter strings are small.** 126 species is a toy. Work on evolvability in such networks (Vasas, Szathmáry and Santos 2010) suggests they may copy and still not evolve. That is the next rung's problem, and it may be where this road ends.

## Open design decisions (to settle before freezing)

1. **Catalysis rule.** Random only, as drafted? Or add a template arm now?
2. **The E thresholds.** Half, 10 residence times, and the bound of 0.05 in H14a.
3. **Size.** Alphabet of 2 and L = 6, or larger at a higher compute cost.
4. **Cycling.** Exploratory, as drafted, or a primary factor.

## Cost

Unknown. The engine does not exist, so I have not measured anything. The run count is 1,600 for arms R and N, 20 for the controls, plus one twin per emerged run.

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
