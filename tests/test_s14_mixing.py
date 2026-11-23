"""The S14 mixing re-check must not touch the dynamics, and its mixing book must behave."""
from dataclasses import replace

import numpy as np

from agency_gradients.experiments.s14_mixing_recheck import MixingReactor
from agency_gradients.experiments.s14_soup import PRM
from agency_gradients.soup.chemistry import designed_chemistry
from agency_gradients.soup.reactor import Reactor

SHORT = replace(PRM, t_end=3.0, t_late=1.0)


def test_mixing_book_leaves_the_dynamics_unchanged():
    chem = designed_chemistry("M", SHORT)
    a = Reactor(chem, SHORT, 12.0, np.random.SeedSequence([14, 99]))
    b = MixingReactor(chem, SHORT, 12.0, np.random.SeedSequence([14, 99]))
    a.run(); b.run()
    assert np.array_equal(a.n, b.n)
    assert np.array_equal(a.series["sigma"], b.series["sigma"])


def test_no_mixing_when_the_reactor_matches_its_feed():
    chem = designed_chemistry("M", SHORT)
    rx = MixingReactor(chem, SHORT, 12.0, np.random.SeedSequence([14, 98]))
    assert rx.mix_rate(np.rint(rx.n_in).astype(np.int64)) == 0.0


def test_mixing_is_never_negative():
    chem = designed_chemistry("P", SHORT)
    rx = MixingReactor(chem, SHORT, 12.0, np.random.SeedSequence([14, 97]))
    rx.run()
    assert (rx.mix >= 0).all() and rx.mix.sum() > 0
