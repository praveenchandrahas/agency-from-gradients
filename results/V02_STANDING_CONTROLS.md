# v0.2 matched standing-variation controls — findings

**Status:** exploratory deterministic experiment. Not confirmatory evidence.

**Workflow:** [matched standing-variation run](https://github.com/praveenchandrahas/evolutionary-gradient-access/actions/runs/45166815441)  
**Artifact:** `ega-v02-standing-controls` (160 simulation rows, 32 paired conditions, CSVs, summary and figure)

## 1. Experimental design

This follow-up tests whether the mutation signal from the first v0.2 pilot survives stronger non-mutating controls.

The grid used barrier 8 (k_BT), mutation rates 0.05 and 0.10 per bit, replication coupling 0.5 and 1, initial rare-target concentrations (10^{-6},10^{-3},10^{-2},0.05), and static or drifting environments. The drifting environment switches from target 00 to target 11 at time 50.

Five arms were compared:

- **D:** faithful copying from the original small initial library.
- **L:** mutation and selection from exactly the same initial library as D.
- **Mmatched:** fixed uniform library initialized with the same total catalyst material as L has at the end of its run.
- **Dmatched:** uniform, faithful-copying library initialized with that same total catalyst material; it can subsequently reproduce and select, but has no mutation.
- **Moracle in the raw artifact:** a fixed library initialized with L's final genotype composition and the same total catalyst concentration. This is a *post-hoc composition-matched fixed library*, not a strict oracle upper bound: it experiences the same target schedule and starts with its own work-currency state, so its full trajectory is not guaranteed to bound L.

The matched libraries are front-loaded: they have the matched material available from time zero, whereas L accumulates it through replication. That is deliberate and is important when interpreting cumulative throughput.

**Artifact wording correction:** the generated `summary.json` describes `Moracle` as an oracle upper bound. That label is too strong. It is a post-hoc composition-matched fixed library, not a strict upper bound, because it experiences the same target schedule and has a different work-pool trajectory. The underlying run data are unchanged.

## 2. Thermodynamic and numerical checks

| Diagnostic | Result |
|---|---:|
| Simulation rows | 160 |
| Paired conditions | 32 |
| Maximum pointwise free-energy identity residual | (1.73	imes10^{-17}) |
| Maximum integrated free-energy residual | (6.37	imes10^{-6}) |
| Maximum integrated work-pool residual | (5.03	imes10^{-8}) |
| Minimum observed total entropy-production rate | (5.09	imes10^{-3}) |

The pointwise identity

[
dot G_{mathrm{reservoir}}-dot G_{mathrm{system}}=dot S_{mathrm{prod}}
]

closes to numerical precision. The integrated residuals are small quadrature errors. No state clipping was used.

## 3. Cost definitions

For this model-specific comparison:

- Fuel-conversion extent: (F=int J_1,dt).
- Catalyst material investment: (I_M=sum_i c_i(0)+int J_2,dt), because each net replication event consumes one monomer and creates one catalyst.
- Declared work investment: (I_W=G_C(0)+W_{mathrm{rep}}+W_{mathrm{maint}}), where (G_C(0)=sum_i c_i(0)(mu_C^circ+ln c_i(0)-1)), (W_{mathrm{rep}}=int J_2(mu_T-mu_D),dt), and (W_{mathrm{maint}}=int J_3(mu_T-mu_D),dt).

These are explicit accounting proxies for this reaction network, not universal cost functions. The fuel gradient input is the resource being exploited and is reported separately by the model's free-energy ledger. Initial catalyst synthesis is not dynamically simulated; its state free energy is counted as an upfront investment.

## 4. Mutation versus faithful copying from the same initial library

Mean L/D ratios across the 16 conditions in each environment:

| Metric, L/D | Static | Drifting |
|---|---:|---:|
| Late throughput | 0.9901 | 1.0141 |
| Cumulative fuel extent | 0.9942 | 1.0040 |
| Declared work investment | 1.0006 | 1.0048 |
| Catalyst material investment | 1.0005 | 1.0033 |
| Fuel extent per work | 0.9935 | 0.9992 |
| Fuel extent per catalyst material | 0.9937 | 1.0007 |

Mutation again produces a small late-throughput advantage under drift, but not a meaningful cumulative work-efficiency gain. The effect disappears as standing variation increases: at initial target-genotype concentration 0.05, the mean L/D late-throughput ratio is 1.0006 and the cumulative-fuel ratio is 0.9998. In other words, a faithful-copying population that already contains substantial standing variation nearly eliminates the mutation advantage.

In static conditions, mutation is consistently disadvantageous in this grid.

## 5. Stronger fixed and standing-variation controls

Mean L/comparator ratios across the 16 conditions per environment:

| Metric | Static: Mmatched | Drift: Mmatched | Static: Dmatched | Drift: Dmatched |
|---|---:|---:|---:|---:|
| Late throughput | 1.255 | 0.971 | 0.823 | 0.673 |
| Cumulative fuel extent | 1.041 | 0.934 | 0.819 | 0.758 |
| Declared work investment | 1.212 | 1.200 | 0.733 | 0.725 |
| Catalyst material investment | 1.000 | 1.000 | 0.733 | 0.734 |
| Fuel extent per work | 0.859 | 0.780 | 1.117 | 1.046 |
| Fuel extent per catalyst material | 1.041 | 0.934 | 1.119 | 1.033 |

Interpretation:

- **Mmatched:** Under drift, the fixed uniform library produces about 6.6% more cumulative fuel conversion than L with the same total catalyst material, while using about 20% less declared work. L can have higher late throughput in some high-standing-variation cases, but that does not translate into higher cumulative output.
- **Dmatched:** The large faithful-copying library produces substantially more total throughput than L because it begins with the same catalyst material as L's final population and can then reproduce. It also uses more work and material. L's output per unit of declared work is about 4.6% higher under drift and its output per catalyst material about 3.3% higher, but its absolute cumulative output is lower. This is a modest efficiency difference, not evidence that mutation gives greater total access.
- **Post-hoc composition-matched fixed library (raw label `Moracle`):** L has higher late throughput, but lower cumulative fuel extent per unit of material and per unit of work. The fixed library begins with L's final genotype composition at time zero, so it has a different time profile and work-pool trajectory. It is a counterfactual composition control, not an oracle bound.

## 6. Overall interpretation

The second experiment strengthens the first pilot's central caution:

1. Mutation can improve late adaptation after a target shift relative to a small, initially identical faithful-copying population.
2. That advantage becomes negligible when the faithful-copying population already has substantial standing variation.
3. A fixed library with the same total catalyst material can outperform L in cumulative throughput and work efficiency under drifting conditions.
4. A large faithful-copying standing-variation population can achieve more total throughput, although it spends more work and material.
5. The only positive cost-normalized result for L is a small advantage over Dmatched, whose population expands further and spends more resources. This does not establish a general evolutionary advantage.

**Current conclusion:** the v0.2 model does not establish that ongoing mutation and selection outperform strong fixed or standing-variation alternatives at comparable energetic and material costs. It shows conditional late adaptation, but the stronger claim remains unsupported.

## 7. The next model should remove the imposed pleiotropic link

The present model gives genotype match a direct effect on both fuel conversion and self-replication. Even though this is varied by `replication_coupling`, it remains an imposed relationship.

The next serious test should make energy capture lineage-associated:

- Genotype affects the rate at which its lineage captures the fuel gradient.
- The captured work currency, rather than a directly assigned genotype-specific replication rate, funds that lineage's reproduction.
- Mutation changes offspring genotype.
- Compartments or private work pools prevent one genotype from capturing energy while another freely uses it.
- Replication kinetics are otherwise identical across genotypes.

That would test whether differential access to a gradient can generate selection and sustained adaptation, rather than assuming the catalytic phenotype directly accelerates reproduction.

Further requirements remain: stochastic finite populations, larger and rugged genotype landscapes, explicit mutation/repair costs, and a more complete comparison of time-dependent material budgets.
