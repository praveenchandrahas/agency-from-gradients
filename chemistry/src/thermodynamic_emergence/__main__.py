"""Command-line entry point: python -m thermodynamic_emergence [--json]."""

import argparse
import json

from .model import calculate_earth_like_baseline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Earth-like planetary thermodynamic ledger")
    parser.add_argument("--json", action="store_true", help="print the full result as JSON")
    args = parser.parse_args()
    result = calculate_earth_like_baseline()

    if args.json:
        print(json.dumps(result, indent=2))
        return

    energy = result["energy"]
    entropy = result["radiative_entropy"]
    exergy = result["exergy_approximation"]
    print("Earth-like zero-dimensional stellar–planetary ledger")
    print("----------------------------------------------------")
    print(f"Direct stellar irradiance:       {result['geometry']['direct_stellar_irradiance_normal_W_m2']:.3f} W/m²")
    print(f"Global-mean incoming sunlight:   {energy['incoming_stellar_global_mean_W_m2']:.3f} W/m²")
    print(f"Reflected shortwave:             {energy['reflected_shortwave_global_mean_W_m2']:.3f} W/m²")
    print(f"Absorbed shortwave:              {energy['absorbed_shortwave_global_mean_W_m2']:.3f} W/m²")
    print(f"Outgoing thermal radiation:      {energy['outgoing_thermal_global_mean_W_m2']:.3f} W/m²")
    print(f"Effective emission temperature: {energy['effective_emission_temperature_K']:.3f} K")
    print(f"Energy storage rate:             {energy['radiative_energy_storage_rate_global_mean_W_m2']:.6g} W/m²")
    print()
    print("Radiative entropy fluxes (Planck spectral calculation)")
    print(f"Incoming stellar:                {entropy['incoming_stellar_entropy_global_mean_W_m2K']:.6f} W/(m² K)")
    print(f"Reflected shortwave:             {entropy['reflected_shortwave_entropy_global_mean_W_m2K']:.6f} W/(m² K)")
    print(f"Outgoing thermal:                {entropy['outgoing_thermal_entropy_global_mean_W_m2K']:.6f} W/(m² K)")
    print(f"Net radiative entropy export:    {entropy['net_radiative_entropy_export_global_mean_W_m2K']:.6f} W/(m² K)")
    value = entropy["conditional_internal_entropy_generation_if_entropy_steady_global_mean_W_m2K"]
    if value is None:
        print("Conditional entropy generation: not inferred (non-zero energy storage)")
    else:
        print(f"Conditional entropy generation*: {value:.6f} W/(m² K)")
        print("*Requires no secular entropy storage or other boundary entropy transfers.")
    print()
    print("Exergy (approximate Petela source-temperature estimate)")
    print(f"Absorbed solar exergy:           {exergy['absorbed_solar_exergy_global_mean_approx_W_m2']:.3f} W/m²")
    print("Note: see model documentation for assumptions and limitations.")


if __name__ == "__main__":
    main()
