"""Command-line entry point for the continuously driven CSTR model."""
from __future__ import annotations

import argparse
import json

from .open_reactor import (
    OpenReactorConfig,
    compare_open_reactor,
    run_open_reactor_sweep,
    run_open_reactor_recovery_sweep,
    simulate_open_reactor,
    simulate_open_reactor_perturbation,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate a continuously driven mutually catalytic CSTR")
    parser.add_argument("--json", action="store_true", help="print complete results as JSON")
    parser.add_argument("--compare", action="store_true", help="compare catalysis with the matched-flow null")
    parser.add_argument("--sweep", action="store_true", help="sweep catalytic strength and dilution rate")
    parser.add_argument("--perturb-sweep", action="store_true", help="sweep catalyst removal and post-event catalyst feed")
    parser.add_argument("--perturbation-time", type=float, default=150.0, help="catalyst-removal time in seconds")
    parser.add_argument("--removal", type=float, default=0.99, help="fraction of X and Y removed")
    parser.add_argument("--post-catalyst-feed", type=float, default=None, help="post-event X/Y feed activity")
    parser.add_argument("--duration", type=float, default=300.0, help="simulation duration in seconds")
    parser.add_argument("--dt", type=float, default=0.002, help="RK4 time step in seconds")
    parser.add_argument("--flow", type=float, default=0.05, help="CSTR dilution rate in inverse seconds")
    parser.add_argument("--catalysis", type=float, default=10.0, help="mutual catalytic strength")
    args = parser.parse_args()
    cfg = OpenReactorConfig(duration_s=args.duration, time_step_s=args.dt,
                            flow_rate_s=args.flow, catalytic_strength=args.catalysis)
    if args.perturb_sweep:
        result = run_open_reactor_recovery_sweep(cfg, perturbation_time_s=args.perturbation_time)
    elif args.sweep:
        result = run_open_reactor_sweep(cfg)
    elif args.compare:
        result = compare_open_reactor(cfg)
    elif args.post_catalyst_feed is not None:
        result = simulate_open_reactor_perturbation(cfg, perturbation_time_s=args.perturbation_time,
                                                    removal_fraction=args.removal,
                                                    post_perturbation_catalyst_feed_activity=args.post_catalyst_feed)
    else:
        result = simulate_open_reactor(cfg)
    if args.json or args.sweep or args.perturb_sweep:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.compare:
        c = result["comparison"]
        print(f"Catalytic X+Y: {c['catalytic_X_plus_Y']:.8g}")
        print(f"Uncatalysed X+Y: {c['uncatalysed_X_plus_Y']:.8g}")
        print(f"X+Y ratio: {c['X_plus_Y_ratio']:.8g}")
        print(f"NESS detected (catalytic / null): {c['catalytic_ness']} / {c['uncatalysed_ness']}")
    else:
        d = result["diagnostics"]
        print(f"Final X+Y: {result['final']['X'] + result['final']['Y']:.8g}")
        print(f"Operational NESS detected: {d['ness_detected']}")
        print(f"Relative endpoint drift: {d['ness_relative_endpoint_drift']:.4g}")
        print(f"Maximum window CV: {d['ness_max_species_coefficient_of_variation']:.4g}")
        print(f"Reaction entropy production: {d['final_reaction_entropy_production_J_L_K_s']:.8g} J L^-1 K^-1 s^-1")
        print(f"Reservoir-exchange entropy production: {d['final_reservoir_exchange_entropy_production_J_L_K_s']:.8g} J L^-1 K^-1 s^-1")
        print(result["accounting"]["warning"])


if __name__ == "__main__":
    main()
