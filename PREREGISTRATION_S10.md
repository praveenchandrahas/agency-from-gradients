# Preregistration S10 - dissipative adaptation inside our world (no selection at all)

Written and committed BEFORE the confirmatory run. Pilots (seeds 1000-1004, 100k steps) are not evidence, but they were seen before writing the hypotheses and are described below.

## Why
Jeremy England's dissipative-adaptation argument says that, in a driven system, rearrangements are biased by the work absorbed and dissipated along them, so structures that absorb and dissipate drive tend to become more likely, without selection for reproduction. Its status: the 2013 replicator bound is contested (a 2024 analysis argues it is not physically meaningful in general); dissipative adaptation is supported by simulations and a few experiments, and its link to agent-like behaviour is speculative.

## What this simulation is
No births, no deaths, no fitness (mortality off, reproduction off, fixed population of 60, small 29-gene policy, body traits fixed). The only thing that changes a policy is a rearrangement rule (world_learn.EnglandWorld): each agent alternates 100-step windows, measuring a score with its retained genome and then with a proposed random rearrangement; it keeps the rearrangement with probability min(1, exp(beta * r)), r the relative change in the score, beta = 10, proposals change 30% of genes with sigma 0.3. Score by arm:
- absorbed: energy taken in during the window
- dissipated: heat dissipated, capped by what was absorbed (so energy injected by the bailout of zero-energy agents does not count as dissipating the drive)
- neutral: keep with probability 1/2 regardless (drift control)
- anti: exp(-beta * r), the opposite bias
- forager: the hand-coded forager, as headroom (not tested)

## Honest framing
The rule is local-detailed-balance written as an acceptance rule. It ASSUMES that rearrangements are biased by absorbed or dissipated work. Because the bias is imposed, an increase in the biased quantity is expected by construction (it is stochastic hill-climbing without selection). S10 therefore cannot show that matter obeys the rule. Its informative questions are whether the biased rule climbs the energy ladder (which needs coordinated, delayed payoffs), and whether the dissipation-capped version behaves like the absorption version.

## World (fixed)
v2_config(scale=1, policy="equivariant2", mortality=False, day_night=True, field_drift_every=400), 100,000 steps, seeds 0-19 per arm.

## Hypotheses (metric = population intake per agent-step in the last quarter of the run unless stated; difference of means; 95% bootstrap CI; supported = lower bound > 0)
Manipulation checks (expected by construction; the pilot already showed the same ordering):
- H10a: absorbed - neutral, intake_late > 0
- H10b: dissipated - neutral, intake_late > 0
- H10c: absorbed - anti, intake_late > 0
Substantive:
- H10d: absorbed - neutral, share of intake from tier-2 deposits (late) > 0
- H10e: dissipated - neutral, share of intake from tier-2 deposits (late) > 0

## Pilot (seeds 1000-1004; not evidence)
Intake: absorbed 0.209, dissipated 0.203, neutral 0.177, anti 0.125, forager 0.026 (the forager invests heavily and shares few deposits, so intake per agent is a poor measure of ladder use; the tier-2 share is the ladder measure). Tier-2 share: absorbed 0.49, dissipated 0.46, neutral 0.51, anti 0.65, forager 0.69. I expect H10a-c supported and H10d-e not.

## Interpretation rules
- Entropy rate is reported but not used for inference: with mortality off, bailout energy inflates it.
- Anti having the highest tier-2 share in the pilot would be reported as found; it is not explained away.

## Deviation log
(empty at registration)
