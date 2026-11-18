#!/usr/bin/env python3
"""HW10: numerical differentiation in one and n dimensions.

One-variable derivatives use forward / backward / central finite
differences plus Richardson extrapolation.  The n-variable gradient is
the same central difference applied coordinate by coordinate
(2n function evaluations for n coordinates, n+1 for the one-sided
variants).

AI disclosure: drafted with AI assistance (OpenCode / LLM); reviewed and
verified by the author. See README.md, "AI usage disclosure".
"""

import numpy as np


def derivative(f, x, h=1e-5, method="central"):
    """Estimate f'(x) with a finite difference of step h.

    method:
      'forward'  -- (f(x+h) - f(x)) / h          truncation error O(h)
      'backward' -- (f(x) - f(x-h)) / h          truncation error O(h)
      'central'  -- (f(x+h) - f(x-h)) / (2h)     truncation error O(h^2)

    Smaller h reduces the truncation error but amplifies floating-point
    noise: the total error is U-shaped in h (see the demo table).
    """
    if h <= 0:
        raise ValueError(f"h must be positive, got {h!r}")
    x = float(x)
    if method == "forward":
        return (f(x + h) - f(x)) / h
    if method == "backward":
        return (f(x) - f(x - h)) / h
    if method == "central":
        return (f(x + h) - f(x - h)) / (2.0 * h)
    raise ValueError(
        f"unknown method {method!r}; use 'forward', 'backward' or 'central'")


def richardson_derivative(f, x, h=1e-2):
    """Richardson extrapolation of the central difference: error O(h^4).

    The central difference has an error expansion in even powers of h, so
    combining D(h) and D(h/2) cancels the h^2 term:

        D_R(h) = (4 * D(h/2) - D(h)) / 3
    """
    if h <= 0:
        raise ValueError(f"h must be positive, got {h!r}")
    coarse = derivative(f, x, h, method="central")
    fine = derivative(f, x, h / 2.0, method="central")
    return (4.0 * fine - coarse) / 3.0


def gradient(f, x, h=1e-5, method="central"):
    """Gradient of f at the point x (a 1-D array), one partial at a time.

    Costs 2n evaluations with the central difference, n+1 with the
    forward or backward difference (the base value f(x) is reused).
    """
    x = np.asarray(x, dtype=float)
    if x.ndim != 1:
        raise ValueError(f"x must be a 1-D point, got shape {x.shape}")
    if x.size == 0:
        raise ValueError("x must have at least one coordinate")
    if h <= 0:
        raise ValueError(f"h must be positive, got {h!r}")

    n = x.size
    out = np.zeros(n)
    if method == "central":
        for i in range(n):
            step = np.zeros(n)
            step[i] = h
            out[i] = (f(x + step) - f(x - step)) / (2.0 * h)
    elif method in ("forward", "backward"):
        base = f(x)
        for i in range(n):
            step = np.zeros(n)
            step[i] = h
            if method == "forward":
                out[i] = (f(x + step) - base) / h
            else:
                out[i] = (base - f(x - step)) / h
    else:
        raise ValueError(
            f"unknown method {method!r}; use 'forward', 'backward' or 'central'")
    return out
