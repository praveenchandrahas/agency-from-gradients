"""E1. Carriers and non-carriers on one planet.

Arms
  full       carriers have everything the paper gives them: the Equation 4 bonus and directed movement
  bonus      carriers keep the Equation 4 bonus but move at random, like non-carriers
  movement   carriers keep directed movement but get no Equation 4 bonus

The full arm starts at 10%, 50% and 90% carriers. The other two start at 50%.
"""
import sys

from common import REPLICATES, Options, execute

sys.path.insert(0, __file__.rsplit("/", 2)[0])
from planet import ENVIRONMENTS  # noqa: E402

SERIES = ["population", "carrier_fraction", "occupied_patch_fraction", "occupied_fraction_c", "occupied_fraction_n",
          "biotic_power_harnessed_TW", "net_mean_c", "net_mean_n", "survival_mean_c", "survival_mean_n",
          "crowding_c", "crowding_n", "frac_on_peak_c", "frac_on_peak_n", "action_c", "mean_agency_composite",
          "marker_composite_c"]

ARMS = {
    "full": dict(eq4_bonus=True, directed_movement=True),
    "bonus": dict(eq4_bonus=True, directed_movement=False),
    "movement": dict(eq4_bonus=False, directed_movement=True),
}

tasks = []
for env, key in ENVIRONMENTS.items():
    for arm, switches in ARMS.items():
        for start in ((0.1, 0.5, 0.9) if arm == "full" else (0.5,)):
            for rep in REPLICATES:
                tasks.append((dict(env=env, arm=arm, start=start), key, rep,
                              Options(carrier_fraction=start, **switches)))

if __name__ == "__main__":
    execute("mixed", tasks, SERIES, series_every=10, smoke="--smoke" in sys.argv)
