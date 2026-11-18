#!/usr/bin/env python3
"""HW10: one-variable numerical integration (quadrature).

Three classical rules on a fixed grid:

  trapezoid        O(h^2), exact for lines
  Simpson          O(h^4), exact for cubics (needs an even n)
  Gauss-Legendre   exact for polynomials of degree <= 2k-1 with k nodes

The n-variable Riemann integrator lives in riemann.py; Monte Carlo in
monte_carlo.py.

AI disclosure: drafted with AI assistance (OpenCode / LLM); reviewed and
verified by the author. See README.md, "AI usage disclosure".
"""

import numpy as np


def trapezoid(f, a, b, n=1000):
    """Composite trapezoid rule with n subintervals of [a, b]."""
    n = int(n)
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")
    h = (b - a) / n
    total = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        total += f(a + i * h)
    return h * total


def simpson(f, a, b, n=1000):
    """Composite Simpson rule with n (even) subintervals of [a, b]."""
    n = int(n)
    if n < 2:
        raise ValueError(f"n must be at least 2, got {n}")
    if n % 2:
        raise ValueError(f"n must be even for composite Simpson, got {n}")
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n, 2):
        total += 4.0 * f(a + i * h)
    for i in range(2, n, 2):
        total += 2.0 * f(a + i * h)
    return total * h / 3.0


def gauss_legendre(f, a, b, order=16):
    """Gauss-Legendre rule with `order` nodes on [a, b]."""
    order = int(order)
    if order < 1:
        raise ValueError(f"order must be at least 1, got {order}")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    mid = 0.5 * (a + b)
    half = 0.5 * (b - a)
    total = 0.0
    for node, weight in zip(nodes, weights):
        total += float(weight) * f(mid + half * float(node))
    return half * total
