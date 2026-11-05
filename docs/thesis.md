# The thesis, rebuilt from the hypothesis

!!! warning "Status: published draft for review"
    This page is part of the documentation site. It is a rebuild of the thesis document, not a new result. Every number comes from the preregistered experiments already reported. The change is one of order and emphasis: the hypothesis comes first, the predictions are derived from it, the evidence is read against those predictions, and the revised claim comes last.

    The [earlier draft](https://github.com/praveenchandrahas/agency-from-gradients/blob/thesis-v2-s12/docs/thesis-v2.md) starts from cosmic inevitability and works back to a proposed experiment. This page starts from the claim the suite was built to test.

## 1. The hypothesis

The design hypothesis, as written before the confirmatory run:

> Agency arises when a population of self-maintaining structures is selected only by persistence and reproduction, in an environment with a ladder of energy gradients, finite resources, heredity with variation, a real cost of failure, and succession.

That is one sentence containing several claims. The rebuild begins by separating them.

### 1.1 The parts

| Part | Meaning in this suite |
|---|---|
| **Persistence selection** | An agent reproduces when its energy reaches a threshold. No external goal, no reward for entropy. |
| **Reproduction** | The parent pays energy; the child inherits a genome, with mutation if heredity is on. |
| **Gradient ladder** | A commons (Tier 0), twelve small reservoirs (Tier 1), four large ones (Tier 2). The higher tiers hold more energy but cost investment to open. |
| **Finite resources** | The commons regrows slowly. Eating is shared among agents on a cell. |
| **Heredity with variation** | Child genome = parent genome plus sparse mutation, versus a fresh random genome when heredity is off. |
| **Cost of failure** | Death at zero energy, plus an extrinsic hazard, versus a bailout to energy 1 when mortality is off. |
| **Succession** | Tier 2 sites form only where a Tier 1 site has been drained, versus existing from the start. |
| **Agency** | Operationalised narrowly as **viability restoration**: after displacement and depletion, does the agent regain a viable energy state? |
| **Entropy** | Measured as passive leak plus \(\kappa\) times agent heat. Never rewarded. |

### 1.2 Two claims, not one

The sentence can be read in a weak and a strong form.

**Weak (sufficiency).** The conditions plus persistence selection are *enough* to produce some agency-like behaviour.

**Strong (necessity).** Each condition is *required*: remove it, and agency falls.

The suite was designed to test both, but the preregistration made the strong form the centrepiece. [H2](results/main.md) asked whether scarcity, heredity and mortality were each load-bearing. That was the central prediction. It failed.

This distinction is the main analytical move of the rebuild. A failure of necessity is not the same as a failure of sufficiency, and the two should be kept apart.

### 1.3 The circularity problem

There is an obvious objection. If agency is viability restoration, and selection is by persistence, then the survivor is by definition good at persisting. The hypothesis risks saying: things that survive survive.

Three things partly break the circle.

1. **Restoration is tested after a displacement and depletion that are not the selection condition.** The agent has to recover in a state it was not selected on.
2. **The contrast is evolved versus random genomes**, and full versus no heredity, not raw recovery. Survivorship inflates the raw number; only the contrast is interpretable.
3. **Ladder access is not implied by survival.** Opening a Tier 2 deposit requires coordinated investment and a delayed payoff. An agent can persist on the commons without ever doing it.

Those are real defences, but they are not complete. The default policy is a 27-parameter, chemotaxis-shaped controller. A generic neural network did not evolve useful behaviour in the available budget. So "agency" here means a small, well-shaped policy tuned by selection, not agency from nothing. The circle is bent, not broken.

## 2. What the hypothesis predicts

If the hypothesis is right, five things should follow. These are the preregistered tests.

| | Prediction | Falsified if |
|---|---|---|
| **P1** (H1) | Persistence selection raises entropy production over random parents | The interval includes zero or is below it |
| **P2** (H2) | Removing scarcity, heredity or mortality lowers Tier 2 access | Removing a factor does not lower access |
| **P3** (H3) | Heredity contributes to recovery after displacement | The full-minus-no-heredity interval includes zero |
| **P4** (H4) | Rewarding entropy directly does not beat persistence on Tier 2 access | The entropy arm is clearly better |
| **P5** (H5) | The energy accounting closes at \(\kappa = 1\) | Capture ratio outside 0.7 to 1.15 |

P5 is not evidence for the thesis. It is a check on the bookkeeping. If it had failed, no S3 number would be reported.

### 2.1 What the hypothesis does not predict

The later experiments were not derived from the hypothesis in advance. They were built to explain the H2 failure or to probe adjacent questions.

| Experiment | Question | Status |
|---|---|---|
| **S6** | Is H2 a free-rider problem? | Post hoc explanation, preregistered after H2 |
| **S7** | Do bigger genomes and more generations help? | Built after S6 failed |
| **S8** | What does an explicit entropy objective produce? | Reverse control, preregistered after a pilot |
| **S9** | Does a learned private reward produce agency? | Follow-up to S8 |
| **S10** | Does dissipative adaptation climb the ladder? | England-style probe, no selection |
| **S11** | What raises the entropy of a lifeless universe? | Cosmic ledger, excludes life by assumption |

A thesis rebuilt from the hypothesis should mark these as **diagnostic**, not **confirmatory**. They can explain a failure. They cannot supply the support the original prediction lacked.

## 3. The evidence

### 3.1 The world has headroom

Before reading any negative result, ask whether the world is simply impossible. It is not.

| | Tier 2 reached | Energy from Tier 2 | Entropy rate |
|---|---|---|---|
| Hand-coded forager | 100% of runs | 50% | 37.1 |
| Evolved populations | 27% of runs | 2% | 27.3 |

The forager is a positive control, not an evolved agent. It shows the ladder can be used. Selection moved the population a little and left most of the available gain unused.

### 3.2 The scorecard

| Test | Contrast | Result | Reading |
|---|---|---|---|
| **H1** | Persistence minus drift, entropy rate | +2.34 [1.08, 3.66] (27.3 vs 24.9) | Supported, small |
| **H2** | All-on minus factor-off, Tier 2 access | Scarcity -0.27 [-0.50, -0.03]; heredity -0.73 [-0.90, -0.57]; mortality -0.53 [-0.73, -0.33]; succession -0.10 [-0.33, 0.13] | **Falsified** for the first three; succession not shown |
| **H3** | Full minus no heredity, recovery | +0.220 [0.189, 0.249] | Supported, with caveat |
| **H4** | Entropy reward minus persistence, Tier 2 access | -0.10 [-0.30, 0.10] | Not falsified |
| **H5** | Capture ratio at \(\kappa = 1\) | 1.080 [1.017, 1.143] | Passes, barely |
| **S6a** | Contributor minus equal sharing, Tier 2 share | +0.024 [-0.023, 0.075] | Not supported |
| **S6b** | Heredity minus no heredity, contributor rule | -0.017 [-0.059, 0.032] on share; -0.60 [-0.77, -0.43] on reach | Not supported; sign reversed on reach |
| **S7a** | Big genome, persistence minus random parents | -0.000 [-0.001, -0.000] | Not supported |
| **S7b** | Big genome minus small policy | -0.037 [-0.092, -0.001] | Not supported; sign reversed |
| **S7c** | Big genome, late minus early | -0.020 [-0.033, -0.008] | Not supported |
| **S8a** | Entropy objective minus forager, entropy rate | +6.85 [0.58, 11.11] | Supported |
| **S8b** | Entropy objective minus forager, invest share | +0.27 [-0.01, 0.44] | Not supported |
| **S8c** | Gain at \(\kappa=3\) minus gain at \(\kappa=1\) | +12.96 [6.58, 17.54] | Supported |
| **S9a-d** | Learned private reward, four probes | H9a and H9b include zero; H9c and H9d reverse the predicted sign | Not supported |
| **S10d** | Absorbed minus neutral, Tier 2 share | -0.033 [-0.070, 0.004] | Not supported |
| **S10e** | Dissipated minus neutral, Tier 2 share | -0.013 [-0.050, 0.023] | Not supported |
| **S11** | Best cosmic entropy strategy | H11a, c, e supported; H11b, d not | A black-hole engineer |

The rest of this section reads the results that matter most.

### 3.3 What moved

**H1 is small but detectable.** Persistence selection raised entropy production by about 2.3 units over random parents. That is a difference of roughly 9%, with a lower bound near 1.1. Two caveats shrink it further.

- The random-parents control is not neutral. Starvation still removes genomes, so only fecundity selection is removed. H1 measures fecundity selection on top of viability selection.
- Rewarding plain grass-eating also produced an entropy rate of 26.5, close to persistence. No interval was computed for that contrast. So the gain is not specific to persistence.

**H3 is supported, but not in the way the thesis needs.** Heredity improved recovery by 0.220 [0.189, 0.249]. That is a clean interval. But random-parents selection produced almost the same gain: 0.259, against 0.270 for persistence. What is inherited is mostly better grass-foraging, filtered by starvation. It does not require selection by surplus.

So H3 says heredity matters for restoration. It does not say that persistence selection is what makes heredity matter.

### 3.4 What failed

**H2 failed in the opposite direction.** Removing scarcity, heredity or mortality *raised* Tier 2 access, with intervals below zero. This was not a null. Every removable factor had a negative effect.

The numbers:

- Scarcity: -0.27 [-0.50, -0.03]
- Heredity: -0.73 [-0.90, -0.57]
- Mortality: -0.53 [-0.73, -0.33]
- Succession: -0.10 [-0.33, 0.13], not shown

Read the sign carefully. All-on minus factor-off is negative. That means the factor-off condition reached the big deposits *more* often.

[**S6**](results/s6.md) **did not rescue the free-rider explanation.** Making the benefit private pointed the right way for steady use (+0.024), but the interval includes zero. Heredity still did not help under the contributor rule: -0.017 on share, and -0.60 on reach. Random fresh genomes still reached Tier 2 in every run; inherited ones lagged.

[**S7**](results/s7.md) **did not rescue the "too few genes" objection.** The big-genome arm reached a Tier 2 share of 0.000. The small policy reached 0.037 [0.001, 0.090]. The hand-coded forager reached 0.399 [0.295, 0.501]. Ninety per cent of big-genome runs went extinct before 200,000 steps. The package bundled five changes, so even a positive result could not have been pinned on one of them. It was not positive.

### 3.5 The entropy objective is not a shortcut

The thesis says entropy should be measured, never rewarded. [S8](results/s8.md) tests the reverse.

An explicit entropy objective produced an entropy rate of 35.8 [29.5, 40.1], beating the hand-coded forager at 29.0. It captured 88% of the energy. But it spent 54% of its actions investing, against 27% for the forager, and got a *smaller* share of its energy from the big deposits: 0.33 against 0.63. Much of its edge was the heat from constant investing. It was closer to a furnace than a forager.

H8b, the preregistered "furnace" prediction, was not supported: +0.27 [-0.01, 0.44]. The interval just reaches zero, because one of five optimisation runs never found the deposits. The descriptive pattern is still furnace-like. The preregistered test is what it is.

[S11](results/s11.md) pushes the same point to a cosmic ledger. Given a lifeless universe and a set of physical levers, the best entropy strategy is to build starlight collectors and feed gas into black holes. The gain is about \(10^{110}\,k_B\), more than 99.99% of it black-hole entropy. The entropy-maximal structure is a black hole; the optimal controller is an engineer. The model excludes life by assumption, so this does not say life cannot raise entropy. It says a pure entropy maximiser, given these options, would not build it.

### 3.6 The later probes

[**S9**](results/s9.md) asked whether a learned private reward produces agency. All four hypotheses failed. The two reversed signs are a probe confound, not better agents: evolved recovery was flat at 0.46 to 0.48 across arms, while the *random* baseline moved. The predictive probe had no positive control, so its null cannot separate "no information" from "probe too weak."

[**S10**](results/s10.md) asked whether England-style dissipative adaptation climbs the ladder without selection. The manipulation checks passed by construction. The substantive tests did not: absorbed minus neutral on Tier 2 share was -0.033 [-0.070, 0.004]; dissipated minus neutral was -0.013 [-0.050, 0.023]. With the bias imposed, the system absorbed more energy. It did not climb.

## 4. What the evidence does to the hypothesis

### 4.1 Sufficiency: partly supported, at a small effect

Persistence selection shifted entropy production, and heredity improved restoration. That is not nothing. But selection did not produce ladder-climbing, and the improvement in restoration was not specific to fecundity selection. The sufficiency claim survives in a thin form: selection can tune a small policy toward better survival in the niche it is selected on.

### 4.2 Necessity: not supported, and possibly the wrong claim

H2 was the central prediction, and it failed for all three removable factors. The direction was negative, not null. Removing a condition made the coarse outcome *more* likely.

There are two readings, and the suite cannot fully separate them.

**Reading A: the conditions are substitutable.** Scarcity, heredity and mortality are not separate ingredients. Removing one changes population density, turnover or exploration in a way that raises the chance of a lucky Tier 2 opening. The hypothesis named the wrong causal structure.

**Reading B: the metric is wrong.** `t2_reached` is a binary, population-level outcome. It means "a site was ever fully open," not "agents used it steadily." Removing mortality means bailouts; the no-mortality cells fill the population cap of 200; more agents mean more chances for someone to open a deposit. The Tier 2 *share* stays at 1.4 to 5.9% in every mortal cell. So H2 may be measuring density and luck, not agency.

The second reading cuts both ways. If the metric is invalid, H2's falsification is not a clean refutation of the necessity claim. It is a failed test, not a decisive one. The honest statement is: **the necessity claim is not supported, and the design cannot tell whether that is because the claim is false or because the outcome measures the wrong thing.**

### 4.3 Specificity: not established

H1 says persistence beats drift on entropy production. It does. But a plain grass-eating reward produced a similar rate (26.5), and no interval was computed. H4 says entropy reward does not beat persistence on Tier 2 access. It does not (-0.10 [-0.30, 0.10]), but that is an absence of a difference, not evidence that persistence is special.

So the comparative claim is weak. Persistence is not worse than the alternatives tested. It is not shown to be better in the way the thesis needs.

### 4.4 The policy problem

The default policy is a 27-parameter, chemotaxis-shaped controller. It has a strong prior: shared weights across directions, sensing gradients. A generic MLP did not evolve useful behaviour. The 5,300-gene v3 policy went extinct in 90% of runs.

This matters for every positive and negative result. "Agency emerged" means a small, well-shaped policy was tuned by selection. "Agency failed to emerge" may mean the policy class could not represent the conditional, cooperative rule that opening a Tier 2 deposit requires. The suite cannot separate the world from the policy.

### 4.5 The design bias

The world went through ten changes, each forced by a pilot that showed a null. The final design is friendlier to selection than a blind one would have been. H2 failing anyway is some evidence that the tuning did not simply guarantee the thesis. Some. It is not a lot.

## 5. The revised thesis

Here is what I would now defend.

> In this toy world, selection by persistence and reproduction alone is enough to shift entropy production and to improve viability restoration, but it is not shown to be enough to produce open-ended, ladder-climbing agency. The conditions that were switched off — scarcity, heredity and mortality — are not shown to be individually necessary. The stronger claim — that a gradient ladder plus those conditions and succession makes agency inevitable — is not supported.

What survives:

1. **Persistence selection has a small, detectable effect.** It raises entropy production modestly and improves recovery, but the recovery gain is mostly viability filtering, not fecundity selection.
2. **Entropy is a consequence, not a goal.** Rewarding it produces a furnace in the pond (S8) and a black-hole engineer in the cosmic ledger (S11). Neither is an agent.
3. **Heredity matters for restoration, but not specifically through surplus.** H3 holds; its interpretation does not.
4. **The ablated conditions are not shown to be necessary.** The data are more consistent with substitutability and density effects than with a checklist of required ingredients.

What I would retract:

- The claim that scarcity, heredity and mortality are each load-bearing.
- The implication that the five conditions are a recipe for agency.
- Any reading of H2 as a clean refutation. It is a failed test with a measurement problem.

What I would keep as an open question:

- Whether a richer policy, a gentler world, or a density-matched design would show the conditions matter.
- Whether "agency" can be operationalised without measuring survival by another name.
- Whether any of this transfers beyond the toy world.

### 5.1 The hypothesis I would test next

The original hypothesis treated the conditions as the cause. The failures point to a different variable: **the range of states the population is selected across**.

> **H13 (candidate, untested).** Persistence selection produces viability restoration only when the selection environment contains the perturbations used to test restoration. A static world selects narrow niche competence. A world that repeatedly displaces and depletes agents selects restoration.

This is not a reward for restoration. Both arms would select only on persistence and reproduction. The difference is the distribution of experiences, not the objective.

What it would predict:

- A static arm survives and forages, but recovers poorly after a novel displacement.
- A variable arm survives about as well, but recovers better.
- The gain is not explained by higher mortality or population density.
- Falsified if the variable arm does not improve recovery on a common test, or if the improvement disappears when density is matched.

This hypothesis is closer to the original design rule than the five-condition list. It says agency is not built by adding ingredients. It is built by selecting across the kinds of disturbance an agent must survive.

## 6. What would make the thesis stronger

These are the tests the rebuild implies. None has been run.

1. **Density-matched ablation.** Hold population size fixed across conditions. If removing mortality still raises Tier 2 use, the effect is not density. If it disappears, H2 was measuring the population cap.
2. **A static-versus-variable selection experiment.** Two arms, the same persistence rule. The static arm never displaces agents; the variable arm subjects them to the displacement used in the restoration test. Compare recovery on a common test. This is the direct test of H13.
3. **A sustained-use metric.** Replace `t2_reached` with Tier 2 share, time to first sustained opening, and individual investment traces. Separate "someone opened it once" from "the population uses it."
4. **A policy-class control.** A hand-coded ladder-user proves the world has headroom, but it does not prove that the generic policy class can represent the rule. A curriculum or a shaped exploration bonus would test that separately.
5. **A gentler v3, preregistered.** Viable seeding, an easier start, a longer grace period. Log how extinct runs are handled before the run, not after.
6. **A predictive probe with a positive control.** Without one, the S9 null cannot distinguish absence of information from a weak probe.
7. **S5, Barrow's efficiency pathway.** Still not implemented.
8. **More power.** Thirty seeds with a binary outcome cannot detect differences below about 0.25. Use more seeds or continuous outcomes.

## 7. What this does not say

- It does not say agency requires an objective. The suite tested persistence-only selection and found small effects, not zero.
- It does not say persistence selection is unimportant. It says the strong, five-condition version is not supported in this world.
- It does not say the five conditions are false on Earth. The abstraction is assumed, not tested.
- It does not say entropy is irrelevant. It says making entropy the objective does not produce agency.
- It does not say the negative results are decisive. Several are underpowered, confounded, or measured with a coarse outcome.
- It does not say anything about prediction, planning, or minds. Viability restoration is not prediction.

## 8. Provenance

- **Confirmatory seeds:** 0 to 29 for S1 to S6; 0 to 19 for S7, S9, S10 and S11; five optimisation runs per \(\kappa\) for S8.
- **Steps:** 20,000 for S1 to S6; 200,000 for S7; 100,000 for S9 and S10.
- **Intervals:** 95% percentile bootstrap, 4,000 resamples (1,000 for the S2 main-effect table).
- **Raw data:** S7-v3 and S8 to S11 CSVs are on the `ci-results` branch. S1 to S4 and S6 CSVs are not in the repository.
- **Code:** `src/agency_gradients/`, with the world in `world.py` and `world_v2.py`, and the experiments in `experiments/`.
- **Preregistrations:** `PREREGISTRATION.md` and `PREREGISTRATION_S6.md` to `PREREGISTRATION_S11.md`.

The one-line version:

> The hypothesis was worth testing, and the test did not support its strong form. What remains is smaller: selection can tune survival, heredity helps restoration, and entropy is what the world does, not what the agent is trying to do.
