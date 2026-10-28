#!/usr/bin/env python3
"""HW8: TSP solver 2 -- Improvement method (deterministic 2-opt).

The classic "improve a feasible tour" approach: take an existing tour
(here one built by the greedy algorithm) and repeatedly replace two
edges by two shorter edges that reconnect the tour in the other
direction:

        ... a - b ... c - d ...      (tour)
        ... a - c ... b - d ...      (2-opt move)

The move is the only way two edges of a tour can be exchanged while the
result stays a single closed tour (reversing the segment between b and
c).  We scan all pairs (i, j), apply the first strictly improving move,
and restart the scan; the process stops when a full scan finds nothing,
i.e. the tour is *2-optimal*.

Complexity: O(n^2) per scan, O(passes * n^2) overall (usually a handful
of passes).  Deterministic: same input always gives the same result.
"""

from tsp_core import apply_2opt, opt2_delta, tour_length


def two_opt_tsp(D, init_order, max_passes=1000):
    """Improve `init_order` with first-improvement 2-opt moves.

    Returns (order, length, history); history records the tour length
    after each full scan pass.
    """
    order = list(init_order)
    n = len(order)
    length = tour_length(order, D)
    history = [(0, length)]
    for _pass in range(1, max_passes + 1):
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue            # reversing the whole ring is the same tour
                delta = opt2_delta(D, order, i, j)
                if delta < -1e-12:
                    apply_2opt(order, i, j)
                    length += delta
                    improved = True
        history.append((_pass, length))
        if not improved:
            break
    return order, length, history
