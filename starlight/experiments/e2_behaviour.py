"""E2. The light moves. Do moving and sensing evolve, and only when the world demands them?

The patches speed up from rest over the first half of the run, then hold.
Every population starts with no behaviour at all (m = g = 0).

Arms
  a      only absorber size can mutate. No behaviour is possible.
  am     absorber and motility can mutate. Moving is possible, sensing is not.
  amg    absorber, motility and sensing can all mutate.
"""
import sys
from common import BASE, replace, execute, STEPS, SEEDS

SPEEDS = (0.0, 0.1, 0.2, 0.3, 0.5, 0.8)
ARMS = {"a": ("a",), "am": ("a", "m"), "amg": ("a", "m", "g")}

tasks = []
for v in SPEEDS:
    for arm, mutable in ARMS.items():
        for s in SEEDS:
            cfg = replace(BASE, mutable=mutable, a0=0.65, speed=v, ramp_steps=STEPS // 2)
            tasks.append((dict(arm=arm, v=v), cfg, s, STEPS))

if __name__ == "__main__":
    execute("e2", tasks, smoke="--smoke" in sys.argv)
