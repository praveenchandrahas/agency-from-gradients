# Thesis v2: inevitable, but conditional

!!! warning "Status: a draft for review"
    This page restates the idea. It is not a result. Nothing here has been run. The test is [S12](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/PREREGISTRATION_S12.md), and that is still a draft too.

## The claim, as first stated

Life, intelligence and agency are a natural consequence of entropy. They had to arise.

They arose after stars formed. Stars radiate energy. Once no stellar process is left to consume that radiation, something else can. Planets absorb it. They release it very slowly. Whatever uses that slow release makes entropy. We call those things life.

Is that moving up the Kardashev scale? Yes. A larger share of the energy gets used before it is lost.

Now the catch. We have found no life elsewhere. So it is rare. Maybe unique. And it took time: about nine billion years from the Big Bang to the first life on Earth.

That is a strong claim. Let me say which parts I think hold, and which do not.

## What I would keep

**Flux plus a store plus a sink.** Energy arrives. Something holds it for a while. It leaves as heat. Structures that sit in that stream can persist by tapping it. This is physics. Nobody argues with it. It is also what the pond simulates.

**Stars came first.** Gradients had to exist before anything could use them. Fair.

**Time matters.** Chemistry needs a stable environment for a long stretch. A young, violent planet is not that.

## What I would change

Here the reasoning gets thin. Four places.

### 1. "Inescapable" is too strong

The honest form is conditional.

> *If* a steady flux arrives at a surface, *and* the surface holds energy in stores, *and* structures can copy themselves with variation, *then* structures that capture more flux persist more.

That "if" carries the weight. We do not know how often the conditions are met. We know they were met once.

### 2. Entropy production alone does not select for life

A hurricane dissipates energy. So does a fire. So does a hot rock. None of them is alive.

Something extra is needed. Three things, I think:

- It **copies** itself.
- It **varies** when it copies.
- Copies that capture more energy **persist longer**.

That is the repo's design rule. Entropy is measured. It is never rewarded. [S8](results/s8.md) shows why. When entropy is the reward, you get a furnace. It burns energy and builds nothing.

So the thesis is not "entropy produces life". It is closer to: *life is one way for a flux to be dissipated, and the copying kind outlasts the others when the flux keeps coming.*

That is my inference. It is not proven here.

### 3. "Rare" does not follow from one sample

We have one example. Call it N = 1.

N = 1 cannot tell you the rate. It could be rare. It could be common and we have not looked well. And any observer exists only where it happened, so we cannot be surprised to find ourselves here.

The data are also thin on one side. We have searched very little.

So "rare, if not unique" is a reasonable guess. It is not a finding. The simulation cannot settle it either.

### 4. "It took nine billion years" is not a free parameter

The nine billion years is partly the time needed to make heavy elements and settle a planet. It is not a rate for life itself. Life appeared on Earth fairly early after the planet became habitable. That points to a different reading.

*Preparing the world* took long. *Using it* may have been quick.

If that is right, the simulation should not be slow. It should start with a world already prepared. Which is what you asked for. Good.

## Three measures

You asked for a measure of how much of the radiated energy gets absorbed, not wasted. Three are on the table.

| Measure | What it says | In this repo |
|---|---|---|
| **Capture fraction** \(f\) | Share of the flux intercepted before it leaks away | `capture_fraction`. Exists |
| **Free energy rate density** \(\Phi_m\) | Energy flow per unit mass, in erg/s/g | Not computed. Chaisson's measure |
| **Residence time** \(\tau\) | How long a store holds energy | Set by `reservoir_leak`. I know of no standard name for it |

### The Kardashev link

The Kardashev scale is about total power. Sagan's interpolation is

\[
K = \frac{\log_{10} P - 6}{10}
\]

with \(P\) in watts. The formula puts Type I at \(10^{16}\) W, Type II at \(10^{26}\) W and Type III at \(10^{36}\) W. Kardashev's original Type III figure is higher, about \(4\times10^{37}\) W. The two conventions differ.

Notice what it measures. It measures how much power a civilisation *uses*. It does not measure the share of the star's output it catches. So it is not quite \(f\). A civilisation could use a lot and still waste most of it.

Chaisson's \(\Phi_m\) is different. It divides by mass. It is a complexity measure, not a power measure. Stars sit low. Plants higher. Animals higher. Societies highest.

I find \(\Phi_m\) the better fit for "how much does a structure do with what flows through it". I have not checked every number in his tables. Read the source before you quote me.

### A trap

Per-agent energy intake sounds like the right measure. It is not safe.

[S10](results/s10.md) found that rewarding intake can reward the wrong behaviour. An agent can raise its own intake by stealing from the neighbourhood. The population's capture does not rise.

So use \(f\) for the population. Not intake for the individual.

### Residence time

This is the one that matches your planet argument.

A planet takes in energy and gives it back slowly. In the pond, a locked store fills until regrowth equals leak. That is

\[
\text{stock} = \frac{\text{regrow}}{\text{leak}}
\]

and \(\tau = 1/\text{leak}\). At the defaults, \(\tau = 500\) steps.

A longer \(\tau\) means a bigger store for the same inflow. So there is more to tap, and for longer.

That gives a testable claim. See below.

## What S12 would test

Three knobs: how much energy arrives as diffuse commons, how much arrives into the locked stores, and how long the stores hold it. 27 settings. Persistence selection against random parents, plus the hand-coded forager as a ceiling.

The hypotheses are in the [preregistration](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/PREREGISTRATION_S12.md). The sharp one is H12c:

> The gap between selection and random parents grows as residence time grows.

If it fails, stored energy is not doing in this world what the thesis says planetary storage does.

## What S12 cannot test

- **Rarity.** It tests this toy world, not the universe.
- **The hot source and cold sink.** The pond has no temperature. `kappa` is an accounting weight, not a physical one. So the temperature ratio is untested.
- **Larger minds.** The policy is tiny and shaped like chemotaxis. A richer genome is a different question.
- **Whether copying arises on its own.** Here it is built in. That is the biggest gap. The real question for the thesis is where the first copier came from. The pond starts with it.

!!! info "The honest summary"
    The part about energy flows is solid. The part about inevitability is a hypothesis. The part about rarity is a guess.

    S12 can strengthen the first. It cannot decide the other two.

## Sources

- Wikipedia, [Entropy and life](https://en.wikipedia.org/wiki/Entropy_and_life).
- Schrödinger, *What is Life?* (1944).
- England, *Statistical physics of self-replication* (2013), and the project PDF "A New Physics Theory of Life".
- Chaisson, *Cosmic Evolution* (2001), for \(\Phi_m\).
- Sagan's interpolation of the Kardashev scale.
