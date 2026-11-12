"""S14 soup: thermodynamic consistency, ledgers and the emergence detector.

The detector is exercised here only on designed chemistries (arms P and M) and on hand-written
reaction lists, never on arm R's random chemistries (PREREGISTRATION_S14.md, the tuning rule).
"""
import numpy as np

from agency_gradients.experiments.s14_soup import emerged, ldb_identity_error, run_one
from agency_gradients.soup import Reactor, SoupParams, designed_chemistry, equilibrium_counts, random_chemistry
from agency_gradients.soup.chemistry import COPIER, COPIER_SEED
from agency_gradients.soup.detect import max_raf, potential_raf, realised_raf, sterilised_twin, twin_lag

SMALL = SoupParams(L=4, t_end=60.0, t_late=40.0)


def test_species_and_sites_count():
    c = random_chemistry(1000, SoupParams())
    assert c.n_species == 126 + 2 and c.n_sites == 516
    assert set(c.lens[c.cp_spec]) | set(c.lens[c.cc_spec]) <= {3, 4, 5, 6}     # food never catalyses


def test_chemistry_is_a_function_of_its_id():
    a, b, c = random_chemistry(1001, SMALL), random_chemistry(1001, SMALL), random_chemistry(1002, SMALL)
    assert a.eps_bond == b.eps_bond and np.array_equal(a.cc_rxn, b.cc_rxn)
    assert a.eps_bond != c.eps_bond
    n = a.without_catalysis()
    assert len(n.cp_rxn) == len(n.cc_rxn) == 0 and np.array_equal(n.g, a.g)


def test_local_detailed_balance_identity():
    # ln[a_forward(n) / a_backward(n')] == Phi(n) - Phi(n') for every channel, at every drive
    c = random_chemistry(1000, SMALL)
    for dmu in (0.0, 4.0, 12.0):
        assert ldb_identity_error(c, SMALL, dmu, seed=1, trials=4) < 1e-9


def test_equilibrium_solver_conserves_mass():
    c = random_chemistry(1003, SMALL)
    eq = equilibrium_counts(c, 800.0, 1200.0, SMALL.c0)
    assert abs((c.na * eq).sum() - 800.0) < 1e-6 and abs((c.nb * eq).sum() - 1200.0) < 1e-6


def _closed(chem, prm, dmu, seed):
    n0 = np.zeros(chem.n_species, np.int64)
    n0[chem.index("a")] = n0[chem.index("b")] = prm.n_mono
    f = int(round(prm.n_fuel * np.exp(-dmu) / (1 + np.exp(-dmu))))
    n0[chem.iF], n0[chem.iW] = f, prm.n_fuel - f
    return Reactor(chem, prm, dmu, seed, flow=False, n0=n0)


def test_closed_box_relaxes_to_boltzmann_and_stops_producing_entropy():
    prm = SoupParams(L=4, t_end=400.0, t_late=100.0)
    c = random_chemistry(1000, prm)                      # with catalysis: a catalyst must not move the equilibrium
    rx = _closed(c, prm, 0.0, 3).run()
    eq = equilibrium_counts(c, prm.n_mono, prm.n_mono, prm.c0)
    d = c.lens == 2
    assert abs(rx.mean_late_counts()[d].sum() / eq[d].sum() - 1.0) < 0.08
    sig = rx.series["sigma"][100:]
    assert abs(sig.mean() / (sig.std(ddof=1) / np.sqrt(len(sig)))) < 4.0
    assert rx.series["sigma"][:20].sum() > 0             # it did produce entropy on the way there
    led = rx.ledger_residuals()
    assert led["mass"] == 0 and led["fw_closed"] == 0 and led["phi_rel"] < 1e-9


def test_tau_leap_agrees_with_the_exact_method():
    prm = SoupParams(L=3, t_end=300.0, t_late=60.0)
    c = random_chemistry(1000, prm).without_catalysis()
    a = _closed(c, prm, 0.0, 1).run()
    b = _closed(c, prm, 0.0, 2).run_exact()
    d = c.lens == 2
    assert abs(a.mean_late_counts()[d].sum() / b.mean_late_counts()[d].sum() - 1.0) < 0.08


def test_driven_run_books_close_and_entropy_is_produced():
    rx = Reactor(designed_chemistry("M", SMALL), SMALL, 12.0, 4, flux_ep=True).run()
    led = rx.ledger_residuals()
    assert led["mass"] == 0 and led["fuel"] == 0 and led["phi_rel"] < 1e-9
    late = rx.late()
    assert late["sigma_rate"] > 0
    assert abs(late["sigma_flux_rate"] / late["sigma_rate"] - 1.0) < 0.05     # fluxes agree with the books
    assert 0 < late["capture"] < 1


def test_ledger_test_detects_a_leak():
    rx = Reactor(designed_chemistry("M", SMALL), SMALL, 12.0, 4, t_end=5.0).run()
    rx.n[rx.chem.index("a")] += 3
    assert rx.ledger_residuals()["mass"] != 0
    rx.n[rx.chem.index("a")] -= 3
    rx.n[rx.iF] += 1
    assert rx.ledger_residuals()["fuel"] != 0


def test_no_drive_no_structure():
    prm = SMALL
    c = designed_chemistry("P", prm)
    rx = Reactor(c, prm, 0.0, 5)
    rx.n[c.index(COPIER)] = COPIER_SEED                  # even a seeded copier dies without fuel
    rx.run()
    eq = equilibrium_counts(c, prm.n_mono, prm.n_mono, prm.c0)
    f_eq = (np.where(c.lens >= 3, c.lens, 0) * eq).sum() / (c.lens * eq).sum()
    assert rx.late()["poly_frac"] <= 2 * f_eq + 0.005


def test_max_raf_on_hand_written_sets():
    food = {0, 1}
    # 0 + 1 -> 2, catalysed by 2 (a copier): kept
    assert max_raf([((0, 1), (2,), (2,))], food) == [0]
    # catalysed by 5, which nothing makes: dropped
    assert max_raf([((0, 1), (2,), (5,))], food) == []
    # a reactant that cannot be built from food: dropped, and what depended on it goes too
    assert max_raf([((0, 9), (2,), (2,)), ((0, 2), (3,), (3,))], food) == []
    # two reactions that catalyse each other
    assert max_raf([((0, 1), (2,), (3,)), ((0, 2), (3,), (2,))], food) == [0, 1]


def test_detector_fires_on_the_copier_and_not_on_the_mineral():
    out = {}
    for kind in ("P", "M"):
        c = designed_chemistry(kind, SMALL)
        rx = Reactor(c, SMALL, 12.0, 6)
        if kind == "P":
            rx.n[c.index(COPIER)] = COPIER_SEED
        rx.run()
        tw = sterilised_twin(rx, 7)
        out[kind] = (realised_raf(rx)["raf"], twin_lag(rx, tw), rx.late()["poly_frac"])
    assert out["P"][0] and out["P"][1] >= 10            # closed, and stays dead when wiped
    assert not out["M"][0] and out["M"][1] < 10         # driven and dissipating, but not a copier
    assert out["P"][2] > 0.2 and out["M"][2] > 0.2      # both build structure
    assert potential_raf(designed_chemistry("P", SMALL))["pot_raf"]
    assert not potential_raf(designed_chemistry("M", SMALL))["pot_raf"]


def test_run_one_rows_and_emergence_rule():
    prm = SoupParams(L=4, t_end=60.0, t_late=40.0)
    p = run_one(dict(arm="P", chem=1000, dmu=12.0, prm=prm))
    m = run_one(dict(arm="M", chem=1000, dmu=12.0, prm=prm))
    assert emerged(p) and not emerged(m)
    assert p["led_mass"] == 0 and p["led_fuel"] == 0
    assert p["c_intact_lag"] > p["c_twin_lag"]
    n = run_one(dict(arm="N", chem=1000, dmu=12.0, prm=prm))
    assert not emerged(n) and n["raf_main"] == 0
