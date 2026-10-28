"""Shared CLI plumbing for experiments."""
from __future__ import annotations

import argparse
import itertools
import os
import sys

from ..config import Config


def base_parser(desc: str) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("--seeds", type=int, default=30, help="number of seeds (confirmatory: 0..29)")
    ap.add_argument("--seed0", type=int, default=0, help="first seed (pilots use >=1000)")
    ap.add_argument("--steps", type=int, default=None, help="override Config.steps")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 0))
    ap.add_argument("--out", type=str, default="results", help="output directory")
    ap.add_argument("--smoke", action="store_true", help="tiny run to check the plumbing")
    return ap


def base_config(args) -> Config:
    kw = {}
    if args.steps:
        kw["steps"] = args.steps
    if args.smoke:
        kw.update(steps=300)
    return Config(**kw)


def seeds_of(args) -> list[int]:
    n = 3 if args.smoke else args.seeds
    return list(range(args.seed0, args.seed0 + n))


def factorial(factors):
    for vals in itertools.product((False, True), repeat=len(factors)):
        yield dict(zip(factors, vals))


def fmt(x, nd=3):
    try:
        return f"{x:.{nd}f}"
    except (TypeError, ValueError):
        return str(x)


def emit(lines: list[str], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    text = "\n".join(lines) + "\n"
    with open(path, "w") as f:
        f.write(text)
    sys.stdout.write(text)
