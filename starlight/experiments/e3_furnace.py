"""E3. The furnace. A heritable trait that raises entropy production and does nothing else.

A second band of light falls on the world. Only the furnace trait f absorbs it,
and it turns it straight into heat. The organism gains nothing.
Every population starts at f = 0.5, the middle of the range, so drift has no preferred direction.

Arms
  free     the furnace costs nothing to carry
  costly   the furnace costs 0.01 * f per step
"""
import sys
from common import BASE, replace, execute, STEPS, SEEDS

ARMS = {"free": 0.0, "costly": 0.01}

tasks = []
for arm, cf in ARMS.items():
    for s in SEEDS:
        cfg = replace(BASE, mutable=("a", "f"), a0=0.65, f0=0.5, furnace_band=True, c_furnace=cf)
        tasks.append((dict(arm=arm, c_furnace=cf), cfg, s, STEPS))

if __name__ == "__main__":
    execute("e3", tasks, smoke="--smoke" in sys.argv)
