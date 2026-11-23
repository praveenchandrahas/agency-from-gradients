"""Pre-run expectations for S15, from steady-state arithmetic only. No living world is simulated.

A growing population with a single key at distance d settles where each catalyst's gain pays
its upkeep plus its share of hazard losses. That fixes the fuel level F*, and F* fixes the
total entropy production. Natural minerals are a fixed number of random keys.
These are guesses written down in advance, not results.
"""
import math

import numpy as np

from locks import Config, g_fn

C = Config()
LN = lambda x: math.log(x)


def binom_cdf(n, d):
    return sum(math.comb(n, k) for k in range(d + 1)) / 2 ** n


def expected_dmin(n, n0):
    """Expected minimum Hamming distance of n0 random keys to a fixed lock."""
    return sum((1.0 - binom_cdf(n, d)) ** n0 for d in range(n))   # E[min] = sum over d of P(min > d)


def solve(r, B, g_star):
    """Steady fuel level F* where a catalyst with rate r gains exactly g_star. Returns (F*, N)."""
    dmu, fin, win, dil = C.dmu0[0], C.f_in[0], C.w_in, C.dil
    em = math.exp(-dmu)
    k_unc = C.k0 * math.exp(-B)

    def gain(F):
        W = fin + win - F
        return C.eta * r * (F - em * W) * (dmu + LN(F / W))

    lo, hi = (fin + win) * em / (1 + em) * (1 + 1e-9), fin
    if gain(hi) <= g_star:
        return None, 0.0                 # not viable even on untouched fuel
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if gain(mid) < g_star else (lo, mid)
    F = 0.5 * (lo + hi)
    W = fin + win - F
    J = dil * (fin - F)
    k = J / (F - em * W)
    return F, max(0.0, (k - k_unc) / r)


def sigma_at(F):
    W = C.f_in[0] + C.w_in - F
    g_in = g_fn(np.array([C.f_in[0]]), np.array([C.w_in]), np.array(C.dmu0))[0]
    return C.dil * (g_in - g_fn(np.array([F]), np.array([W]), np.array(C.dmu0))[0])


def fixed_F(k):
    em, fin, win, dil = math.exp(-C.dmu0[0]), C.f_in[0], C.w_in, C.dil
    # dil (fin - F) = k (F - em (fin + win - F))
    return (dil * fin + k * em * (fin + win)) / (dil + k * (1 + em))


def main():
    g_star = C.c_up + C.hazard * 0.75 * C.e_div      # upkeep plus hazard losses, per catalyst
    r = lambda d: C.k0 * math.exp(-(C.b_cat + C.lam * d)) / C.vol
    B = 16.0
    print(f"gain needed per catalyst: {g_star:.2f} kT per residence time")
    d_star = max(d for d in range(40) if solve(r(d), B, g_star)[0] is not None)
    print(f"viable on untouched fuel: d <= {d_star}")
    print(f"passive sigma at B=16: {sigma_at(fixed_F(C.k0 * math.exp(-B))):.1f}")
    for n in (24, 32):
        p = binom_cdf(n, d_star)
        dmin = expected_dmin(n, C.n0)
        print(f"\nn = {n}: P(random key viable) = {p:.4f}; expected viable keys in a library of {C.n0}: {C.n0 * p:.1f};"
              f" expected best distance {dmin:.1f}")
        FL, NL = solve(r(0), B, g_star)
        print(f"  life, near-perfect key (d=0): F* = {FL:.2f}, sigma = {sigma_at(FL):.0f}, catalysts = {NL:.0f}")
        for d in (math.floor(dmin), math.ceil(dmin)):
            F, N = solve(r(d), B, g_star)
            if F is None:
                print(f"  fire with best library key d={d}: not viable")
            else:
                print(f"  fire with best library key d={d}: F* = {F:.1f}, sigma = {sigma_at(F):.0f}, catalysts = {N:.0f}")
        Em = ((1 + math.exp(-C.lam)) / 2) ** n
        kM = C.k0 * math.exp(-B) + NL * C.k0 * math.exp(-C.b_cat) / C.vol * Em
        FM = fixed_F(kM)
        print(f"  mineral, {NL:.0f} random keys: spent {1 - FM / C.f_in[0]:.3f}, sigma = {sigma_at(FM):.0f}")
        kU = C.k0 * math.exp(-B) + NL * r(0)
        print(f"  designer, {NL:.0f} perfect keys: sigma = {sigma_at(fixed_F(kU)):.0f}")


if __name__ == "__main__":
    main()
