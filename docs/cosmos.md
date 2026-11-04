# The cosmic ledger (S11)

## A different kind of question

Everything so far lives in a pond. S11 zooms out. All the way out.

The question: **what is the best way to increase the entropy of a lifeless universe?**

No life. No agents in the biological sense. Just stars, galaxies, remnants and black holes, and a controller that gets to pull some levers.

Why ask? Because the thesis leans on entropy, and I wanted to see what a pure entropy-maximiser does when life is not on the menu. The answer is on the [S11 results page](results/s11.md). It is not what a life-first story would predict.

!!! warning "A consistency check, not a discovery"
    The model is a stylised ledger built on published formulas. It is **not** an N-body or hydrodynamic simulation. Matching the literature shows the formulas hang together. It does not show the universe works this way.

## What is in the model

A flat \(\Lambda\)CDM universe. Stars in five classes. White dwarfs. Neutron stars. Supermassive black holes. Photons. Collector mass. And 80 mass bins of black holes, each carrying a count, a mass and a sum of \(M^2\), so the entropy is exact for the moments it carries.

The universe is split in two:

- **Reached (R).** Matter the controller's probes have got to. Levers work here.
- **Unreached (U).** Baseline physics only.

Probes travel at some fraction of light speed, and the reached region grows with a comoving cone. Light speed limits everything. Under 5% of galaxies are ever affectable.

## Why black holes?

Because of one formula.

\[
S_{\text{BH}} = \frac{4\pi G M^2}{\hbar c} \approx 1.05\times 10^{77}\left(\frac{M}{M_\odot}\right)^2 \, k_B
\]

Entropy goes as the *square* of the mass. Merge two holes and the entropy of the result exceeds the sum of the parts. Feed a hole and it grows faster than it feeds.

So a black hole is enormously more entropic than anything else matter can become. Hold that thought. It is the whole answer to the S11 question.

## The levers

The controller chooses among six options. Shares form a simplex, and "do nothing" takes the remainder.

1. **Speed up star formation** in the reached region (up to 10 times).
2. **Funnel cold gas** into black holes, weighted by \(M^2\) and capped at the Eddington limit.
3. **Merge black holes** in pairs.
4. **Collapse** white dwarfs and neutron stars into black holes.
5. **Deploy collectors** that harvest starlight as work and radiate the waste heat colder.
6. **Do nothing.**

Every action costs energy from a work reservoir. That reservoir is filled only by collectors. If it runs short, all requested actions are throttled together.

## Two ledgers that must close

Just like the pond, the cosmos is checked every step.

- **Mass-energy:** non-hole mass, hole gravitational mass, stored work and radiated energy sum to a constant.
- **Baryon number:** non-hole mass, fusion defect, baryons inside holes and evaporated mass sum to a constant.

Both are checked in tests and in every experiment rollout. The relative error must stay below \(10^{-9}\). Observed: about \(10^{-15}\). A leak injected by hand is detected.

## Entropy bookkeeping

Blackbody radiation of energy \(E\) at temperature \(T\) carries \((4/3)\,E/T\) of entropy. Collectors capture starlight, store part of it as work, and radiate the rest at a lower temperature \(T_c\). The colder the radiator, the more entropy per joule.

\(T_c\) cannot go below an environmental floor: the larger of the CMB temperature and the de Sitter temperature (\(2.2\times 10^{-30}\) K). And radiator area is tied to collector mass, so you cannot cheat with an infinite radiator.

Work that is stored but never spent is *not* counted as entropy. It is organised energy.

## Bound domains: the key assumption

Dark energy pushes unbound structures apart. So a hole can only absorb gas from, and merge with, holes inside its own **gravitationally bound domain**. The default domain is a cluster, about \(1.5\times 10^{14}\,M_\odot\) of baryons.

This stops the model turning the whole reachable universe into one giant hole. Without it, hole entropy runs to the holographic cap, and the model flags that.

I found that exploit in my *own* model during a pilot. Hole mass was unbounded by domain size. I fixed it before the confirmatory run, and logged it as a deviation. Better a pilot than a headline.

## Where the numbers come from

| Quantity | Value | Source |
|---|---|---|
| Observable-universe entropy | \(3.1\times 10^{104}\,k_B\), mostly SMBHs | Egan and Lineweaver 2010 |
| Cosmic event horizon | \(2.6\times 10^{122}\,k_B\) | Egan and Lineweaver 2010 |
| Stellar black holes | \(5.9\times 10^{97}\,k_B\) | Egan and Lineweaver 2010 |
| Affectable region | about 16.5 Gly comoving, of 46.4 Gly observable | Ord 2021 |
| Hawking emission | 1.4847 times the hole entropy lost | Page 2013 |

One data wrinkle. Egan and Lineweaver give two different CMB values (Eq. 13 and Table 1). My model computes its own from the photon entropy density and the observable volume. The result, \(5.2\times 10^{89}\), sits between them.

## Seeds mean something different here

The model is deterministic. So a "seed" does not add noise. It draws a set of **uncertain physical parameters**: the SMBH entropy normalisation, the star-formation timescale, radiative efficiency, merger energy loss, and domain mass.

Policies train on seeds 1000 and above. They are evaluated on held-out seeds 0 to 19. And the confidence intervals express *parameter uncertainty*, not statistical noise.

## What the model leaves out

Life. Intelligence as a physical agent, with a body, memory limits or error. Dark matter as feedstock. Relic neutrinos. Galaxy dynamics. Proton decay. Black hole spin and charge. Gravitational-wave entropy. Exotica.

Take the first one seriously. The model excludes life **by assumption**. So it cannot tell you whether life increases entropy. It can only tell you what the formulas say a pure entropy-maximiser would do without it.
