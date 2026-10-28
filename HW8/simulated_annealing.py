#!/usr/bin/env python3
"""HW8: TSP solver 4 -- Simulated annealing.

Like hill climbing (same 2-opt neighbourhood), but a move that *worsens*
the tour is still accepted with the Metropolis probability

        P(accept) = exp(-delta / T)

where T is a temperature that cools down geometrically.  A high T lets
the search escape local optima and wander over the landscape; as T -> 0
the search freezes into the deepest basin found.  The best tour ever
seen is remembered and returned, so the result never worsens.

Parameters:
  T0      -- initial temperature, set by probing random 2-opt moves so
             that a typical worsening move is initially accepted with
             reasonable probability
  T_end   -- final temperature (T0 * 1e-4)
  alpha   -- cooling factor per step, chosen so T goes from T0 to T_end
             in exactly `iters` steps
  iters   -- number of attempted moves (120 * n^2 by default, capped)

Complexity: O(iters) -- each move attempt costs O(1) via opt2_delta.
"""

import math

import numpy as np

from tsp_core import apply_2opt, opt2_delta, tour_length


def simulated_annealing(D, init_order, seed=None, iters=None,
                        T0=None, T_end=None):
    """Metropolis search with geometric cooling over random 2-opt moves.

    Returns (best_order, best_length, history); history samples the
    current tour length (the wandering curve) plus the final best.
    """
    n = len(D)
    rng = np.random.default_rng(seed)
    if iters is None:
        iters = min(400_000, 120 * n * n)
    order = list(init_order)
    length = tour_length(order, D)
    best_order, best_len = order[:], length

    if T0 is None:
        probe = []
        for _ in range(200):
            i = int(rng.integers(0, n - 2))
            j = int(rng.integers(i + 2, n))
            if not (i == 0 and j == n - 1):
                probe.append(abs(opt2_delta(D, order, i, j)))
        T0 = max(sum(probe) / len(probe), 1e-9) * 1.5
    if T_end is None:
        T_end = T0 * 1e-4
    alpha = (T_end / T0) ** (1.0 / iters)

    T = T0
    record_every = max(1, iters // 500)
    history = [(0, length)]
    for step in range(1, iters + 1):
        i = int(rng.integers(0, n - 2))
        j = int(rng.integers(i + 2, n))
        if i == 0 and j == n - 1:
            continue
        delta = opt2_delta(D, order, i, j)
        if delta < 0.0 or rng.random() < math.exp(-delta / T):
            apply_2opt(order, i, j)
            length += delta
            if length < best_len:
                best_len = length
                best_order = order[:]
        T *= alpha
        if step % record_every == 0:
            history.append((step, length))
    history.append((iters, best_len))
    return best_order, best_len, history
