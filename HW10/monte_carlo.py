#!/usr/bin/env python3
"""HW10: Monte Carlo integration in one and n dimensions.

The estimator is the plain sample-mean rule: draw N uniform points in the
box, average f there, multiply by the box volume.  Its error is a random
variable with standard deviation sigma/sqrt(N), where sigma is the
standard deviation of f over the box -- independent of the dimension.
That is why Monte Carlo still works at n = 100, where a Riemann grid
would need 2**100 cells.

f may be written in either of two styles:

  point-wise   f(point) -> float,          point has shape (n,)
  batch-wise   f(points) -> array (k,),    points has shape (k, n)

Batch-wise functions are detected once and then evaluated chunk by
chunk (fast); point-wise functions are called once per sample.  For
n = 1 a point-wise f receives a plain float.

AI disclosure: drafted with AI assistance (OpenCode / LLM); reviewed and
verified by the author. See README.md, "AI usage disclosure".
"""

import math
from typing import NamedTuple

import numpy as np

from riemann import as_bounds


class MCResult(NamedTuple):
    """Outcome of one Monte Carlo integration."""
    estimate: float
    stderr: float
    n_samples: int
    dimension: int


def _accepts_batches(f, probe):
    """True if f maps a (k, n) array to a (k,) array."""
    try:
        values = np.asarray(f(probe), dtype=float)
    except Exception:
        return False
    return values.shape == (probe.shape[0],)


def mc_integral(f, low, high, n_samples=1_000_000, seed=2026, chunk=10_000):
    """Integrate f over the box [low, high] by Monte Carlo.

    Returns MCResult(estimate, stderr, n_samples, dimension), where
    stderr is the estimated standard deviation of the estimator
    (volume * sigma / sqrt(N), sigma estimated from the samples).
    """
    lows, highs = as_bounds(low, high)
    n = lows.size
    n_samples = int(n_samples)
    chunk = int(chunk)
    if n_samples < 2:
        raise ValueError(f"n_samples must be at least 2, got {n_samples}")
    if chunk < 1:
        raise ValueError(f"chunk must be at least 1, got {chunk}")

    width = highs - lows
    volume = float(np.prod(width))
    rng = np.random.default_rng(seed)

    # Deterministic probe: never consumes random numbers, so batch-wise
    # and point-wise functions see exactly the same sample stream.
    probe = np.repeat((lows + 0.5 * width)[None, :], 2, axis=0)
    batch = _accepts_batches(f, probe)

    total = 0.0
    total_sq = 0.0
    remaining = n_samples
    while remaining > 0:
        size = min(chunk, remaining)
        points = lows + rng.random((size, n)) * width
        if batch:
            values = np.asarray(f(points), dtype=float)
            if values.shape != (size,):
                raise ValueError(
                    f"batch-wise f returned shape {values.shape}, expected "
                    f"({size},)")
        elif n == 1:
            values = np.fromiter((f(row[0]) for row in points),
                                 dtype=float, count=size)
        else:
            values = np.fromiter((f(row) for row in points),
                                 dtype=float, count=size)
        total += float(values.sum())
        total_sq += float(np.dot(values, values))
        remaining -= size

    mean = total / n_samples
    variance = max(0.0, (total_sq - n_samples * mean * mean) / (n_samples - 1))
    return MCResult(volume * mean,
                    volume * math.sqrt(variance / n_samples),
                    n_samples, n)
