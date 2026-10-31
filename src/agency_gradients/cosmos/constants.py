"""Physical constants (SI) and derived quantities. All sources in docs/DESIGN.md (S11)."""
import math

G = 6.67430e-11
C = 2.99792458e8
HBAR = 1.054571817e-34
KB = 1.380649e-23
MSUN = 1.98847e30
YR = 3.15576e7
GYR = 1e9 * YR
MP = 1.67262192e-27
SIGMA_SB = 5.670374e-8
LSUN = 3.828e26
GLY_M = 9.4607e24            # metres per Gly

EJ = MSUN * C ** 2           # J per Msun c^2
K1 = EJ / KB                 # entropy per (Msun c^2) per kelvin, k_B units
S_BH_COEF = 4 * math.pi * G * MSUN ** 2 / (HBAR * C)   # ~1.05e77 k_B per Msun^2
NB_PER_MSUN = MSUN / MP

H0 = 67.4e3 / 3.0857e22      # 1/s
H0_YR = H0 * YR
OM, OL = 0.315, 0.685
OB = 0.0493
CHI_OBS_GLY = 46.4           # comoving radius of observable universe (Ord 2021)
T_CMB0 = 2.7255
S_CEH = 2.6e122              # cosmic event horizon entropy (Egan and Lineweaver 2010)
S_OBS_EL = 3.1e104
S_STELLAR_BH_EL = 5.9e97

T_DS = HBAR * H0 * math.sqrt(OL) / (2 * math.pi * KB)   # de Sitter temperature, ~2.2e-30 K
HAWKING_RATIO = 1.4847       # radiation entropy per unit BH entropy lost (Page 2013, arXiv:1301.4995)
# photon-only evaporation time: t = 5120 pi G^2 M^3 /(hbar c^4)
T_EVAP_MSUN_YR = 5120 * math.pi * G ** 2 * MSUN ** 3 / (HBAR * C ** 4) / YR
HAWKING_K = 1.0 / (3.0 * T_EVAP_MSUN_YR)   # dM/dt = -K/M^2 (Msun, yr)
THAWK_MSUN = HBAR * C ** 3 / (8 * math.pi * G * MSUN * KB)  # Hawking temperature of 1 Msun, ~6.2e-8 K
