"""Entropy bookkeeping for a star with and without a cold absorber.

Used by docs/unlocking.md. No simulation: textbook radiation thermodynamics.

Starlight streaming into empty space keeps its entropy; nothing new is made
after it leaves the star. An absorber that re-radiates the same power as a
black body at temperature T_d emits entropy at (4/3) L / T_d. The absorber's
composition does not enter: a Dyson sphere and a dust shell at the same
temperature and covering fraction give the same numbers.

Work that a civilization extracts from the light ends as heat too, so it
changes nothing here. What it changes is the incentive: the maximum work
fraction rises as T_d falls (Landsberg limit for black-body radiation).

Run:  python analysis/dyson_entropy.py
"""

import math

L_SUN = 3.828e26      # W, IAU nominal solar luminosity
T_SUN = 5772.0        # K, IAU nominal effective temperature
SIGMA = 5.670374e-8   # W m^-2 K^-4
AU = 1.495978707e11   # m


def entropy_rate(power_w: float, temp_k: float) -> float:
    """Entropy carried by black-body radiation of this power and temperature, W/K."""
    return 4.0 / 3.0 * power_w / temp_k


def shell_radius_au(power_w: float, temp_k: float) -> float:
    """Radius of a spherical shell that radiates power_w outward at temp_k."""
    return math.sqrt(power_w / (4 * math.pi * SIGMA * temp_k**4)) / AU


def landsberg(t_low: float, t_high: float) -> float:
    """Maximum fraction of black-body radiation at t_high convertible to work, sink at t_low."""
    x = t_low / t_high
    return 1 - 4.0 / 3.0 * x + x**4 / 3.0


def carnot(t_low: float, t_high: float) -> float:
    return 1 - t_low / t_high


def main() -> None:
    s_star = entropy_rate(L_SUN, T_SUN)
    print(f"Starlight leaving the Sun: {s_star:.3e} W/K (unchanged in free flight)\n")
    print("| Absorber T (K) | Entropy out (W/K) | Ratio to starlight | Shell radius (AU) | Carnot | Landsberg |")
    print("|---|---|---|---|---|---|")
    for t in (300.0, 100.0, 50.0, 2.725):
        s = entropy_rate(L_SUN, t)
        print(
            f"| {t:g} | {s:.2e} | {s / s_star:,.0f} | {shell_radius_au(L_SUN, t):,.1f} "
            f"| {carnot(t, T_SUN):.3f} | {landsberg(t, T_SUN):.3f} |"
        )


if __name__ == "__main__":
    main()
