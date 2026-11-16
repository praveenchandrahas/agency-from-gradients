"""The six published scenarios, run again with the instruments on. Feeds E2 and E3.

Nothing about the model changes. Replicates 0 to 5 repeat the paper's runs bit for bit.
The neutral markers and the demography are read off the same runs.
"""
import sys

from common import REPLICATES, Options, execute

sys.path.insert(0, __file__.rsplit("/", 2)[0])
from planet import SCENARIOS  # noqa: E402

SERIES = ["population", "occupied_patch_fraction", "biotic_power_harnessed_TW", "biotic_power_per_entity_GW",
          "biotic_capture_fraction_of_photo_pool", "mean_net_energy_units", "net_q10", "net_q50", "net_q90",
          "frac_net_below_threshold", "growth_realized", "growth_expected", "growth_meanfield",
          "mean_survival_probability", "birth_rate_per_entity", "crowding_entity_weighted",
          "mean_entities_per_occupied_patch", "pop_share_top5pc_patches", "frac_on_peak", "choice_true_best",
          "mean_collector", "mean_sensing", "mean_processing", "mean_prediction", "mean_planning", "mean_action",
          "mean_agency_composite", "marker_composite", "marker_1", "marker_2", "marker_3", "marker_4", "marker_5",
          "mean_cooperation", "mean_technology", "mean_infrastructure", "delta_radiative_entropy_percent"]

tasks = [(dict(scenario_key=key), key, rep, Options()) for key in SCENARIOS for rep in REPLICATES]

if __name__ == "__main__":
    execute("pure", tasks, SERIES, series_every=5, smoke="--smoke" in sys.argv)
