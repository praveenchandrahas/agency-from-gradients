# The chemistry line: catalysis before the replicator

!!! warning "Status: model demonstrations, as of 2026-11-23"
    Nothing here is preregistered. Every result is a model output under stated assumptions, not prebiotic chemistry.

This line began as a separate repository, `thermodynamic-emergence`. It was folded in here on 2026-11-23, with its history, as [`chemistry/`](https://github.com/praveenchandrahas/agency-from-gradients/tree/main/chemistry). It sits with [S14](s14.md): what happens before anything copies itself?

## What it built

| Model | What it shows | What it doesn't |
|---|---|---|
| **Star and planet ledger** | Energy balance closes for an Earth-like planet: about 238 W/m² in and out, effective temperature about 255 K | Climate, chemistry, life. It's bookkeeping. It's also the *catching* frame: see [catching against unlocking](../unlocking.md) |
| **One autocatalyst** (A + X ⇌ 2X + W, X ⇌ D) | Fixed reservoirs drive X about 90,000 times above its background level | It starts with a seed, and D feeds X back. Not emergence |
| **Two mutual catalysts, closed batch** | Catalysis speeds up conversion | A closed batch only reaches equilibrium sooner. The final entropy is the same. No steady state |
| **Two mutual catalysts, open reactor** | A driven steady state holds. Catalytic abundance is about 176 times the uncatalysed null | The null also holds a steady state. Catalysis isn't needed for steadiness |
| **Open reactor, damage and recovery** | After 99% catalyst removal, about 99.9% of abundance comes back | 1% of the catalyst survives, and every species, catalysts included, is fed continuously. Recovery is from a seed, not from nothing |

Full numbers: [`chemistry/results/README.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/chemistry/results/README.md).

## How it fits with S14

S14 asked whether a driven soup starts copying itself. It found no closed catalytic set was even possible in 0 of 200 random chemistries. Its mineral-catalysed structure persisted while driven and came back after being wiped.

The chemistry line adds a cleaner reactor and a recovery protocol. It agrees with S14 on the main point: driven chemistry can hold an organized state. It doesn't show that state copying itself, or arising without a seed.

## Lessons it shares with the rest of the repo

- **Report reaction and exchange entropy separately.** It does. That's the lesson S15 learned the hard way.
- **A closed batch can't test persistence.** Only a driven system can.
- **Match the state before a perturbation.** Its first recovery sweep was confounded: changing background rates also changed how much catalyst and food were present at the moment of damage. The matched sweep fixed that.

## Open

- Recovery with zero catalyst feed and nothing surviving.
- Stochastic, finite-molecule extinction.
- Anything that copies with heredity. That's S14's H14a and H14b, still unanswered in a model where a closed set is possible.
