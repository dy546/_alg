#!/usr/bin/env python3
"""HW8: TSP solver 1 -- Greedy algorithm (nearest neighbour).

Construction heuristic: start at a city, always travel to the closest
city not yet visited, and finally return to the start.  Because the
first step is fixed by the chosen start city, we run the heuristic from
every possible start and keep the shortest of the n tours.

Complexity: O(n^3) naive, or O(n^2) with all-start restarts using the
precomputed distance matrix (each run is O(n^2), there are n runs).
"""

import numpy as np

from tsp_core import tour_length


def greedy_nearest(D, start):
    """One nearest-neighbour run starting at city `start`.

    Returns (order, length, history) where history records the partial
    open-path length after each city is added, plus the closed tour
    length at the end.
    """
    n = len(D)
    unvisited = set(range(n))
    unvisited.discard(start)
    order = [start]
    cur = start
    total = 0.0
    history = [(1, 0.0)]
    while unvisited:
        nxt = min(unvisited, key=lambda j: D[cur, j])
        unvisited.discard(nxt)
        total += D[cur, nxt]
        order.append(nxt)
        cur = nxt
        history.append((len(order), total))
    total += D[cur, start]
    history.append((n, total))
    return order, total, history


def greedy_tsp(D, seed=None, max_starts=64):
    """Nearest neighbour from every starting city, keep the best tour.

    For n > max_starts only a fixed-size random sample of start cities is
    tried, to keep the benchmark affordable.
    """
    n = len(D)
    best_order, best_len, best_hist = None, float('inf'), None
    if n <= max_starts:
        starts = range(n)
    else:
        starts = np.random.default_rng(seed).choice(n, size=max_starts,
                                                    replace=False)
    for s in starts:
        order, length, history = greedy_nearest(D, int(s))
        if length < best_len:
            best_order, best_len, best_hist = order, length, history
    return best_order, best_len, best_hist
