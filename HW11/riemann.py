#!/usr/bin/env python3
"""HW10: n-variable integration with Riemann sums.

`integral(f, low, high)` integrates f over the box [low, high], where
n = len(low) = len(high).  Every axis is split into `cells` equal cells,
so one call costs exactly cells**n evaluations of f.

That cost is the point of the exercise: a grid is cheap in 1-D and
hopeless in 100-D.  The default cells="auto" therefore picks the largest
grid that fits the evaluation budget, which shrinks to one cell per axis
at n = 100 -- the one-cell midpoint rule.  Monte Carlo (monte_carlo.py)
is the method that still works there.

AI disclosure: drafted with AI assistance (OpenCode / LLM); reviewed and
verified by the author. See README.md, "AI usage disclosure".
"""

import itertools

import numpy as np


def as_bounds(low, high):
    """Normalise integration bounds to two equal-length 1-D float arrays."""
    lows = np.atleast_1d(np.asarray(low, dtype=float))
    highs = np.atleast_1d(np.asarray(high, dtype=float))
    if lows.ndim != 1 or highs.ndim != 1:
        raise ValueError("low and high must be scalars or 1-D sequences")
    if lows.size != highs.size:
        raise ValueError(
            f"low and high must have the same length, got {lows.size} and "
            f"{highs.size}")
    if lows.size == 0:
        raise ValueError("low and high must have at least one entry")
    if not (np.all(np.isfinite(lows)) and np.all(np.isfinite(highs))):
        raise ValueError("low and high must be finite")
    return lows, highs


def choose_cells(n, budget=100_000, max_cells=1000):
    """Largest m <= max_cells with m**n <= budget (never below 1)."""
    n = int(n)
    budget = int(budget)
    max_cells = int(max_cells)
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")
    if budget < 1:
        raise ValueError(f"budget must be at least 1, got {budget}")
    if max_cells < 1:
        raise ValueError(f"max_cells must be at least 1, got {max_cells}")
    best = 1
    for m in range(1, max_cells + 1):
        if m ** n <= budget:
            best = m
        else:
            break
    return best


def integral(f, low, high, cells="auto", rule="mid", budget=100_000,
             max_cells=1000, max_evals=10_000_000):
    """Riemann sum of f over the box [low, high] (n = len(low)).

    cells : "auto" (largest m with m**n <= budget) or a positive integer.
    rule  : 'left', 'mid' (default) or 'right' evaluation point per cell.
    low, high : scalars (n = 1) or equal-length 1-D sequences.

    Cost is cells**n evaluations; a grid above max_evals raises
    ValueError instead of running for hours.  In one dimension f is
    called with a float, in n dimensions with a length-n array.
    """
    lows, highs = as_bounds(low, high)
    n = lows.size

    if rule not in ("left", "mid", "right"):
        raise ValueError(f"unknown rule {rule!r}; use 'left', 'mid' or 'right'")
    if isinstance(cells, str):
        if cells != "auto":
            raise ValueError(
                f"cells must be 'auto' or a positive integer, got {cells!r}")
        m = choose_cells(n, budget=budget, max_cells=max_cells)
    else:
        m = int(cells)
        if m < 1:
            raise ValueError(f"cells must be positive, got {cells!r}")

    evaluations = m ** n
    if evaluations > max_evals:
        raise ValueError(
            f"this Riemann grid needs {m}**{n} = {evaluations:.3e} "
            f"evaluations, above max_evals = {max_evals:.1e}; pass a smaller "
            f"cells value or use monte_carlo.mc_integral")

    offset = {"left": 0.0, "mid": 0.5, "right": 1.0}[rule]
    step = (highs - lows) / m
    volume = float(np.prod(step))
    axes = [lows[i] + (np.arange(m) + offset) * step[i] for i in range(n)]

    total = 0.0
    for index in itertools.product(range(m), repeat=n):
        point = np.array([axes[i][index[i]] for i in range(n)])
        total += float(f(point[0])) if n == 1 else float(f(point))
    return volume * total
