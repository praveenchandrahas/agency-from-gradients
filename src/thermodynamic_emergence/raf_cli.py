"""Command-line entry point for the finite-resource RAF-like batch model."""
from __future__ import annotations

import argparse
import json

from .raf import RafConfig, compare_catalysis, simulate_raf_network


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate a finite-resource mutually catalytic network")
    parser.add_argument("--json", action="store_true", help="print the complete simulation result as JSON")
    parser.add_argument("--compare", action="store_true", help="compare mutual catalysis with the uncatalysed null")
    parser.add_argument("--duration", type=float, default=10.0, help="batch duration in seconds")
    parser.add_argument("--dt", type=float, default=1.0e-3, help="RK4 time step in seconds")
    args = parser.parse_args()
    config = RafConfig(duration_s=args.duration, time_step_s=args.dt)
    result = compare_catalysis(config) if args.compare else simulate_raf_network(config)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.compare:
        print(f"Finite-time X+Y amplification ratio: {result['finite_time_amplification_ratio']:.6g}")
        print(f"Catalytic integrated entropy production: {result['catalytic_integrated_entropy_production_J_L_K']:.6g} J L^-1 K^-1")
        print(f"Uncatalysed integrated entropy production: {result['uncatalysed_integrated_entropy_production_J_L_K']:.6g} J L^-1 K^-1")
        print(result["equilibrium_warning"])
    else:
        print(f"Final X activity: {result['final']['X']:.6g}")
        print(f"Final Y activity: {result['final']['Y']:.6g}")
        print(f"Food conversion: {result['diagnostics']['food_conversion_fraction']:.6g}")
        print(f"Integrated entropy production: {result['diagnostics']['integrated_reaction_entropy_production_J_L_K']:.6g} J L^-1 K^-1")
        print(f"Maximum absolute moiety-balance error: {max(abs(v) for v in result['diagnostics']['moiety_balance_errors'].values()):.3g}")


if __name__ == "__main__":
    main()
