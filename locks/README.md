# Locks (S15)

Does life open free-energy gradients that nothing else opens?

A flow reactor with locked gradients. A barrier dial sets how locked they are. Five arms: passive, a natural mineral, a self-sustaining fire with fixed keys, life with heritable keys, and a designer bound. Entropy production is measured from the free-energy books, never rewarded.

**Status:** spec, engine and gates. No preregistration and no results yet.

- [`SPEC.md`](SPEC.md): the question, definitions, hypotheses, falsifiers and decisions. Read this first.
- `locks/world.py`: the engine.
- `tests/test_gates.py`: gates G1 to G6. If any fails, nothing this engine says counts.
- `experiments/pilot_controls.py`: pilot of the controls only.

```bash
cd locks
python -m pytest -q
PYTHONPATH=. python experiments/pilot_controls.py results/pilot_controls.json
```
