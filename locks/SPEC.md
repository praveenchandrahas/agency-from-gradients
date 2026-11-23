# S15, Locks: does life open gradients that nothing else opens?

> **Status: SPEC. Not a preregistration.**
> This file fixes the question, the definitions, the hypotheses and the falsifiers. It contains no code and no results.
> Numbers marked **TBD** are set in `locks/PREREGISTRATION.md`, after pilots on the **controls only**, and frozen before any confirmatory run.

## The core hypothesis

Everything else in this repo follows from one claim. So this is the claim to test first.

In my own words, the broad version:

> Life increases global entropy more than any passive structure can.
> Any structure that decreases local entropy will eventually cause a greater increase in global entropy.

The broad version is already in trouble. Stars and black holes are not passive. They persist only while energy flows through them. And they produce vastly more entropy than any biosphere. S11 found the same thing: in a lifeless universe, the entropy-maximal structure is a black hole.

So the version tested here is narrower:

> **In cold, locked gradients, where passive structures and non-living dissipative ones stall, life opens the lock. Nothing else does.**

This narrows "only" to a domain. It is also the version that could be true. It matches the succession idea in [`docs/thesis.md`](../docs/thesis.md): the big engines go first, then life works through what they leave behind.

## Why this, why now

### What the suite already says

The core claim has been touched. It has not been tested.

- **Starlight.** Light that nothing absorbs escapes undegraded. The lifeless world is a perfect mirror. Its preregistration says so. So life beat a mirror. A dark rock would have turned that light into heat too.
- **Planet** (draft PR 7). Agents competed with agents. Nothing passive was in the comparison. It measured energy throughput, not entropy production.
- **S11.** An entropy objective, with life excluded, favours black holes and an engineer. It cannot say whether life adds entropy.
- **S14 controls.** A designed copier and a fixed outside "mineral" catalyst dissipated about the same: 8,070 against 8,077 k_B per residence time. But the mineral's level was a number I chose. So it does not say which is the better engine. It says copying was not needed to burn that fuel.
- **Horowitz and England (2017).** Driven chemical networks settled into states tuned to the drive, both ways. Some coupled strongly. Some sheltered from it.

The evidence that exists leans against the broad version. That is a reason to test the narrow one properly, not to stop.

### Why not sunlight

Sunlight is an **unlocked** gradient. Any dark surface absorbs it and turns it into heat. No key is needed.

Worse, a planet in sunlight is a **fixed-flux** system. Energy out equals energy in. Entropy production is set by how much is absorbed and the temperature it leaves at. A black rock is already near the ceiling. And at fixed flux, convection *lowers* entropy production: it carries heat faster, so the temperature difference shrinks.

A sunlight test could fail for reasons unrelated to life. So sunlight becomes one end of the dial below: the zero-barrier case.

### Where free energy comes from

A correction to my own framing. Most free energy is not starlight.

Black holes shine on gravity. Infalling matter heats up and radiates. An accretion disk releases roughly 6 to 40% of the infalling mass as energy, depending on spin. Fusion releases about 0.7%. Stars, in turn, run on gravity switching fusion on.

Both trace back to the low-entropy start of the universe. Matter began spread almost perfectly smoothly, which for gravity is low entropy. And most of it was left as unfused hydrogen. Those are the two great locked gradients.

On Earth, too, not everything is sunlight. Hydrothermal vents run on internal heat from radioactive decay and the planet's formation.

The accurate line: **most free energy is released through gravity and fusion.** Life works the colder, smaller locks those engines leave.

## Definitions

Defined by what a structure does, not by "local entropy".

| Class | Definition | Examples |
|---|---|---|
| **Passive** | Persists with no energy flowing through it | Rock, still water, ice |
| **Dissipative** | Persists only while energy flows through it. Does not make copies with heritable variation | Flame, convection cell, hurricane, a fixed autocatalytic cycle |
| **Living** | Persists only while energy flows through it. Makes copies with heritable variation | Replicators |

Why not "decreases local entropy"? An organism in steady state holds its entropy roughly constant. What sets it apart is that it falls apart when the flow stops. That is measurable. "Local entropy" of a toy structure mostly is not.

The other terms:

- **Locked gradient.** Free energy is available, but no fast passive route releases it. Wood sits in oxygen for centuries. Hydrogen and CO₂ coexist.
- **Barrier, B.** How locked a gradient is: the activation barrier in units of kT.
- **Cold.** B is many times kT. Thermal motion alone almost never opens the lock.
- **Entropy production, σ.** From reaction fluxes: the sum over reactions of (J₊ − J₋) ln(J₊/J₋), in k_B per unit time. Checked against the free-energy books, as in S14.
- **The counterfactual.** Same world, same inflow, same barrier, with the structure absent. Every claim is a difference against it.

Why the counterfactual matters: the second law already says any ordered structure exports at least as much entropy as it holds off. That part is guaranteed. The claim worth testing is about the **rate**, against the same world without the structure.

## The model, in outline

A new engine in `locks/`, self-contained, like `starlight/`. It borrows S14's thermodynamic rules: every reaction is reversible, rates obey local detailed balance against a heat bath, the books are kept in free energy, and entropy production is measured, never rewarded or imposed.

### Why a new engine

- **Not the S14 soup.** Copying did not arise there (0 of 200). Here copying is given, and the question is what it does. Evolving catalytic keys in a full polymer chemistry is also too slow to run at scale.
- **Not Starlight.** It has no temperatures and no reverse reactions, and its lifeless world is a mirror.

### The world

- A flow reactor. Fuel arrives, is spent or leaks, and washes out.
- One or more **locks**. Lock *i* is a reaction F_i ⇌ W_i, with free-energy drop Δμ_i (TBD, several kT).
- The uncatalysed rate is k₀·e^(−B). **B is the dial.**
- Each lock has a target **key**: a bit string of length *n* (TBD).
- A catalyst carries a key. Its speed-up falls with the Hamming distance *d* between its key and the lock's (shape TBD).
- **A catalyst speeds the forward and backward reaction by the same factor.** It cannot shift the equilibrium. This is a gate (G2), not an assumption I trust.

### The classes, as a ladder of ablations

Each arm adds one thing to the one before.

| Arm | What it is | What it adds |
|---|---|---|
| **N** | No catalysts. Only the uncatalysed route | The passive counterfactual |
| **M** | Fixed catalysts, random keys, fixed abundance. Abundance does not depend on the flux | A natural mineral |
| **D** | Catalysts that grow on the free energy their own reaction releases, and decay. Keys fixed, copied without error | Self-sustaining dissipation. A fire |
| **L** | As D, but keys are inherited with mutation | Heritable variation. Life |
| **U** | The perfect key at the highest allowed abundance | A designer bound. Not a competitor |

D and L differ in one thing only: variation. M and D differ in one thing only: whether the catalyst feeds on the flow.

**Matching.** M's abundance is matched to L's late-window mean catalyst mass, at the same B. Then the M against L contrast is about keys, not quantity. (The S14 mineral was not matched. That is why its contrast meant nothing.)

**Energy books for D and L.** Growth is paid from the free energy released, with efficiency below 1 (TBD). Upkeep costs free energy. A dead catalyst's stored free energy is dissipated and counted. Stored free energy is tracked separately from what is dissipated.

**Extinct worlds** keep running. They revert to arm N, with the leak still producing entropy. So an extinct world scores the passive baseline, not zero. That fixes Starlight's mirror problem.

### The factors

- **Barrier B:** a grid from 0 to cold (TBD, roughly 0 to 16 kT).
- **Drift r:** the lock's key flips bits over time. r = 0, plus one or two drifting levels (TBD).
- **Locks K:** 1, then a stack of 3 with rising B (H3b only).
- **Neutral marker:** every catalyst in L also carries marker bits that do nothing. Key evolution is compared against marker drift.

## What is true by construction

I have to say this before any result.

- **More catalysis means more flux, and more flux means more entropy.** That is bookkeeping. So H1 and H2d are checks, not findings.
- **In a static world, evolution can at most match the best fixed key.** It also pays for its mutations. So "L matches U" is the ceiling, not a failure.
- **The key–lock geometry is my choice.** How hard the search is follows from *n* and from how fast speed-up falls with distance. Those set the results. Sensitivity to both is reported.
- **Copying is given.** Where the first copier comes from is not asked. S14 asked, and got a structural null.

What is **not** by construction:

- whether evolution finds keys faster than its costs kill it,
- whether L beats a matched natural mineral and a fixed-key fire,
- whether drift breaks fixed keys more than mutation breaks life,
- whether life overexploits and crashes,
- whether lineages shelter from the drive rather than couple to it.

## Hypotheses

### H0. Gates (must pass, or nothing is reported)

- **G1.** A closed box relaxes to its equilibrium composition, and σ falls to zero within noise.
- **G2.** With catalysts present, the closed-box equilibrium is unchanged. Catalysis changes speed, never destination.
- **G3.** Fuel, mass and free-energy ledgers close every step.
- **G4.** σ from the fluxes agrees with the free-energy books (within TBD).
- **G5.** No run shows significantly negative σ.
- **G6.** Positive control: L seeded with the perfect key holds it. Negative control: L with mutation set to zero is indistinguishable from D.

### H1. Structure beats passive in locked gradients (check)

At cold B, σ in D and L exceeds σ in N.
*Fails if* either interval of the difference includes zero.

### H2. Life beats non-living structure in cold, locked gradients (the core claim)

- **H2a.** At the coldest B, σ(L) > σ(M) and σ(L) > σ(D).
  *Fails if* either interval of the difference includes zero or lies below it.
- **H2b.** The advantage of L over the best non-living arm grows with B.
  *Fails if* the slope's interval includes zero or lies below it.
- **H2c.** At B = 0, life adds nothing: all arms lie within TBD of N.
  *This is the sunlight case.* The hypothesis predicts no advantage where there is no lock. If L wins big at B = 0, something in the model is giving life a free advantage, and the model is wrong.
- **H2d.** σ(L) ≤ σ(U) everywhere (check).

### H3. Life keeps opening locks over time

- **H3a. Drifting lock.** With r > 0, σ(L) is sustained. σ(M) and σ(D) decay toward N.
  *Fails if* L decays as fast as the fixed arms.
- **H3b. Stacked locks.** With K = 3, L opens more locks by the end of the run than any non-living arm.
  *Fails if* L opens no more than the best non-living arm.
- **H3c. Eventually.** Cumulative entropy over the whole run, with stored free energy counted when it is dissipated, favours L at cold B.
  *This is the word "eventually" in the hypothesis, made testable.*

### Risks the run must report either way

- **R1. Overexploitation.** Planet showed agency winning the fight and shrinking the pie. Report extinctions and boom–bust cycles, and whether cumulative σ suffers.
- **R2. Sheltering.** Horowitz and England found networks tuned *away* from the drive. Report the share of L lineages whose keys move away from the lock faster than neutral drift.
- **R3. Two horizons.** Planet's generation 220 was the bottom of a dip. Every endpoint is reported at two horizons.

## When the core claim fails

In this model, the narrow hypothesis **fails** if:

- H2a fails at the coldest B, **and** H2b fails. Or:
- H2c fails. Then the model is broken and nothing it says counts.

It is **weakened**, not failed, if H2 holds in static worlds but H3a fails. Then life is just a search process for a good fixed key. That is still something. It is not "nothing else does".

## What a positive result would not show

- That real life does this. These are toy locks.
- That "nothing else does" outside the classes modelled. Stars, black holes and gravity are excluded by scale, not by argument.
- Where life comes from.
- Anything about agency. Agency is a later rung. This tests the ground it stands on.

## Measurements

- **σ**, late window (TBD), at two horizons.
- **Cumulative entropy**, with stored free energy tracked separately.
- **Fuel spent**: the share of incoming fuel released through each lock. The rest leaks or washes out.
- **Key–lock distance** and **marker distance**, for L.
- **Catalyst mass**, for M, D and L.
- **Extinctions**, counted. Extinct worlds are scored as they run, not dropped.
- 20 seeds per cell (0 to 19). 95% bootstrap intervals on seed means, 10,000 resamples.
- Pilots on seeds 1000 and above, **controls only** (N, U, and the G6 controls). L, M and D are not run at confirmatory settings until the preregistration is frozen. This is S14's blind-tuning rule.

## Decisions for the author before preregistration

1. **Engine.** A new coarse engine in `locks/` (recommended), or an extension of the S14 soup.
2. **Matching rule for M.** Match to L's late catalyst mass (recommended), or to a fixed budget shared by all arms.
3. **Key geometry.** Bit strings with Hamming distance (recommended), or a random catalysis table as in S14.
4. **Arm D in the first run**, or deferred to a follow-up. Without D, H2a can only beat a mineral, not a fire.
5. **Numbering.** S15 is used here. There is no S13 (see `docs/before-life.md`).

## Reading list, to sharpen the falsifiers

The fight in the literature sits roughly here. These are to read, not to settle the answer.

- Ulanowicz and Hannon (1987), "Life and the production of entropy", *Proc. R. Soc. B*.
- Schneider and Kay (1994), "Life as a manifestation of the second law of thermodynamics", *Mathematical and Computer Modelling*.
- Michaelian (2011), "Thermodynamic dissipation theory for the origin of life", *Earth System Dynamics*.
- Kleidon (2016), *Thermodynamic Foundations of the Earth System*, Cambridge University Press.
- Horowitz and England (2017), *PNAS* 114. Already in `docs/before-life.md`.
- Egan and Lineweaver (2010), the entropy budget of the observable universe. Already used in S11.
- Vasas, Szathmáry and Santos (2010), on autocatalytic networks that copy but do not evolve. Relevant to arm D.

## The one-line version

> Build a world of locks. Turn the barrier up. See whether only the living curve stays up.
