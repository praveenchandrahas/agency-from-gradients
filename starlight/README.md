# Starlight

A from-scratch test of one chain of reasoning.

1. Free energy flows from a star into space.
2. Structures that feed on that flow appear and persist. Life is one.
3. Such structures evolve to capture more of the flow.
4. The behaviour that captures more is what we call agency.
5. Why? Because more capture means more entropy, and the Universe favours that.

Links 1 and 2 are assumed. Links 3 and 4 are tested. Link 5 is tested against its rival:
that entropy production is a side effect of selection for persistence, and not the thing selected.

> **Since then.** Later experiments changed several of these links. Link 1 is wrong as written: most free energy comes from gravity and fusion, and starlight is an unlocked gradient. Link 5 was rejected as a cause. And the claim underneath link 2, that life drains energy nothing else can, failed when tested directly in S15. See [`docs/standing.md`](../docs/standing.md) for every link.

## The world in six lines

- A ring of 256 sites. Four patches of light fall on it.
- Light nobody absorbs escapes, undegraded. Absorbed light becomes heat.
- Organisms absorb light, pay costs, split at energy 2, die by starvation or by a blind hazard.
- Children copy the parent's traits, with small mutations.
- There is no fitness function. Nothing rewards capture, heat or entropy.
- The energy ledger closes at every step, to about 1e-12.

Traits: absorber size `a`, motility `m`, gradient sensing `g`, and a furnace `f` that only makes heat.

## Run it

```bash
pip install numpy matplotlib pytest
pytest -q                               # 11 tests, under a second

python experiments/e1_capture.py --smoke   # plumbing check, seconds
python experiments/e1_capture.py           # about 2.5 minutes on 2 cores
python experiments/e3_furnace.py           # about 2 minutes
python experiments/e2_behaviour.py         # about 15 minutes
python analysis/report.py                  # writes RESULTS.md and figures/
```

## Layout

```
starlight/world.py        the engine. One file, about 250 lines
tests/test_world.py       ledger, determinism, shading, movement, division
experiments/              e1, e2, e3: one script each, plus a shared runner
analysis/report.py        every number in RESULTS.md comes from here
PREREGISTRATION.md        predictions and falsifiers, frozen before the runs
RESULTS.md                the outcome, prediction by prediction
results/                  raw CSVs and RUN_INFO.txt (hashes of the frozen files)
figures/
```

## What it does not show

- **Nothing about Earth.** It is a toy.
- **Nothing about where copiers come from.** Copying is given.
- **Capture equals entropy here by bookkeeping.** The lifeless world is a perfect mirror. Real rock absorbs sunlight and makes heat without any help from life.
- **Sensing is a ready-made dial.** Evolution tunes it. It does not invent it.
- **All capture is private.** No organism builds anything that others can use. The Kardashev steps are collective. They are not in this model.
