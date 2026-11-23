"""Pilot on the controls only: N (passive) and U (designer bound) across the barrier dial.

Seeds 1000 and up. Not evidence. Its only job is to check that the dial has room:
the passive curve should fall toward zero as B rises while the designer key stays up.
Arms M, D and L are not run here (SPEC.md, blind-tuning rule).
"""
import json
import sys

import numpy as np

from locks import Config, run

B_GRID = (0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0)
N_FIXED = (100, 500)
SEEDS = range(1000, 1003)
T_END, T_LATE = 100.0, 50.0


def main(out):
    rows = []
    for B in B_GRID:
        cells = [("N", 0)] + [("U", n) for n in N_FIXED]
        for arm, nf in cells:
            r = [run(Config(arm=arm, B=(B,), n_fixed=nf), seed=s, t_end=T_END, t_late=T_LATE) for s in SEEDS]
            rows.append(dict(arm=arm, n_fixed=nf, B=B,
                             sigma=float(np.mean([x["sigma_late"] for x in r])),
                             sigma_rxn=float(np.mean([x["sigma_rxn_late"] for x in r])),
                             spent=float(np.mean([x["spent_late"][0] for x in r]))))
    json.dump(rows, open(out, "w"), indent=1)
    print(f"{'B':>5} {'arm':>4} {'n':>4} {'total sigma':>12} {'reactions only':>15} {'fuel spent':>11}")
    for x in rows:
        print(f"{x['B']:5.1f} {x['arm']:>4} {x['n_fixed']:4d} {x['sigma']:12.1f} {x['sigma_rxn']:15.1f} {x['spent']:11.4f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/pilot_controls.json")
