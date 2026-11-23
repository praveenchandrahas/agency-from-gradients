# Locks (S15): testing the claim underneath everything

!!! warning "Status: preregistered and run. The answer: not in this model"
    This page explains S15 in plain language. The frozen design is in [`locks/PREREGISTRATION.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/locks/PREREGISTRATION.md). The full reasoning is in [`locks/SPEC.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/locks/SPEC.md). The outcome is on [the S15 results page](results/s15.md). In short: life beat everything at the cold end, but a fire and a large enough mineral bed opened the lock too. "Nothing else does" fails here. Only life improved its key.

## The claim underneath

Everything in this repo leans on one idea.

Life does not just use energy. It makes the universe run downhill faster than anything passive could. A rock warms in the sun. Life does more than that.

Put that way, it is too big to test. So I asked a sharper question first.

Is it even true?

## The broad version is already in trouble

Stars and black holes are not passive. They persist only while energy flows through them. And they produce far more entropy than any biosphere ever will.

S11 found the same thing from the other side. Asked to raise the entropy of a lifeless universe, the best strategy was a black-hole engineer. Not life.

So "life beats everything" is false at cosmic scale.

Where could it still be true?

In the places the big engines leave behind. Cold places. Places where the energy is there, but locked.

Wood sits in oxygen for centuries. It could burn. It doesn't. Hydrogen and carbon dioxide can sit side by side for ages. Microbes eat that gap for a living.

That gives the claim S15 tests:

> **In cold, locked gradients, where passive structures and non-living dissipative ones stall, life opens the lock. Nothing else does.**

## Why the earlier experiments did not test it

Look back, and something is missing every time.

- **Starlight** let unused light escape untouched. Its lifeless world was a mirror. So life beat a mirror. A dark rock would have turned that light into heat too.
- **Planet** pitted agents against agents. Nothing passive was in the race.
- **S11** left life out by design.
- **S14** had a copier and a fixed "mineral" burn the same fuel about equally. But I picked the mineral's strength by hand. So that comparison meant nothing.

Touched, yes. Tested, no.

## Why not just use sunlight?

Sunlight is an *unlocked* gradient. Any dark surface absorbs it. No key needed.

So a sunlight test would be rigged against life, for reasons that have nothing to do with life.

Sunlight becomes one end of a dial instead.

## The dial

Here is the world.

A tank. Fuel flows in. Fuel flows out. Inside, the fuel can turn into waste and release free energy. But only through a lock.

The **barrier** sets how hard the lock is. At zero, the fuel falls apart on its own. That is the sunlight case. Turn the barrier up, and the fuel just sits there.

Catalysts carry **keys**: strings of bits. The closer a key is to the lock's own pattern, the faster it opens the lock. A catalyst can never move the end point, only the speed. That is checked, not assumed.

## Five worlds, one change at a time

| | What lives in the tank | What it adds |
|---|---|---|
| **N** | Nothing | The passive world. The baseline |
| **M** | Fixed catalysts with random keys | A natural mineral |
| **D** | Catalysts that grow on the energy they release. Keys copied exactly | A fire. Self-sustaining, but it cannot invent |
| **L** | The same, but keys are copied with small errors | Life. Heredity with variation |
| **U** | Perfect keys, placed by hand | A designer. The best possible, not a competitor |

The fire and life differ in one thing only: whether copying can make a new key. They start from the same library of keys.

The mineral and the designer get exactly as many catalysts as life ends up with. So the comparison is about keys, not about numbers.

Nothing is rewarded. Nobody is told about entropy. Catalysts that pay their bills persist. The rest die.

## A mistake the pilot caught

Before running anything with life in it, I ran the passive and designer worlds across the dial.

Something looked wrong.

The designer with 500 perfect keys spent 98% of the fuel. The designer with 100 spent 91%. Yet the first one scored *lower* on entropy.

Why?

Spend the fuel fast, and the tank fills with waste. Each reaction then releases less. The entropy did not vanish. It moved. Fresh fuel pouring into a spent tank mixes, and mixing makes entropy too.

I had been counting reactions only. So had S14.

Count both, and everything lines up: more fuel spent, more entropy. Physics says the total is the right number. That is what S15 reports. Reactions alone are reported next to it.

## What I expected, before the run

I wrote this down before any life world ran. It comes from arithmetic, not simulation.

A key is good enough to live on cold fuel if it is within about 10 bits of the lock.

- **With 24-bit keys**, a random library of 100 already holds about 27 such keys. So I expected the *fire* to open the lock too. It makes up for a weaker key with more catalysts. Life should still do better, by 10 to 20%. But not alone.
- **With 32-bit keys**, only about 2 or 3 library keys are viable, and barely. I expected the fire to stall. Life wins only if it can climb from that foothold before it starves.
- **The mineral** should stall either way.

If that holds, the honest reading is uncomfortable. Whether "nothing else does" is true depends on how rare a working key is among the structures already lying around. That is a property of the chemistry, not of life. And in this model, I chose it.

## The tests

| | Question | Passes if |
|---|---|---|
| **H1** | Does any structure beat the passive world at the coldest barrier? | Fire and life both beat N |
| **H2a** | Does life beat the mineral and the fire there? | Both differences are above zero |
| **H2b** | Does life's lead grow as the lock gets harder? | The slope over the barrier is above zero |
| **H2c** | With no lock, does life add nothing? | Every world is within 2% of N at zero barrier. If not, the model is broken |
| **H2d** | Does life stay below the designer? | Always. A check |
| **H2e** | Does everything else stall? | Fire and mineral reach under 10% of the designer at the coldest barrier |

H2e is the "nothing else does" half. H2a cannot test it: a fire at 90% and life at 99% would pass H2a.

## What this cannot show

- That real life does this. These are toy locks.
- Anything about stars, black holes or gravity. They are left out by scale, not by argument.
- Where life comes from. Copying is given.
- Anything about agency. This tests the ground agency would stand on.

## Read more

- [`locks/SPEC.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/locks/SPEC.md): definitions, the full argument, and what is true by construction.
- [`locks/PREREGISTRATION.md`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/locks/PREREGISTRATION.md): the frozen numbers and decision rules.
- [`locks/locks/world.py`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/locks/locks/world.py): the engine. [`locks/tests/test_gates.py`](https://github.com/praveenchandrahas/agency-from-gradients/blob/main/locks/tests/test_gates.py): the gates it must pass.
