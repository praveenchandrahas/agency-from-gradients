"""S14 re-check: the copier (P) against the mineral (M), with the entropy of mixing counted.

S14 recorded reaction entropy only: Phi(before) - Phi(after) over each reaction step. In a flow
reactor that misses the entropy made when the feed mixes into the reactor. S15's control pilot
showed why that matters: a better catalyst drives the fuel closer to equilibrium, so each
reaction releases less, and the loss reappears as mixing. Counting reactions alone can rank a
better catalyst lower.

This script re-runs the 10 P and 10 M runs of S14 with the same chemistries, drive and seeds,
and the same reactor code. It adds one book: the mixing entropy rate,
    dil * sum over species of [n_in ln(n_in / n) - n_in + n]     (k_B per residence time),
accumulated over every step from the counts at the start of the step. Nothing in the dynamics
changes, so the reaction entropy must reproduce S14's published numbers exactly. That is the
first check. The second: in steady state, reactions plus mixing should equal the free energy
carried in minus carried out, dil * [G(n_in) - G(n_mean)], with G(n) = sum n (g - ln c0 + ln n - 1).

Post hoc. This is a correction to a descriptive number in S14, not a preregistered test. It
does not touch any S14 verdict: those are about whether copying emerges, not about entropy.

    PYTHONPATH=src python -m agency_gradients.experiments.s14_mixing_recheck --out out --workers 2
"""
from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from ..soup.chemistry import COPIER, COPIER_SEED, designed_chemistry
from ..soup.reactor import Reactor
from .s14_soup import ARM_CODE, DRIVES, PRM, TOP

PUBLISHED = {  # S14 late-window reaction entropy, from docs/results/s14.md (run 43258823346)
    "P": 8070.0, "M": 8077.4,
}


class MixingReactor(Reactor):
    """The S14 reactor, unchanged, plus a mixing-entropy book."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.mix = np.zeros(len(self.series["dt"]))
        self._fed = self.n_in > 0

    def mix_rate(self, n: np.ndarray) -> float:
        nin, fed = self.n_in, self._fed
        if (n[fed] <= 0).any():
            raise RuntimeError("a fed species hit zero; the mixing rate is unbounded")
        nn = n.astype(float)
        t = nn.copy()                                    # unfed species: c_in = 0, term = n
        t[fed] = nin[fed] * np.log(nin[fed] / nn[fed]) - nin[fed] + nn[fed]
        return self.prm.dil * float(t.sum())

    def step(self):
        b, t0, n0 = self.bin, self.t, self.n.copy()
        super().step()
        tau = self.t - t0
        self.mix[b] += tau * self.mix_rate(n0)


def g_fn(rx: Reactor, n: np.ndarray) -> float:
    n = np.asarray(n, float)
    pos = n > 0
    return float((n[pos] * (rx.glin[pos] + np.log(n[pos]) - 1.0)).sum())


def run_one(job):
    arm, cid = job
    chem = designed_chemistry(arm, PRM)
    ss = [14, 2, ARM_CODE[arm], int(cid), DRIVES.index(TOP)]
    rx = MixingReactor(chem, PRM, TOP, np.random.SeedSequence(ss), flux_ep=True)
    if arm == "P":
        rx.n[chem.index(COPIER)] = COPIER_SEED
        rx.n_start, rx.phi0 = rx.n.copy(), rx.phi(rx.n)
    rx.run()
    late = rx.late()
    lo = rx.late_from
    dt = late["dt"]
    mix = float(rx.mix[lo:].sum() / dt)
    nbar = rx.mean_late_counts()
    balance = PRM.dil * (g_fn(rx, rx.n_in) - g_fn(rx, nbar))
    # where the mixing comes from: fuel, waste, monomers, polymers
    fed = rx.n_in > 0
    def part(sel):
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.where(fed[sel], rx.n_in[sel] * np.log(rx.n_in[sel] / np.maximum(nbar[sel], 1e-12))
                         - rx.n_in[sel] + nbar[sel], nbar[sel])
        return PRM.dil * float(t.sum())
    iF, iW = rx.iF, rx.iW
    ia, ib = chem.index("a"), chem.index("b")
    poly = np.ones(rx.S, bool); poly[[iF, iW, ia, ib]] = False
    one = lambda i: np.array([i])
    return dict(arm=arm, chem=cid, capture=late["capture"], sigma_rxn=late["sigma_rate"], sigma_mix=mix,
                sigma_total=late["sigma_rate"] + mix, balance=balance,
                mix_fuel=part(one(iF)), mix_waste=part(one(iW)), mix_monomers=part(np.array([ia, ib])),
                mix_polymers=part(np.flatnonzero(poly)),
                fuel_left=float(nbar[iF] / rx.n_in[iF]), led_phi=rx.ledger_residuals()["phi_rel"])


def boot(x, nb=10_000, seed=14):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), (nb, len(x)))].mean(axis=1)
    return float(x.mean()), float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))


def boot_diff(x, y, nb=10_000, seed=14):
    """Difference of means, P - M. The arms are independent runs (each is one designed
    chemistry; the run index only sets the seed), so they are resampled separately."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    rng = np.random.default_rng(seed)
    d = (x[rng.integers(0, len(x), (nb, len(x)))].mean(axis=1)
         - y[rng.integers(0, len(y), (nb, len(y)))].mean(axis=1))
    return float(x.mean() - y.mean()), float(np.quantile(d, 0.025)), float(np.quantile(d, 0.975))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--from-json", default=None, help="rebuild the report from saved runs")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.from_json:
        rows = json.load(open(a.from_json))
    else:
        jobs = [(arm, c) for arm in ("P", "M") for c in range(10)]
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            rows = list(ex.map(run_one, jobs))
    with open(f"{a.out}/s14_mixing_recheck.json", "w") as f:
        json.dump(rows, f, indent=1)
    by = {arm: [r for r in rows if r["arm"] == arm] for arm in ("P", "M")}
    f = lambda t, d=1: f"{t[0]:.{d}f} [{t[1]:.{d}f}, {t[2]:.{d}f}]"
    L = ["Late-window means, k_B per residence time. 95% bootstrap intervals, 10,000 resamples; P − M resamples the arms independently.", "",
         "| | Copier (P) | Mineral (M) | P − M |", "|---|---|---|---|"]
    for key, label in (("capture", "Capture"), ("sigma_rxn", "Reactions only"), ("sigma_mix", "Mixing"),
                       ("sigma_total", "**Total**"), ("balance", "Free energy in − out (check)")):
        d = 3 if key == "capture" else 1
        xp, xm = [r[key] for r in by["P"]], [r[key] for r in by["M"]]
        L.append(f"| {label} | {f(boot(xp), d)} | {f(boot(xm), d)} | {f(boot_diff(xp, xm), d)} |")
    L += ["", "Mixing by source (means): " + "; ".join(
        f"{arm}: fuel {np.mean([r['mix_fuel'] for r in by[arm]]):.0f}, waste {np.mean([r['mix_waste'] for r in by[arm]]):.0f}, "
        f"monomers {np.mean([r['mix_monomers'] for r in by[arm]]):.0f}, polymers {np.mean([r['mix_polymers'] for r in by[arm]]):.0f}"
        for arm in ("P", "M"))]
    L += ["", "Reproduction of S14's published reaction entropy: " + "; ".join(
        f"{arm} {np.mean([r['sigma_rxn'] for r in by[arm]]):.1f} (published {PUBLISHED[arm]})" for arm in ("P", "M"))]
    L += [f"Largest relative gap, total against the free-energy balance: "
          f"{max(abs(r['sigma_total'] - r['balance']) / r['balance'] for r in rows):.2e}",
          f"Largest Phi-ledger residual: {max(r['led_phi'] for r in rows):.1e}"]
    with open(f"{a.out}/s14_mixing_recheck.md", "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
