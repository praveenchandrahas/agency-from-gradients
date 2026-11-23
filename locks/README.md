# Locks (S15)

Does life open free-energy gradients that nothing else opens?

A flow reactor with locked gradients. A barrier dial sets how locked they are. Five arms: passive, a natural mineral, a self-sustaining fire with fixed keys, life with heritable keys, and a designer bound. Entropy production is measured from the free-energy books, never rewarded.

**Status:** run. Preregistered in [`PREREGISTRATION.md`](PREREGISTRATION.md), frozen 2026-11-23; results in [`RESULTS.md`](RESULTS.md). In short: life beat everything at the cold end, but a fire and a large mineral bed opened the lock too. "Nothing else does" fails here. Only life improved its key.

- [`SPEC.md`](SPEC.md): the question, definitions, hypotheses, falsifiers and decisions. Read this first.
- `locks/world.py`: the engine.
- `tests/test_gates.py`: gates G1 to G6. If any fails, nothing this engine says counts.
- `experiments/pilot_controls.py`: pilot of the controls only.
- `experiments/s15.py`: the confirmatory runner. `analysis/report.py`: the frozen analysis. `analysis/expectations.py`: pre-run arithmetic.

```bash
cd locks
python -m pytest -q
PYTHONPATH=. python experiments/pilot_controls.py results/pilot_controls.json
```
