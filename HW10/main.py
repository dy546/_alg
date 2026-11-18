#!/usr/bin/env python3
"""HW10: numerical differentiation and integration -- demo driver.

Collects and prints six reports:

  1. single-variable differentiation (forward / central / Richardson)
  2. single-variable integration (trapezoid / Simpson / Gauss / Monte Carlo)
  3. n-variable gradient (finite differences)
  4. n-variable Riemann integral, n = 1, 2, 5, 100
  5. n-variable Monte Carlo integral, same n
  6. why the 100-dimensional Riemann grid collapses

Usage:
  python3 main.py                    # full report, N = 1,000,000
  python3 main.py --quick            # same report with N = 100,000
  python3 main.py --samples 5000000  # more Monte Carlo samples
  python3 main.py --seed 7           # different random stream
  python3 main.py --cells 20         # fixed Riemann grid instead of "auto"
  python3 main.py --test             # run the correctness test suite

AI disclosure: drafted with AI assistance (OpenCode / LLM); reviewed and
verified by the author. See README.md, "AI usage disclosure".
"""

import argparse
import math
import time

import numpy as np

from differentiate import derivative, gradient, richardson_derivative
from monte_carlo import mc_integral
from quadrature import gauss_legendre, simpson, trapezoid
from riemann import choose_cells, integral

EXACT_SWEEP = math.cos(1.0)


def sum_squares(point):
    """f(x) = x_1^2 + ... + x_n^2 for a single point."""
    return float(np.sum(np.asarray(point, dtype=float) ** 2))


def sum_squares_batch(points):
    """Batch-aware version of sum_squares: (k, n) -> (k,)."""
    return np.sum(points * points, axis=-1)


# ----------------------------------------------------------------------
# Collecting the numbers
# ----------------------------------------------------------------------

def collect_diff1d(h_values=(1.0, 0.5, 0.25, 0.1, 0.01, 1e-3, 1e-5, 1e-7)):
    """Error of the three 1-D rules on sin at x = 1, as a function of h."""
    sweep = []
    for h in h_values:
        sweep.append({
            "h": h,
            "forward": derivative(math.sin, 1.0, h, "forward"),
            "central": derivative(math.sin, 1.0, h, "central"),
            "richardson": richardson_derivative(math.sin, 1.0, h),
        })
    examples = []
    for label, func, point, exact in (
            ("x^2", lambda x: x * x, 0.7, 1.4),
            ("x^3", lambda x: x ** 3, 2.0, 12.0),
            ("sin(x)", math.sin, 1.0, math.cos(1.0)),
            ("exp(x)", math.exp, 0.5, math.exp(0.5))):
        examples.append({
            "label": label,
            "x": point,
            "exact": exact,
            "forward": derivative(func, point, 1e-5, "forward"),
            "central": derivative(func, point, 1e-5, "central"),
            "richardson": richardson_derivative(func, point, 1e-5),
        })
    return {"exact": EXACT_SWEEP, "sweep": sweep, "examples": examples}


def collect_quad1d(samples=1_000_000, seed=2026):
    """Two 1-D integration reports: an exact polynomial and a smooth wave."""
    square = lambda x: x * x
    exact_rows = []
    for n in (10, 100):
        exact_rows.append({"method": "trapezoid", "param": f"n={n}",
                           "estimate": trapezoid(square, 0.0, 1.0, n)})
    for n in (10, 100):
        exact_rows.append({"method": "simpson", "param": f"n={n}",
                           "estimate": simpson(square, 0.0, 1.0, n)})
    for order in (4, 16):
        exact_rows.append({"method": "gauss-legendre", "param": f"order={order}",
                           "estimate": gauss_legendre(square, 0.0, 1.0, order)})
    mc = mc_integral(square, 0.0, 1.0, n_samples=samples, seed=seed)
    exact_rows.append({"method": "monte carlo", "param": f"N={samples:,}",
                       "estimate": mc.estimate})

    sin_rows = []
    for name, rule in (("trapezoid", trapezoid), ("simpson", simpson)):
        previous = None
        for n in (100, 200, 400):
            estimate = rule(math.sin, 0.0, math.pi, n)
            error = abs(estimate - 2.0)
            sin_rows.append({
                "method": name, "param": f"n={n}", "estimate": estimate,
                "error": error,
                "ratio": None if previous is None else previous / error,
            })
            previous = error
    for order in (4, 8, 16):
        estimate = gauss_legendre(math.sin, 0.0, math.pi, order)
        sin_rows.append({"method": "gauss-legendre", "param": f"order={order}",
                         "estimate": estimate,
                         "error": abs(estimate - 2.0), "ratio": None})
    return {"exact": exact_rows, "sin": sin_rows}


def collect_gradient():
    """Gradient of sum x_i^2 at x_i = (i+1)/(n+1) for n = 1, 2, 5, 100."""
    rows = []
    for n in (1, 2, 5, 100):
        point = (np.arange(n) + 1.0) / (n + 1.0)
        start = time.perf_counter()
        grad = gradient(sum_squares, point)
        elapsed = time.perf_counter() - start
        truth = 2.0 * point
        abs_error = float(np.max(np.abs(grad - truth)))
        rows.append({
            "n": n,
            "evals": 2 * n,
            "abs_error": abs_error,
            "rel_error": abs_error / float(np.max(np.abs(truth))),
            "time": elapsed,
        })
    return rows


def collect_riemann(cells="auto"):
    """Riemann integral of sum x_i^2 over [0,1]^n for n = 1, 2, 5, 100."""
    rows = []
    for n in (1, 2, 5, 100):
        lows = np.zeros(n)
        highs = np.ones(n)
        m = choose_cells(n) if cells == "auto" else int(cells)
        start = time.perf_counter()
        estimate = integral(sum_squares, lows, highs, cells=cells)
        elapsed = time.perf_counter() - start
        exact = n / 3.0
        rows.append({
            "n": n,
            "cells": m,
            "evals": m ** n,
            "estimate": estimate,
            "exact": exact,
            "rel_error": (estimate - exact) / exact,
            "time": elapsed,
        })
    return rows


def collect_mc(samples=1_000_000, seed=2026):
    """Monte Carlo integral of sum x_i^2 over [0,1]^n for n = 1, 2, 5, 100."""
    rows = []
    for n in (1, 2, 5, 100):
        lows = np.zeros(n)
        highs = np.ones(n)
        start = time.perf_counter()
        result = mc_integral(sum_squares_batch, lows, highs,
                             n_samples=samples, seed=seed)
        elapsed = time.perf_counter() - start
        exact = n / 3.0
        rows.append({
            "n": n,
            "samples": samples,
            "estimate": result.estimate,
            "exact": exact,
            "abs_error": abs(result.estimate - exact),
            "stderr": result.stderr,
            "z": (result.estimate - exact) / result.stderr if result.stderr else 0.0,
            "time": elapsed,
        })
    return rows


def collect_demo(samples=1_000_000, seed=2026, cells="auto"):
    """Every number printed by the report, as plain Python data."""
    return {
        "samples": samples,
        "seed": seed,
        "diff": collect_diff1d(),
        "quad": collect_quad1d(samples=samples, seed=seed),
        "gradient": collect_gradient(),
        "riemann": collect_riemann(cells=cells),
        "mc": collect_mc(samples=samples, seed=seed),
    }


# ----------------------------------------------------------------------
# Printing the report
# ----------------------------------------------------------------------

def print_report(data):
    diff = data["diff"]
    quad = data["quad"]

    print("HW10 -- numerical differentiation and integration")
    print("=" * 78)

    print("\n== 1. Single-variable differentiation ==")
    print(f"f(x) = sin(x) at x = 1, exact f'(1) = cos(1) = {diff['exact']:.10f}")
    print(f"\n{'h':>9} {'forward':>15} {'|err|':>10} {'central':>15} "
          f"{'|err|':>10} {'richardson':>15} {'|err|':>10}")
    for row in diff["sweep"]:
        print(f"{row['h']:>9.0e} {row['forward']:>15.10f} "
              f"{abs(row['forward'] - diff['exact']):>10.2e} "
              f"{row['central']:>15.10f} "
              f"{abs(row['central'] - diff['exact']):>10.2e} "
              f"{row['richardson']:>15.10f} "
              f"{abs(row['richardson'] - diff['exact']):>10.2e}")

    print("\nFour functions at h = 1e-5 (estimate, exact value in column 3):")
    print(f"{'f(x)':>9} {'x':>5} {'exact':>15} {'forward':>15} "
          f"{'central':>15} {'richardson':>15}")
    for row in diff["examples"]:
        print(f"{row['label']:>9} {row['x']:>5.1f} {row['exact']:>15.10f} "
              f"{row['forward']:>15.10f} {row['central']:>15.10f} "
              f"{row['richardson']:>15.10f}")

    print("\n== 2. Single-variable integration ==")
    print("(a) f(x) = x^2 on [0, 1], exact = 1/3 = 0.3333333333333333")
    print(f"{'method':<16} {'parameter':>9} {'estimate':>22} {'abs error':>11}")
    for row in quad["exact"]:
        print(f"{row['method']:<16} {row['param']:>9} "
              f"{row['estimate']:>22.16f} "
              f"{abs(row['estimate'] - 1.0 / 3.0):>11.2e}")

    print("\n(b) f(x) = sin(x) on [0, pi], exact = 2 "
          "(ratio = previous error / current error)")
    print(f"{'method':<16} {'param':>9} {'estimate':>22} {'abs error':>11} "
          f"{'ratio':>7}")
    for row in quad["sin"]:
        ratio = "-" if row["ratio"] is None else f"{row['ratio']:.2f}"
        print(f"{row['method']:<16} {row['param']:>9} "
              f"{row['estimate']:>22.16f} {row['error']:>11.2e} {ratio:>7}")

    print("\n== 3. n-variable differentiation (gradient) ==")
    print("f(x) = sum x_i^2, x_i = (i+1)/(n+1), exact gradient = 2x")
    print(f"{'n':>4} {'evals':>7} {'max |err|':>12} {'max rel err':>13} "
          f"{'time':>9}")
    for row in data["gradient"]:
        print(f"{row['n']:>4} {row['evals']:>7} {row['abs_error']:>12.2e} "
              f"{row['rel_error']:>13.2e} {row['time'] * 1e3:>7.1f} ms")

    print("\n== 4. n-variable integration by Riemann sums ==")
    print("f(x) = sum x_i^2 on [0,1]^n, exact = n/3")
    print(f"{'n':>4} {'cells':>6} {'evals':>12} {'estimate':>20} "
          f"{'exact':>10} {'rel error':>11} {'time':>9}")
    for row in data["riemann"]:
        print(f"{row['n']:>4} {row['cells']:>6} {row['evals']:>12,} "
              f"{row['estimate']:>20.12f} {row['exact']:>10.4f} "
              f"{row['rel_error']:>+11.2e} {row['time'] * 1e3:>7.1f} ms")

    big = data["riemann"][-1]
    print(f"\n  n = 100 forces cells = {big['cells']}: one midpoint cell, "
          f"estimate {big['estimate']:.6f}, relative error "
          f"{100 * big['rel_error']:+.1f}%.")

    print("\n== 5. n-variable integration by Monte Carlo ==")
    print(f"same f and box, N = {data['samples']:,}, seed = {data['seed']}")
    print(f"{'n':>4} {'estimate':>20} {'exact':>10} {'abs error':>11} "
          f"{'stderr':>10} {'z':>7} {'time':>9}")
    for row in data["mc"]:
        print(f"{row['n']:>4} {row['estimate']:>20.12f} {row['exact']:>10.4f} "
              f"{row['abs_error']:>11.2e} {row['stderr']:>10.2e} "
              f"{row['z']:>+7.2f} {row['time'] * 1e3:>7.1f} ms")

    print("\n== 6. Cost of a 100-dimensional Riemann grid ==")
    print("cells per axis, total evaluations, and time at 1e9 evaluations/s")
    print(f"{'cells m':>8} {'m^100':>10} {'seconds':>12} {'years':>10}")
    for m in (1, 2, 3, 4):
        evaluations = m ** 100
        seconds = evaluations / 1e9
        years = seconds / (365.25 * 24 * 3600)
        print(f"{m:>8} {evaluations:>10.2e} {seconds:>12.2e} {years:>10.2e}")

    mc100 = data["mc"][-1]
    print(f"\nAt n = 100 the Riemann estimate is {big['estimate']:.4f} "
          f"(rel. error {100 * big['rel_error']:+.1f}%), while Monte Carlo "
          f"with {mc100['samples']:,} samples gives {mc100['estimate']:.6f} "
          f"+- {mc100['stderr']:.2e}.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="HW10: numerical differentiation and integration demo")
    parser.add_argument("--samples", type=int, default=1_000_000,
                        help="Monte Carlo samples (default 1,000,000)")
    parser.add_argument("--seed", type=int, default=2026,
                        help="Monte Carlo seed (default 2026)")
    parser.add_argument("--cells", default="auto",
                        help="Riemann cells per axis, or 'auto' (default)")
    parser.add_argument("--quick", action="store_true",
                        help="use 100,000 Monte Carlo samples")
    parser.add_argument("--test", action="store_true",
                        help="run the correctness test suite")
    args = parser.parse_args(argv)

    if args.test:
        import test_numerics
        return test_numerics.main()

    cells = args.cells
    if cells != "auto":
        cells = int(cells)
    samples = 100_000 if args.quick else args.samples
    data = collect_demo(samples=samples, seed=args.seed, cells=cells)
    print_report(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
