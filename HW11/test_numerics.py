#!/usr/bin/env python3
"""HW10: correctness tests for the numerical methods.

Run with:  python3 test_numerics.py    (or: python3 main.py --test)

Every check compares a computed number against a value known in closed
form (analytic derivatives, exact integrals of polynomials, the exact
n/3 of sum x_i^2, the known variance of the Monte Carlo estimator) or
against a scaling law (error O(h), O(h^2), O(h^4), O(1/sqrt(N))).

AI disclosure: drafted with AI assistance (OpenCode / LLM); reviewed and
verified by the author. See README.md, "AI usage disclosure".
"""

import math

import numpy as np

from differentiate import derivative, gradient, richardson_derivative
from main import collect_demo
from monte_carlo import MCResult, mc_integral
from quadrature import gauss_legendre, simpson, trapezoid
from riemann import choose_cells, integral

PASS = 0
FAIL = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"[OK]   {label}")
    else:
        FAIL += 1
        print(f"[FAIL] {label}  {detail}")


def approx(value, target, tol):
    return abs(value - target) <= tol


def raises(exc, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except exc:
        return True
    except Exception:
        return False
    return False


class Counter:
    """Wrap f and count how often it is evaluated."""

    def __init__(self, func):
        self.func = func
        self.calls = 0

    def __call__(self, point):
        self.calls += 1
        return self.func(point)


def sum_squares(point):
    return float(np.sum(np.asarray(point, dtype=float) ** 2))


def sum_squares_batch(points):
    return np.sum(points * points, axis=-1)


# ----------------------------------------------------------------------
# 1. Single-variable differentiation
# ----------------------------------------------------------------------

def check_derivative_1d():
    check("central: d/dx x^2 at 0.7 = 1.4",
          approx(derivative(lambda x: x * x, 0.7), 1.4, 1e-9))
    check("central: d/dx x^3 at 2 = 12",
          approx(derivative(lambda x: x ** 3, 2.0), 12.0, 1e-7))
    check("central: d/dx sin at 1 = cos(1)",
          approx(derivative(math.sin, 1.0), math.cos(1.0), 1e-9))
    check("central: d/dx exp at 0.5 = exp(0.5)",
          approx(derivative(math.exp, 0.5), math.exp(0.5), 1e-9))
    check("backward: d/dx x^2 at 0.7 = 1.4 (within O(h))",
          approx(derivative(lambda x: x * x, 0.7, method="backward"), 1.4, 1e-4))

    coarse = abs(derivative(math.sin, 1.0, 1e-2) - math.cos(1.0))
    fine = abs(derivative(math.sin, 1.0, 5e-3) - math.cos(1.0))
    ratio = coarse / fine
    check("central error is O(h^2): halving h divides it by about 4",
          3.6 <= ratio <= 4.4, f"ratio={ratio:.3f}")

    coarse = abs(derivative(math.sin, 1.0, 1e-2, "forward") - math.cos(1.0))
    fine = abs(derivative(math.sin, 1.0, 5e-3, "forward") - math.cos(1.0))
    ratio = coarse / fine
    check("forward error is O(h): halving h divides it by about 2",
          1.8 <= ratio <= 2.2, f"ratio={ratio:.3f}")

    check("richardson: sin at 1 with h=0.1 reaches O(h^4)",
          approx(richardson_derivative(math.sin, 1.0, 0.1), math.cos(1.0), 1e-5))
    check("derivative rejects h <= 0",
          raises(ValueError, derivative, math.sin, 1.0, 0.0))
    check("derivative rejects unknown methods",
          raises(ValueError, derivative, math.sin, 1.0, 1e-5, "magic"))


# ----------------------------------------------------------------------
# 2. n-variable gradient
# ----------------------------------------------------------------------

def check_gradient():
    for n in (1, 2, 5, 100):
        point = (np.arange(n) + 1.0) / (n + 1.0)
        error = float(np.max(np.abs(gradient(sum_squares, point) - 2.0 * point)))
        check(f"gradient n={n}: sum x_i^2 -> 2x",
              error < 1e-6, f"max error={error:.2e}")

    point = np.array([0.5, 1.1])
    exact = np.array([math.cos(point[0]) * math.cos(point[1]),
                      -math.sin(point[0]) * math.sin(point[1])])
    error = float(np.max(np.abs(gradient(
        lambda v: math.sin(v[0]) * math.cos(v[1]), point) - exact)))
    check("gradient 2-D: sin(x)cos(y) matches the analytic gradient",
          error < 1e-8, f"max error={error:.2e}")

    counted = Counter(sum_squares)
    gradient(counted, np.zeros(4))
    check("gradient central uses 2n evaluations", counted.calls == 8,
          f"calls={counted.calls}")

    counted = Counter(sum_squares)
    gradient(counted, np.zeros(4), method="forward")
    check("gradient forward uses n+1 evaluations", counted.calls == 5,
          f"calls={counted.calls}")

    coarse = gradient(sum_squares, np.array([0.3]), 1e-2, "forward")[0]
    fine = gradient(sum_squares, np.array([0.3]), 5e-3, "forward")[0]
    ratio = (coarse - 0.6) / (fine - 0.6)
    check("gradient forward error is O(h) (ratio about 2)",
          1.8 <= ratio <= 2.2, f"ratio={ratio:.3f}")

    check("gradient rejects an empty point",
          raises(ValueError, gradient, sum_squares, []))
    check("gradient rejects a 2-D point",
          raises(ValueError, gradient, sum_squares, np.zeros((2, 2))))


# ----------------------------------------------------------------------
# 3. Single-variable quadrature
# ----------------------------------------------------------------------

def check_quadrature():
    check("trapezoid is exact for a line",
          approx(trapezoid(lambda x: 3 * x + 1, 0.0, 2.0, 5), 8.0, 1e-12))
    check("simpson is exact for a cubic",
          approx(simpson(lambda x: x ** 3 + 2 * x, 0.0, 1.0, 10), 1.25, 1e-12))

    poly = lambda x: sum(x ** k for k in range(16))
    exact = sum(1.0 / (k + 1) for k in range(16))
    check("gauss-legendre(8) is exact for a degree-15 polynomial",
          approx(gauss_legendre(poly, 0.0, 1.0, 8), exact, 1e-10))

    check("trapezoid: sin on [0, pi], n=1000",
          approx(trapezoid(math.sin, 0.0, math.pi, 1000), 2.0, 1e-5))
    check("simpson: sin on [0, pi], n=1000",
          approx(simpson(math.sin, 0.0, math.pi, 1000), 2.0, 1e-10))

    coarse = abs(trapezoid(math.sin, 0.0, math.pi, 100) - 2.0)
    fine = abs(trapezoid(math.sin, 0.0, math.pi, 200) - 2.0)
    ratio = coarse / fine
    check("trapezoid error is O(h^2) (ratio about 4)",
          3.6 <= ratio <= 4.4, f"ratio={ratio:.3f}")

    coarse = abs(simpson(math.sin, 0.0, math.pi, 100) - 2.0)
    fine = abs(simpson(math.sin, 0.0, math.pi, 200) - 2.0)
    ratio = coarse / fine
    check("simpson error is O(h^4) (ratio about 16)",
          14.0 <= ratio <= 18.0, f"ratio={ratio:.3f}")

    check("simpson rejects an odd n",
          raises(ValueError, simpson, math.sin, 0.0, 1.0, 7))
    check("trapezoid rejects n < 1",
          raises(ValueError, trapezoid, math.sin, 0.0, 1.0, 0))
    check("gauss-legendre rejects order < 1",
          raises(ValueError, gauss_legendre, math.sin, 0.0, 1.0, 0))


# ----------------------------------------------------------------------
# 4. n-variable Riemann integration
# ----------------------------------------------------------------------

def check_riemann():
    square = lambda x: x * x
    check("integral 1-D: x^2 on [0, 1] = 1/3",
          approx(integral(square, 0.0, 1.0), 1.0 / 3.0, 1e-6))
    check("integral 1-D: sin on [0, pi] = 2",
          approx(integral(math.sin, 0.0, math.pi), 2.0, 1e-4))

    for n, tol in ((2, 1e-5), (5, 1e-2)):
        lows = np.zeros(n)
        highs = np.ones(n)
        estimate = integral(sum_squares, lows, highs)
        check(f"integral n={n}: sum x_i^2 = n/3",
              approx(estimate, n / 3.0, tol),
              f"estimate={estimate:.10f} exact={n / 3.0:.10f}")

    check("choose_cells picks 1000, 316, 10, 1 for n = 1, 2, 5, 100",
          [choose_cells(n) for n in (1, 2, 5, 100)] == [1000, 316, 10, 1],
          f"got {[choose_cells(n) for n in (1, 2, 5, 100)]}")

    lows = np.zeros(100)
    highs = np.ones(100)
    estimate = integral(sum_squares, lows, highs)
    check("integral n=100 collapses to one midpoint cell", choose_cells(100) == 1)
    check("integral n=100 returns the one-cell value 25.0",
          approx(estimate, 25.0, 1e-9), f"estimate={estimate!r}")
    check("integral n=100 relative error is exactly -25%",
          approx((estimate - 100.0 / 3.0) / (100.0 / 3.0), -0.25, 1e-12),
          f"rel error={(estimate - 100.0 / 3.0) / (100.0 / 3.0):.3e}")

    counted = Counter(square)
    integral(counted, 0.0, 1.0, cells=7)
    check("integral evaluates f exactly m^n times (1-D, m=7)",
          counted.calls == 7, f"calls={counted.calls}")

    counted = Counter(sum_squares)
    integral(counted, np.zeros(2), np.ones(2), cells=4)
    check("integral evaluates f exactly m^n times (2-D, m=4)",
          counted.calls == 16, f"calls={counted.calls}")

    check("integral refuses a grid above max_evals",
          raises(ValueError, integral, sum_squares, np.zeros(100), np.ones(100), 2))
    check("integral rejects mismatched bounds",
          raises(ValueError, integral, square, [0.0, 0.0], [1.0]))
    check("integral rejects empty bounds",
          raises(ValueError, integral, square, [], []))
    check("integral rejects an unknown rule",
          raises(ValueError, integral, square, 0.0, 1.0, "auto", "triangle"))
    check("integral flips sign for reversed bounds",
          approx(integral(square, 1.0, 0.0), -1.0 / 3.0, 1e-6))

    left = integral(square, 0.0, 1.0, cells=100, rule="left")
    mid = integral(square, 0.0, 1.0, cells=100, rule="mid")
    right = integral(square, 0.0, 1.0, cells=100, rule="right")
    check("left < mid < right for an increasing function",
          left < mid < right and left < 1.0 / 3.0 < right,
          f"left={left:.6f} mid={mid:.6f} right={right:.6f}")


# ----------------------------------------------------------------------
# 5. Monte Carlo integration
# ----------------------------------------------------------------------

def check_monte_carlo():
    square = lambda x: x * x
    samples = 200_000
    result = mc_integral(square, 0.0, 1.0, n_samples=samples, seed=2026)
    theoretical = math.sqrt((4.0 / 45.0) / samples)
    check("MC 1-D: estimate of x^2 on [0, 1] within 4 sigma",
          abs(result.estimate - 1.0 / 3.0) <= 4.0 * theoretical,
          f"estimate={result.estimate:.9f} stderr={result.stderr:.2e}")
    check("MC 1-D: stderr matches sqrt(Var/N) within 10%",
          abs(result.stderr - theoretical) <= 0.1 * theoretical,
          f"stderr={result.stderr:.3e} theory={theoretical:.3e}")
    check("MCResult carries n_samples and dimension",
          isinstance(result, MCResult) and result.n_samples == samples
          and result.dimension == 1)

    lows = np.zeros(100)
    highs = np.ones(100)
    result = mc_integral(sum_squares_batch, lows, highs,
                         n_samples=samples, seed=2026)
    theoretical = math.sqrt((100.0 * 4.0 / 45.0) / samples)
    check("MC n=100: estimate of sum x_i^2 within 4 sigma",
          abs(result.estimate - 100.0 / 3.0) <= 4.0 * theoretical,
          f"estimate={result.estimate:.6f} theory={theoretical:.2e}")
    check("MC n=100: dimension is recorded", result.dimension == 100)

    lows = np.zeros(3)
    highs = np.ones(3)
    batch = mc_integral(sum_squares_batch, lows, highs,
                        n_samples=10_000, seed=7)
    point = mc_integral(sum_squares, lows, highs,
                        n_samples=10_000, seed=7)
    check("batch-wise and point-wise f give identical results",
          batch.estimate == point.estimate and batch.stderr == point.stderr,
          f"batch={batch.estimate!r} point={point.estimate!r}")

    again = mc_integral(sum_squares_batch, lows, highs,
                        n_samples=10_000, seed=7)
    check("the same seed reproduces the estimate", again == batch)

    constant = mc_integral(lambda x: 3.0, 0.0, 1.0, n_samples=10_000, seed=1)
    check("constant f is exact and has zero stderr",
          approx(constant.estimate, 3.0, 1e-12) and constant.stderr < 1e-12,
          f"estimate={constant.estimate!r} stderr={constant.stderr!r}")

    scalar = mc_integral(square, 0.0, 1.0, n_samples=5_000, seed=3)
    listed = mc_integral(square, [0.0], [1.0], n_samples=5_000, seed=3)
    check("scalar and length-1 bounds agree", scalar.estimate == listed.estimate)

    check("mc_integral rejects n_samples < 2",
          raises(ValueError, mc_integral, square, 0.0, 1.0, 1))
    check("mc_integral rejects mismatched bounds",
          raises(ValueError, mc_integral, square, [0.0, 0.0], [1.0]))


# ----------------------------------------------------------------------
# 6. The demo driver
# ----------------------------------------------------------------------

def check_demo():
    data = collect_demo(samples=100_000, seed=2026)
    check("demo covers n = 1, 2, 5, 100 in the Riemann table",
          [row["n"] for row in data["riemann"]] == [1, 2, 5, 100])
    check("demo covers n = 1, 2, 5, 100 in the Monte Carlo table",
          [row["n"] for row in data["mc"]] == [1, 2, 5, 100])
    check("all Riemann estimates are finite",
          all(math.isfinite(row["estimate"]) for row in data["riemann"]))
    check("demo n=100 Riemann uses one cell", data["riemann"][-1]["cells"] == 1)
    check("all demo z-scores are below 5",
          all(abs(row["z"]) < 5.0 for row in data["mc"]),
          f"z={[round(row['z'], 2) for row in data['mc']]}")


def main():
    global PASS, FAIL
    PASS = 0
    FAIL = 0
    check_derivative_1d()
    check_gradient()
    check_quadrature()
    check_riemann()
    check_monte_carlo()
    check_demo()
    print()
    print(f"{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
