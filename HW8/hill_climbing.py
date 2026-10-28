#!/usr/bin/env python3
"""HW8: TSP solver 3 -- Hill climbing (with random restarts).

Classic greedy local search.  The neighbours of a tour are the tours
reachable by one 2-opt move (reverse a segment between two edges):

        ... a - b ... c - d ...      (tour)
        ... a - c ... b - d ...      (neighbour)

From the current tour we sample 2-opt moves uniformly at random and move
to the *first* one that strictly shortens the tour (first-improvement
ascent).  When no improvement has been seen for a long while the tour is
a 2-opt local optimum and the climb stops.

A single climb from one random start is usually a poor local optimum, so
we use random-restart hill climbing: run the climber many times from
random tours and keep the best local optimum found.  Unlike the
deterministic improvement method (which scans *all* moves systematically
from one good start), hill climbing makes *randomised greedy* steps --
same neighbourhood, different search strategy.

Complexity: O(stall) move attempts per climb, each O(1); O(R * stall)
for R restarts.  Memory: O(n).
"""

import numpy as np

from tsp_core import apply_2opt, opt2_delta, random_tour, tour_length


def hill_climb(D, init_order, seed=None, max_steps=None, stall=None):
    """First-improvement ascent over random 2-opt moves.

    Returns (order, length, history) with history = (step, length).
    """
    n = len(D)
    rng = np.random.default_rng(seed)
    order = list(init_order)
    length = tour_length(order, D)
    history = [(0, length)]
    if stall is None:
        stall = 4 * n * n
    if max_steps is None:
        max_steps = 40 * n * n
    rejections = 0
    for step in range(1, max_steps + 1):
        i = int(rng.integers(0, n - 2))
        j = int(rng.integers(i + 2, n))
        if i == 0 and j == n - 1:
            continue                       # reversing the whole ring is a no-op
        delta = opt2_delta(D, order, i, j)
        if delta < -1e-12:
            apply_2opt(order, i, j)
            length += delta
            rejections = 0
        else:
            rejections += 1
        history.append((step, length))
        if rejections >= stall:
            break
    return order, length, history


def hill_climb_restarts(D, n_restarts=30, seed=None):
    """Random-restart hill climbing.

    Returns (best_order, best_length, best_so_far, restart_lengths) where
    best_so_far = [(restart_index, best length so far)] for plotting and
    restart_lengths = length of every restart's local optimum.
    """
    n = len(D)
    rng = np.random.default_rng(seed)
    best_order, best_len = None, float('inf')
    restart_lengths = []
    best_so_far = []
    for r in range(1, n_restarts + 1):
        order, length, _history = hill_climb(
            D, random_tour(n, seed=int(rng.integers(0, 2 ** 31))),
            seed=int(rng.integers(0, 2 ** 31)))
        restart_lengths.append(length)
        if length < best_len:
            best_len, best_order = length, order
        best_so_far.append((r, best_len))
    return best_order, best_len, best_so_far, restart_lengths
