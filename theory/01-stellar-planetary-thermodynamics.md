# 01 — Stellar–planetary thermodynamics
## A first-principles energy, exergy and entropy framework

**Status:** Technical foundation, version 0.1  
**Scope:** A planet intercepting stellar radiation and returning energy to space  
**Purpose:** Specify the minimum thermodynamic accounting required before modelling dissipative organization.

---

## 1. The physical picture

A star emits electromagnetic radiation because of its high temperature and internal energy-generation processes. At a planet's orbit, only a small fraction of the star's total luminosity is intercepted. The planet reflects some incident radiation, absorbs the rest, redistributes and transforms part of that absorbed energy, stores a portion temporarily, and ultimately emits energy back to space, predominantly as thermal infrared radiation.

An important correction to an intuitive picture is needed: **a planet is not generally a reservoir that stores most incoming sunlight and releases it much later.** In long-term global energy balance, the energy entering the planetary system is approximately balanced by reflected sunlight plus outgoing thermal radiation. The planet is continuously absorbing, transforming and re-emitting energy. Oceans, atmosphere, land, ice, chemical reservoirs and biomass store or release energy over different timescales, but most absorbed solar power is not accumulated over geological timescales. NASA's overview of Earth's energy budget describes this top-of-atmosphere balance and the intervening surface and atmospheric pathways [1].

The thermodynamic interest lies in the **quality and gradients** of incoming energy, the irreversible transformations occurring within the planetary system, and the entropy carried away by outgoing radiation. Energy is conserved; exergy can be consumed or destroyed; entropy is generated and transported.

The first model must keep these ledgers separate.

## 2. System boundary: what exactly are we accounting for?

For the initial model, define the control volume as the entire planet and its atmosphere, bounded by a spherical surface at the top of the atmosphere (TOA).

Across this boundary, account for:

**Radiative energy entering**
- Direct and diffuse stellar radiation incident on the planet.

**Radiative energy leaving**
- Reflected shortwave radiation.
- Thermal longwave radiation emitted to space by the atmosphere, clouds and surface through atmospheric windows.

**Other exchanges**
- Energy and entropy carried by matter that escapes or enters, if included.
- Tidal, mechanical or other external work/energy transfers, if relevant to the chosen planet.
- Any other energy transfer crossing the declared boundary.

For a first Earth-like global model, matter exchange across the TOA can be neglected as an explicit approximation. The internal energy sources associated with the planet's interior can initially be omitted or represented as a separately specified term. This is a modelling choice, not a claim that such processes do not exist.

The stellar interior is **outside** this first control volume. The model treats stellar radiation as an imposed boundary input. It therefore does not calculate nuclear energy generation or entropy production inside the star. Those belong to a larger star–planet–space model.

Be explicit about this boundary in every reported energy or entropy production figure. A planetary entropy budget is not the entropy budget of the star–planet system or of the Universe.

## 3. Stellar irradiance at the planet

For a first approximation, model the star as a blackbody of effective temperature T★ and radius R★. Its luminosity is

\[
L_\star = 4\pi R_\star^2 \sigma T_\star^4,
\]

where σ is the Stefan–Boltzmann constant.

At orbital distance d, assuming d is much greater than R★ and negligible absorption between star and planet, the irradiance on a surface perpendicular to the incoming rays is

\[
S_\star = \frac{L_\star}{4\pi d^2}
= \sigma T_\star^4 \left(\frac{R_\star}{d}\right)^2.
\]

For a planet of radius Rp, the intercepted power is irradiance multiplied by the planet's cross-sectional area:

\[
P_{\mathrm{in}} = \pi R_p^2 S_\star.
\]

The planet's full surface area is \(4\pi R_p^2\). Consequently, the global and time mean incoming flux for a spherical planet under steady illumination is

\[
\overline{F}_{\mathrm{in}} = \frac{S_\star}{4}.
\]

The factor of four is geometric: the planet intercepts radiation over a disk, while the global mean is defined over its full sphere. Rotation, orbital eccentricity, obliquity, clouds and spatially varying illumination matter for resolved models, but not for this first global-mean identity.

For Earth, the solar irradiance at mean orbital distance is approximately \(1.36\ \mathrm{kW\,m^{-2}}\), corresponding to a global mean incoming flux near \(340\ \mathrm{W\,m^{-2}}\) before reflection [1].

## 4. Reflection and absorption

Define the **Bond albedo** αB as the fraction of total incident stellar radiant power reflected by the planet, integrated over wavelength and direction. In a zero-dimensional model, treat it as a single parameter between zero and one.

Then

\[
P_{\mathrm{ref}} = \alpha_B P_{\mathrm{in}},
\]

\[
P_{\mathrm{abs}} = (1-\alpha_B)P_{\mathrm{in}}.
\]

In global-mean flux units:

\[
F_{\mathrm{abs}} = (1-\alpha_B)\frac{S_\star}{4}.
\]

The distinction matters:
- Reflected photons leave the planetary control volume without being absorbed.
- Absorbed photons transfer energy into the planetary system.
- Reflection is not necessarily thermodynamically neutral. Scattering can redistribute radiation across directions and increase its entropy even when reflected energy is approximately unchanged.

A Bond albedo is sufficient for a first energy budget. It is **not** sufficient for a detailed radiation-entropy calculation, because the entropy of reflected light depends on its spectrum and angular distribution as well as its total energy.

## 5. The simplest radiative-equilibrium model

First ignore atmospheric structure and assume the planet emits as a spatially uniform blackbody at effective temperature Te. Its thermal emission power is

\[
P_{\mathrm{LW}} = 4\pi R_p^2 \sigma T_e^4.
\]

At radiative equilibrium, with no net energy storage and no other energy sources or exports,

\[
P_{\mathrm{abs}} = P_{\mathrm{LW}}.
\]

Dividing by the planetary area gives

\[
(1-\alpha_B)\frac{S_\star}{4} = \sigma T_e^4,
\]

and therefore

\[
T_e = \left[
\frac{(1-\alpha_B)S_\star}{4\sigma}
\right]^{1/4}.
\]

For an illustrative Earth calculation, use \(S_\star \approx 1360\ \mathrm{W\,m^{-2}}\) and \(\alpha_B \approx 0.29\). The global-mean incoming flux is \(340\ \mathrm{W\,m^{-2}}\); about 29% is reflected and about 71% absorbed, giving an absorbed flux of roughly \(241\ \mathrm{W\,m^{-2}}\). The corresponding blackbody effective emission temperature is about \(255\ \mathrm{K}\). These rounded values are consistent with NASA's energy-budget explanation [1].

**This is not the global mean surface temperature.** Earth's global mean surface temperature is about \(288\ \mathrm{K}\), while its effective radiating temperature is about \(255\ \mathrm{K}\). The atmosphere, clouds and vertical distribution of infrared opacity matter: much of the outgoing longwave radiation to space originates from atmospheric levels colder than the surface [1, 2].

The zero-dimensional equation is a conservation check. It is not a climate model and must not be used to infer surface conditions, atmospheric structure or local habitability.

## 6. Energy balance away from equilibrium

The planet need not be in exact radiative equilibrium at every moment. Oceans, atmosphere, land, ice, chemical reservoirs and biomass can gain or lose energy.

For the TOA control volume, a simplified energy balance is

\[
\frac{dE_{\mathrm{sys}}}{dt}
=
P_{\mathrm{in}}
-
P_{\mathrm{ref}}
-
P_{\mathrm{LW}}
+
P_{\mathrm{other,in}}
-
P_{\mathrm{other,out}}.
\]

Here:
- Esys is the total energy stored within the defined planetary control volume.
- Pin is incoming stellar radiation.
- Pref is reflected shortwave power leaving the system.
- PLW is outgoing thermal longwave power.
- The other terms represent explicitly declared non-radiative energy or work transfers across the boundary.

Equivalently, if Pabs = Pin − Pref,

\[
\frac{dE_{\mathrm{sys}}}{dt}
=
P_{\mathrm{abs}} - P_{\mathrm{LW}}
+
P_{\mathrm{other,in}}-P_{\mathrm{other,out}}.
\]

The storage term can include thermal energy, chemical free energy, gravitational potential energy, kinetic energy and other relevant reservoirs. Internal transfers — for example, from radiation to heat, from heat to atmospheric motion, or from photosynthetic capture to chemical energy — do not disappear from the total energy balance. They change the form and location of energy inside the boundary.

At long-term steady state, with negligible net non-radiative export/import and no secular trend in stored energy,

\[
P_{\mathrm{in}} \approx P_{\mathrm{ref}} + P_{\mathrm{LW}},
\qquad
P_{\mathrm{abs}} \approx P_{\mathrm{LW}}.
\]

The balance is approximate because actual planets can be warming or cooling. A nonzero TOA imbalance is precisely a net rate of energy storage or release.

## 7. Energy, free energy and exergy are not interchangeable

Energy is conserved. Exergy is the maximum useful work that can, in principle, be extracted as a system comes into equilibrium with a specified reference environment. It depends on both the system and the chosen environment [3].

A joule of high-temperature radiation is not thermodynamically equivalent to a joule of low-temperature heat. Stellar photons arrive from a source with a characteristic temperature near 5800 K, while the planet emits most of its thermal radiation at a much lower effective temperature near 255 K. This temperature and spectral contrast makes incoming stellar radiation a high-quality energy input relative to the planetary environment.

For ideal blackbody radiation from a source at temperature Ts relative to a blackbody reference environment at temperature T0, the classical Petela exergy factor is

\[
\psi_{\mathrm{P}}
=
1-\frac{4}{3}\frac{T_0}{T_s}
+\frac{1}{3}\left(\frac{T_0}{T_s}\right)^4.
\]

In that idealized formulation, the associated radiation exergy is \(B_{\mathrm{rad}}=\psi_{\mathrm{P}}E_{\mathrm{rad}}\) [3].

This expression is useful as a baseline, not as a universal formula for every radiation field. The reference environment must be stated; actual radiation has a spectrum and angular distribution; and published formulations differ in assumptions about radiation and the environment [3]. The first model should label the Petela calculation as an idealized blackbody estimate, not as a complete exergy model for an atmosphere–planet system.

Exergy destruction in an irreversible process is related to entropy generation through the Gouy–Stodola relation

\[
B_{\mathrm{destroyed}} = T_0 S_{\mathrm{gen}},
\]

for a specified reference-environment temperature T0 and the corresponding exergy accounting. This relation makes the distinction explicit: exergy is destroyed by irreversibility; energy is not destroyed.

## 8. Entropy balance for the planetary control volume

For an open control volume, the entropy balance is

\[
\frac{dS_{\mathrm{sys}}}{dt}
=
\dot S_{\mathrm{in}}
-
\dot S_{\mathrm{out}}
+
\dot S_{\mathrm{gen}},
\]

where:
- Ssys is entropy stored within the planetary control volume.
- Sin is the entropy transfer rate into the control volume.
- Sout is the entropy transfer rate out of it.
- Sgen is entropy generated internally by irreversible processes.

The second law requires

\[
\dot S_{\mathrm{gen}} \geq 0.
\]

At steady state, if entropy storage has no secular trend,

\[
\dot S_{\mathrm{gen}}
=
\dot S_{\mathrm{out}}-\dot S_{\mathrm{in}}.
\]

For a planet whose only boundary transfers are radiative, the incoming and outgoing terms include the entropy carried by incoming stellar radiation, reflected shortwave radiation and outgoing thermal radiation. If matter or other energy/work transfers cross the boundary, their entropy transfers must also be included.

**Do not calculate planetary entropy production by simply dividing net energy flux by a single temperature.** Incoming sunlight is not a thermal flux at the planet's temperature; outgoing radiation is spectrally distributed; and reflected sunlight's entropy depends strongly on its angular redistribution. Wu and Liu's review shows that radiation-entropy estimates can differ substantially with the method used and that the frequently used energy-flux/temperature approximation can underestimate Earth's radiation entropy flux by more than 30% [4].

## 9. Entropy flux of blackbody radiation

For a blackbody surface at temperature T, the hemispherical radiative energy flux is the Stefan–Boltzmann result

\[
F_E = \sigma T^4.
\]

The corresponding hemispherical entropy flux is

\[
F_S = \frac{4}{3}\sigma T^3.
\]

Thus, for ideal blackbody emission,

\[
\dot S_{\mathrm{rad}} = \frac{4}{3}\frac{P_{\mathrm{rad}}}{T}.
\]

The factor \(4/3\) is essential: the entropy flux of blackbody radiation is not simply energy flux divided by temperature [4].

This result applies to blackbody radiation. It should not be applied blindly to arbitrary greybody or non-blackbody radiation by multiplying by an emissivity. For real planetary radiation, spectral and angular distributions matter.

### 9.1 A spectral expression for general radiation

For a more complete treatment, represent the radiation field by its spectral radiance \(I_\nu(\Omega)\), as a function of frequency ν and direction Ω. The photon occupation number per mode can be written

\[
n_\nu(\Omega)=\frac{c^2 I_\nu(\Omega)}{2h\nu^3},
\]

where c is the speed of light, h is Planck's constant, and the factor of two accounts for the two photon polarizations.

The corresponding spectral entropy radiance is

\[
L_{S,\nu}(\Omega)
=
\frac{2 k_B \nu^2}{c^2}
\left[
(1+n_\nu)\ln(1+n_\nu)
-
n_\nu\ln n_\nu
\right],
\]

where kB is Boltzmann's constant.

The entropy flux through a surface is obtained by integrating this quantity over frequency and over the appropriate incoming or outgoing hemisphere, weighted by the direction cosine:

\[
F_S =
\int_0^\infty
\int_{\mathrm{hemisphere}}
L_{S,\nu}(\Omega)\,
|\cos\theta|\,
d\Omega\,d\nu.
\]

This is the level of description needed when comparing reflected solar radiation and outgoing thermal radiation in detail. It makes clear why total power and a single effective temperature are not enough to determine radiative entropy flux. See Wu and Liu for a review of the expressions and their applicability to Earth [4].

## 10. A deliberately simplified entropy calculation

A toy calculation can illustrate the large entropy difference between high-temperature incoming radiation and low-temperature outgoing radiation. It must not be mistaken for a full Earth entropy budget.

Assume:
1. The star emits ideal blackbody radiation at T★.
2. The absorbed fraction is spectrally neutral.
3. The planet returns the absorbed energy as ideal blackbody radiation at Te.
4. Reflected radiation preserves the incoming radiation entropy per unit energy — effectively an idealized reversible reflection assumption.
5. The planet is in steady energy balance, with no net entropy storage or non-radiative boundary transfer.

Under those assumptions, reflected radiation cancels from the net entropy balance, and the absorbed energy flux Fabs is re-emitted thermally. The simplified entropy generation per planetary area is

\[
\frac{\dot S_{\mathrm{gen}}}{A}
=
\frac{4}{3}F_{\mathrm{abs}}
\left(
\frac{1}{T_e}-\frac{1}{T_\star}
\right).
\]

Using \(F_{\mathrm{abs}}\approx 240\ \mathrm{W\,m^{-2}}\), \(T_e\approx255\ \mathrm{K}\), and \(T_\star\approx5800\ \mathrm{K}\), this idealized expression gives approximately

\[
\frac{\dot S_{\mathrm{gen}}}{A}
\approx 1.20\ \mathrm{W\,m^{-2}\,K^{-1}}.
\]

This is a pedagogical limiting calculation, not a recommended estimate for Earth. In particular, it assumes away the entropy change associated with the real angular redistribution of reflected sunlight and the complexity of Earth's non-blackbody outgoing radiation. Wu and Liu's more detailed analysis of Earth's radiative entropy flux obtains about 1.27–1.28 W m⁻² K⁻¹ for its stated albedo and emissivity assumptions using a Planck spectral expression [4]. The difference is a warning against turning the toy formula into a planetary constant.

## 11. Why reflection requires special care

The same reflected energy can be associated with different entropy fluxes depending on the angular distribution of the outgoing radiation. A specular reflection preserves directional structure differently from diffuse, approximately Lambertian reflection.

Wu and Liu identify this as a major source of differences among estimates of Earth's reflected shortwave entropy flux [4]. Therefore:
- Albedo determines reflected **energy fraction**, not reflected-radiation entropy by itself.
- A global albedo parameter cannot close the entropy budget.
- A model that changes surface or cloud reflectivity must also consider the angular and spectral consequences for radiation.
- Any claim that biological cover changes planetary entropy production through albedo must use an explicit radiative treatment, or state that it is only a sensitivity proxy.

## 12. What biological and chemical organization changes — and what it does not

Life does not create energy. It can alter the pathways, timing and location through which planetary energy is transformed.

Examples include:
- Photosynthesis temporarily storing part of absorbed radiant exergy in chemical free energy.
- Respiration and decomposition converting chemical free energy into heat and other products.
- Organisms modifying surface reflectance, roughness, evapotranspiration and atmospheric composition.
- Ecosystems changing water, carbon and nutrient cycling, which can alter radiative and transport processes.

These mechanisms can influence local dissipation, energy storage, planetary albedo and outgoing radiation. Their net effect on planetary entropy production is not determined merely by the presence or complexity of life. It must be calculated from a declared system boundary and measured physical properties.

At planetary steady state, chemical storage cannot grow without bound. Stored chemical free energy must eventually be used, recycled, buried, exported or otherwise included in the balance. Biological throughput is not itself a measurement of entropy production.

## 13. What this establishes — and what it does not

This first thermodynamic framework establishes a defensible starting point:

1. A star–planet configuration supplies a sustained radiative energy flow.
2. The incoming and outgoing radiation differ greatly in characteristic temperature and spectrum.
3. The planetary system transforms energy while maintaining a long-term energy balance, subject to transient storage and imbalance.
4. Irreversible transformations generate entropy, while radiation transports entropy across the planetary boundary.
5. The quantity and quality of energy available for work are different questions; exergy depends on a reference environment.

It does **not** establish:
- That dissipative structures must emerge.
- That life is an inevitable consequence of stellar irradiation.
- That increasing organizational complexity is thermodynamically required.
- That natural selection maximizes planetary entropy production.
- That agency or intelligence is a necessary endpoint of evolution.

Those remain separate hypotheses requiring separate mechanisms and evidence.

## 14. Minimum requirements for the first computational model

The first implementation should be a transparent global-mean accounting model, not an agent-based simulation.

**Inputs**
- Stellar effective temperature and radius, or directly measured stellar irradiance at the planet.
- Orbital distance or incident irradiance.
- Planetary radius.
- Bond albedo.
- Effective radiating temperature or a simple radiative model.
- An explicit reference environment for exergy.
- Optional storage and internal-source terms.

**Core calculations**
- Stellar luminosity and irradiance.
- Intercepted stellar power.
- Global-mean incoming flux.
- Reflected and absorbed power.
- Outgoing thermal power.
- Energy imbalance and implied storage rate.
- Idealized radiation exergy using a clearly stated reference model.
- Blackbody radiation entropy as a limiting case.
- Spectral radiation entropy only when spectral and angular data are available.

**Validation tests**
1. The geometric global-mean flux equals one quarter of the substellar irradiance for a spherical planet under the stated assumptions.
2. Energy balance closes to numerical tolerance when steady-state inputs are chosen.
3. Energy storage changes by exactly the imposed energy imbalance.
4. Entropy generation is non-negative when all entropy transfers and storage are accounted for.
5. The blackbody entropy-flux implementation reproduces \(4\sigma T^3/3\).
6. A result based only on energy flux and one temperature is clearly labelled as an approximation, not a general radiative entropy calculation.

Only after this accounting model is correct should spatial climate, chemistry, dissipative structures or biological mechanisms be added.

## 15. Open questions for the next research step

- Which planetary energy gradients are relevant to chemical organization, rather than merely to bulk heating?
- How do temperature, redox, pH, water activity, mineral surfaces and chemical disequilibria enter the available exergy budget?
- Which physical mechanisms couple a gradient to sustained reaction networks?
- How can the persistence of an organized structure be distinguished from a transient pattern?
- What does a meaningful system boundary look like when the question shifts from planetary radiative balance to a local prebiotic environment?

These questions bridge the global planetary budget to the local chemistry needed for Phase II. The global energy budget is necessary context, but it is not yet an origin-of-life mechanism.

---

## References

[1] NASA Earth Observatory. “Climate and Earth's Energy Budget.” https://science.nasa.gov/earth/earth-observatory/climate-and-earths-energy-budget/

[2] Trenberth, K. E., Fasullo, J. T., & Kiehl, J. (2009). “Earth's Global Energy Budget.” *Bulletin of the American Meteorological Society*, 90(3), 311–323. https://doi.org/10.1175/2008BAMS2634.1

[3] Rodríguez, E., Cardemil, J. M., Starke, A. R., & Escobar, R. (2022). “Modelling the Exergy of Solar Radiation: A Review.” *Energies*, 15(4), 1477. https://doi.org/10.3390/en15041477

[4] Wu, W., & Liu, Y. (2010). “Radiation entropy flux and entropy production of the Earth system.” *Reviews of Geophysics*, 48, RG4006. https://doi.org/10.1029/2008RG000275

[5] National Institute of Standards and Technology. “CODATA Value: Stefan–Boltzmann constant.” https://physics.nist.gov/cgi-bin/cuu/Value?sigma
