# The world

## A pond, in numbers

Picture a small pond. Grass grows slowly on the bottom. A few deep wells hold rich energy, but they are sealed.

Creatures swim around. They eat the grass. Some pay a cost to open a well. Everyone nearby shares what flows out.

That is the whole simulation, give or take. The details below are exact. The picture above is enough to follow the rest.

!!! tip "Want the full spec?"
    This page is the plain-language tour. For every constant, formula and design decision, see the [Design reference](DESIGN.md). That file is the source of truth.

## The stage

- A **torus**, 32 by 32. Walk off one edge and you appear on the other.
- Population **cap** of 200. Start with 60.
- Everyone acts every step. Births and deaths happen continuously. No generations in lockstep.

## The ladder

Three kinds of energy source. Together they are the "ladder of gradients".

| Tier | What it is | How it behaves |
|---|---|---|
| **0, the commons** | Grass, on every cell | Regrows slowly. Energy above a per-cell cap leaks away as passive dissipation |
| **1** | 12 mid-sized deposits (stock 150) | Locked until someone invests. One agent investing now and then can hold one open |
| **2** | 4 big deposits (stock 800) | Needs about four agents investing *continuously* to open fully. Partial opening pays partially |

A deposit's **openness** runs from 0 to 1. Each invest action adds progress. Progress decays every step: 2% for Tier 1, 15% for Tier 2.

So Tier 2 is hard on purpose. It is the "rich, high gradient" rung. Getting there takes cooperation.

## What an agent can do

Six actions. Move north, east, south or west. Stay. Invest.

Eating is automatic. Whatever is on your cell is shared evenly among everyone standing on it.

What does an agent *see*? Five cells: its own and four neighbours. Seven channels on each.

Those channels are the commons level, and whether Tier 1 and Tier 2 are locked or open. Then two smooth "scent" fields, one pointing toward each tier. It also knows its own energy.

## The costs of living

- **Metabolism:** 0.10 energy per step. Always.
- **Moving:** 0.03.
- **Investing:** 0.15.
- **Reproducing:** needs energy of at least 12. The parent pays 6. The child receives 80% of that.

Run out of energy and you die. Unless the mortality factor is switched off. More on that below.

## The four switches

This is the factorial design. S2 flips each switch on and off and looks at what changes.

| Factor | On | Off |
|---|---|---|
| **Scarcity** | Commons regrow slowly (0.008) | Commons regrow fast (0.08) |
| **Heredity** | A child is its parent plus sparse mutation | A child gets a fresh random genome |
| **Mortality** | Death at zero energy, plus a small extrinsic hazard (0.003 per step) | Zero-energy agents are bailed out to energy 1. No hazard |
| **Succession** | Tier 2 sites appear only where a Tier 1 site has been drained | Tier 2 sites exist from the start |

The ladder itself is **not** a switch. Removing it would make "climbing the ladder" false by construction. That is a real limitation, and I list it [with the others](limitations.md).

## Who gets to have children?

S1 compares four rules for choosing parents.

- **Persistence.** You reproduce if your energy reaches the threshold. This is the treatment.
- **Entropy.** You reproduce once you have burned enough energy. Entropy used as a reward. This is the control the thesis argues against.
- **Task.** You reproduce once you have eaten enough grass. A conventional task reward.
- **Drift.** Parents are random among the living. This is the null.

!!! warning "The null is not perfectly neutral"
    Starvation still removes genomes under drift. So only *fecundity* selection is removed. Viability selection stays. Keep that in mind whenever you read an H1 result.

## What the agents run on

The default policy has about **27 parameters**. It applies one set of weights to each direction's cues, so it is shaped like chemotaxis: move toward what smells good.

Here is the catch, and I want to be loud about it. That is a strong prior. A generic neural net with about 450 parameters did not evolve useful behaviour in the available budget.

So "agency emerged" in this suite means something modest: *a small, well-shaped policy was tuned by selection*. It does not mean agency grew from nothing.

## How I measure things

| Metric | What it is |
|---|---|
| `capture_fraction` | Energy intercepted by agents, divided by intercepted plus passively leaked. Last quarter of the run |
| `entropy_rate` | Leaked energy plus kappa times agent heat, per step. Last quarter of the run |
| `capture_ratio` | `entropy_rate` divided by the same world's rate with no agents |
| `share_tier1`, `share_tier2` | Share of captured energy from each tier |
| `t2_reached` | 1 if any Tier 2 site was ever fully open |
| `delta_recovered` | Recovery after displacement and depletion, evolved minus random genomes |

`t2_reached` only says a site was *ever* fully open. It does not say anyone used it steadily. I learned that the hard way. It is why [S6](results/s6.md) switched to `share_tier2`.

## The accounting assumption

Now the uncomfortable part.

Entropy is counted with a weight. Passive leakage counts as 1 unit per unit of energy. Energy dissipated by an agent counts as \(\kappa\) units, with \(\kappa = 3\) by default.

\[
\text{entropy rate} = \text{leak} + \kappa \cdot \text{heat}
\]

Why? The idea is that a structure processing energy at a lower temperature than its source makes more entropy per unit of energy.

But look at what that does. It makes capturing energy *pay by construction*.

\[
\text{capture ratio} \approx 1 + (\kappa - 1)\, f
\]

Here \(f\) is the capture fraction. So the capture ratio is mostly the capture fraction in a costume.

That is why I call it an **assumption**, not a result. The \(\kappa = 1\) arm in S3 is the check. There, the ratio must collapse toward 1. It did (1.080).

The empirical content of the suite lives in the capture fraction, the tier shares, `t2_reached`, and the S4 recovery contrast. Not in the capture ratio.

## The energy ledger

One more thing, because it is what makes the numbers trustworthy.

Every single step is checked against a closed ledger:

\[
\Delta E_{\text{total}} = \text{injected} - \text{leaked} - \text{heat} - \text{reproduction loss} - \text{death loss} + \text{bailouts}
\]

The tests assert that the residual stays below \(10^{-6}\). That includes the steps where succession converts a site.

If the ledger did not close, energy would be appearing from nowhere. Any "agency" you measured could be a bug. So it is checked, always.

## Ten design changes, forced by pilots

The world went through ten redesigns. Early pilots showed selection doing *nothing*. Each change was a fix for a null.

That is a bias, and I want to name it. A world tuned until selection beats random parents will tend to make selection beat random parents. So weigh H1 with that in mind.

H2 failing *despite* this tuning is some evidence that the tuning did not simply guarantee the thesis. Some. Not much.

The full list is in the [Design reference](DESIGN.md#design-history-forced-by-pilots).
