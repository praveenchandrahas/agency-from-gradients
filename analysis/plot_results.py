"""Create compact plots from paired_contrasts.json."""
import argparse
import json
from pathlib import Path
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    data = json.loads((args.results / "paired_contrasts.json").read_text())
    out = args.results / "figures"
    out.mkdir(exist_ok=True)
    for design in data:
        for metric, label in (("late_throughput", "Late-window net throughput"),
                              ("cumulative_sigma", "Cumulative implemented entropy")):
            fig, ax = plt.subplots(figsize=(8, 5))
            for comparator in ("Mmatched", "D", "Amatched"):
                means, lows, highs = [], [], []
                for barrier in ("0.0", "4.0", "8.0", "12.0"):
                    item = data[design][barrier][f"L_minus_{comparator}"][metric]
                    means.append(item["mean"])
                    lows.append(item["mean"] - item["ci95_low"])
                    highs.append(item["ci95_high"] - item["mean"])
                ax.errorbar([0, 4, 8, 12], means, yerr=[lows, highs],
                            marker="o", capsize=3, label=f"L − {comparator}")
            ax.axhline(0, linewidth=1)
            ax.set_xlabel("Activation barrier (kT)")
            ax.set_ylabel(label + " difference")
            ax.set_title(f"{design}: evolutionary arm contrasts")
            ax.legend()
            fig.tight_layout()
            fig.savefig(out / f"{design}_{metric}.png", dpi=160)
            plt.close(fig)


if __name__ == "__main__":
    main()
