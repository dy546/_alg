#!/usr/bin/env python3
"""HW8: TSP solver 5 -- Gradient descent (on a continuous relaxation).

A tour is a permutation, a purely discrete object, so the tour length
has no gradient in the usual sense.  Gradient descent is applied to a
*continuous relaxation* instead:

  * P[i, j] in [0, 1] = "mass" assigned to the claim that position i of
    the tour is occupied by city j.  A hard tour is the special case
    where P is a permutation matrix (one 1 per row and column).

  * The tour length becomes the smooth quadratic form

        L(P) = sum_i  P[i, :] . (P_{i+1} @ D)

    i.e. each position i is connected to the next position i+1 through
    the distance matrix D (cyclically).

  * Rows and columns of P are kept near permutation-like by a quadratic
    penalty g(P) = sum (row sum - 1)^2 + sum (col sum - 1)^2, weighted
    by a multiplier mu that is ramped up during a pass (penalty method).

Projected gradient descent (with momentum, P clipped back to [0, 1])
minimizes  F(P) = L(P) + mu * g(P):

        P <- clip( P - lr * (grad L + mu * grad g) )

  * While P descends, it is regularly rounded back to the nearest
    permutation (greedy: repeatedly pick the largest unused entry).
    Rounding is cheap, so it is done along the whole trajectory; any
    rounded tour that beats the best tour so far is remembered.

  * After each pass (a fixed number of GD steps) P is re-seeded from
    the best rounded tour found so far, slightly smoothed, and the next
    pass starts from there (iterative rounding).  The first pass is
    seeded from a tour built by the greedy algorithm.

The method is honest gradient descent on a smooth surrogate of the TSP:
each pass descends the relaxation, and rounding maps the soft solution
back to the discrete space.  It demonstrates how a continuous optimizer
can be bent to a discrete problem -- and where its limits are: it is
more expensive and less competitive than the dedicated local searches.

Complexity: O(passes * steps * n^3) for the matrix products and
O(passes * steps / round_every * n^3) for the roundings.
"""

import numpy as np

from tsp_core import tour_length


def _round_to_tour(P):
    """Greedy rounding of a soft assignment matrix to a permutation.

    Repeatedly pick the largest unused entry (position, city); the inner
    argmax is vectorised, O(n^3) worst case.
    """
    n = len(P)
    Q = P.copy()
    rows_used = np.zeros(n, dtype=bool)
    cols_used = np.zeros(n, dtype=bool)
    order = np.empty(n, dtype=int)
    for _ in range(n):
        tmp = Q.copy()
        tmp[rows_used, :] = -1.0
        tmp[:, cols_used] = -1.0
        idx = int(np.argmax(tmp))
        i, j = divmod(idx, n)
        order[i] = j
        rows_used[i] = True
        cols_used[j] = True
    return order.tolist()


def _loss_and_grad(P, D):
    """Smooth tour length L(P) and its gradient.

    L(P) = sum_i P[i, :] . (P_{i+1} @ D)   (rows are consecutive stops)
    grad L[a, b] = (P_{a+1} @ D)[b] + (P_{a-1} @ D)[b]
    """
    Q = P @ D
    L = float(np.sum(P * np.roll(Q, -1, axis=0)))
    grad = np.roll(Q, -1, axis=0) + np.roll(Q, 1, axis=0)
    return L, grad


def gradient_descent_tsp(cities, D, init_order, passes=None,
                         steps_per_pass=None, lr=1e-4, mu_max=60.0,
                         momentum=0.9, smoothing=0.10, seed=None,
                         round_every=None):
    """Projected gradient descent on the soft-assignment relaxation.

    Seeded from the permutation matrix of `init_order` (built by the
    greedy algorithm); later passes are re-seeded from the best rounded
    tour found so far.  Returns (best_order, best_length, history);
    history = [(cumulative steps, best rounded tour length so far)].
    """
    n = len(cities)
    if passes is None:
        passes = 10 if n <= 40 else 6
    if steps_per_pass is None:
        steps_per_pass = 1000 if n <= 40 else 800
    if round_every is None:
        round_every = 25 if n <= 40 else 50

    best_order = list(init_order)
    best_len = tour_length(init_order, D)
    history = [(0, best_len)]

    for p in range(passes):
        P = np.zeros((n, n))
        for pos, city in enumerate(best_order):
            P[pos, city] = 1.0
        P = (1.0 - smoothing) * P + smoothing / n
        velocity = np.zeros_like(P)
        mu_ramp = max(1, int(steps_per_pass * 0.6))

        for t in range(1, steps_per_pass + 1):
            mu = mu_max * min(1.0, t / mu_ramp)
            _L, grad = _loss_and_grad(P, D)
            row_dev = P.sum(axis=1, keepdims=True) - 1.0
            col_dev = P.sum(axis=0, keepdims=True) - 1.0
            grad = grad + mu * 2.0 * (row_dev + col_dev)
            velocity = momentum * velocity + grad
            P = np.clip(P - lr * velocity, 0.0, 1.0)

            if t % round_every == 0 or t == steps_per_pass:
                order = _round_to_tour(P)
                length = tour_length(order, D)
                if length < best_len:
                    best_len = length
                    best_order = order
                history.append((p * steps_per_pass + t, best_len))

    return best_order, best_len, history
