# Zero-dimensional stellar–planetary ledger (v0.1)

This is the project's first executable thermodynamic accounting baseline. It is deliberately not a climate model, chemical reaction model, origin-of-life simulation or evolutionary simulation.

## Questions it answers

- How much stellar power does a spherical planet intercept?
- What are the global-mean incoming, reflected, absorbed and outgoing energy fluxes?
- What effective emission temperature closes a simple radiative equilibrium?
- What net energy storage rate follows when an emission temperature is specified instead?
- What idealized source-temperature Petela exergy estimate follows from a stated reference environment?
- What are the incoming, Lambertian-reflected and outgoing thermal radiation entropy fluxes when evaluated from Planck-mode entropy?

## Why the radiation entropy calculation is spectral

For photon occupation number n, the entropy per bosonic mode is proportional to (1+n) ln(1+n) - n ln(n). The code integrates this expression over dimensionless frequency. It models the finite angular size of the star; treats shortwave reflection as spectrally neutral Lambertian reflection; and treats planetary longwave emission as a uniform graybody.

This approach is materially better than replacing every radiation entropy flux with energy_flux / temperature. Wu and Liu (2010) show that simple approximations can produce errors exceeding 30% for Earth's radiative entropy budget, and that the reflected-light result depends on assumptions about diffuse versus specular reflection.

## Install and run

From the repository root, run these commands:

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -e .
    python -m thermodynamic_emergence
    python -m thermodynamic_emergence --json

Run tests with:

    python -m unittest discover -s tests -v

## Current reference case

The default configuration is a rounded Earth–Sun-like case: star effective temperature 5772 K, star radius 695,700 km, orbital distance 1 AU, planet radius 6,371 km, Bond albedo 0.30 and thermal emissivity 1.0. The output is a theoretical graybody reference, not a reconstruction of Earth's observed climate.

| Quantity | Approximate result |
|---|---:|
| Direct stellar irradiance | 1361.17 W m⁻² |
| Global-mean incoming sunlight | 340.29 W m⁻² |
| Reflected shortwave | 102.09 W m⁻² |
| Absorbed shortwave | 238.20 W m⁻² |
| Outgoing thermal radiation at equilibrium | 238.20 W m⁻² |
| Effective emission temperature | 254.59 K |
| Incoming stellar entropy flux | 0.07861 W m⁻² K⁻¹ |
| Lambertian reflected entropy flux | 0.10425 W m⁻² K⁻¹ |
| Outgoing thermal entropy flux | 1.24754 W m⁻² K⁻¹ |
| Net radiative entropy export | 1.27318 W m⁻² K⁻¹ |

The net radiative entropy export is a useful cross-check against Wu and Liu's (2010) Planck-spectral treatment, under similar idealized albedo and emissivity assumptions. It is not, by itself, a measured or independently validated value of Earth's total internal entropy production.

## Accounting rules

1. Energy is conserved; exergy destruction is not energy destruction.
2. Net radiative entropy export is only a conditional proxy for internal entropy generation: besides energy balance, the system must have no secular entropy storage and no matter or other non-radiative entropy transfer across the boundary. This model cannot independently test the entropy-storage assumption.
3. If an explicit emission temperature creates an energy imbalance, the model reports an energy storage/release rate and does not infer entropy production from that energy imbalance. Energy storage alone does not determine entropy storage rate.
4. The Petela result is labelled an approximation. It uses a source-temperature factor and does not fully resolve the diluted, finite-angular-size radiation field.
5. No output is a fitness function or a measure of life, agency, intelligence or complexity.

## Key references

- Wu, W., & Liu, Y. (2010). “Radiation entropy flux and entropy production of the Earth system.” Reviews of Geophysics, 48, RG4006. https://doi.org/10.1029/2008RG000275
- Rodríguez, E., Cardemil, J. M., Starke, A. R., & Escobar, R. (2022). “Modelling the Exergy of Solar Radiation: A Review.” Energies, 15(4), 1477. https://doi.org/10.3390/en15041477
- NIST 2022 CODATA recommended values: https://physics.nist.gov/cuu/Constants/
