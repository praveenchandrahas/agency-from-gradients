"""E1. Static light. Only absorber size evolves. Does selection by persistence raise capture?

Arms
  evolved   a mutable, started far too small (0.08) and far too big (2.0)
  fixed     a frozen at each value on a grid: the capture curve the world allows
"""
import sys
from common import BASE, replace, execute, STEPS, STEPS_FIXED, SEEDS

A_GRID = (0.08, 0.2, 0.35, 0.5, 0.65, 0.8, 1.0, 1.3, 2.0)
STARTS = (0.08, 2.0)

tasks = []
for a0 in STARTS:
    for s in SEEDS:
        tasks.append((dict(arm="evolved", a0=a0), replace(BASE, mutable=("a",), a0=a0), s, STEPS))
for a0 in A_GRID:
    for s in range(10):
        tasks.append((dict(arm="fixed", a0=a0), replace(BASE, mutable=(), a0=a0), s, STEPS_FIXED))

if __name__ == "__main__":
    execute("e1", tasks, smoke="--smoke" in sys.argv)
