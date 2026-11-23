"""Command-line runner for the local chemical disequilibrium model."""

import argparse
import json

from .chemistry import ChemicalConfig, run_feed_sweep, simulate_chemical_network


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the minimal chemostatted autocatalytic network")
    parser.add_argument("--json", action="store_true", help="print the full baseline result as JSON")
    parser.add_argument("--sweep", action="store_true", help="run the default feed-activity sweep")
    args = parser.parse_args()

    if args.sweep:
        result = run_feed_sweep([1.0e-6, 0.05, 0.2, 0.5, 1.0, 2.0])
        print(json.dumps(result, indent=2))
        return

    result = simulate_chemical_network(ChemicalConfig())
    if args.json:
        print(json.dumps(result, indent=2))
        return

    final = result["final"]
    print("Minimal local chemical disequilibrium model")
    print("-------------------------------------------")
    print("Network: A + X <-> 2X + W; X <-> D")
    print(f"Feed activity:                  {result['configuration']['feed_activity']:.6g}")
    print(f"Final catalyst activity:        {final['catalyst_activity']:.8g}")
    print(f"Analytic fixed point:            {final['analytic_equilibrium_catalyst_activity']:.8g}")
    print(f"Enrichment over low-feed control:{final['catalyst_enrichment_over_background']: .6g}x")
    print(f"Entropy production:              {final['total_entropy_production_J_L_K_s']:.6g} J/(L K s)")
    print(f"Free-energy dissipation:         {result['accounting']['free_energy_dissipation_rate_J_L_s']:.6g} J/(L s)")
    print("Interpretation: abstract autocatalysis only; not a model of life or abiogenesis.")


if __name__ == "__main__":
    main()
