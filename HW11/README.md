# HW10: Numerical Differentiation and Integration

Compute derivatives and integrals numerically, and watch the same problem
change character as the dimension grows:

| # | Assignment item | Implementation |
|---|---|---|
| 1 | Single-variable differentiation | [`differentiate.py`](differentiate.py) — forward / backward / central differences, Richardson extrapolation |
| 2 | Single-variable integration | [`quadrature.py`](quadrature.py) — trapezoid, Simpson, Gauss-Legendre |
| 3 | Single-variable Monte Carlo integration | [`monte_carlo.py`](monte_carlo.py) — the `n = 1` case of `mc_integral` |
| 4 | n-variable differentiation (gradient) | [`differentiate.py`](differentiate.py) — `gradient` |
| 5 | n-variable integration (hypervolume) | [`riemann.py`](riemann.py) — `integral(f, low, high)` |
| 6 | n-variable Monte Carlo integration | [`monte_carlo.py`](monte_carlo.py) — `mc_integral` |
| 7 | 1-D, 2-D, 5-D, 100-D runs of `f(x) = Σ xᵢ²` on `[0,1]ⁿ` | [`main.py`](main.py) — sections 4 and 5 of the report |
| 8 | Tests for everything | [`test_numerics.py`](test_numerics.py) — 62 checks |

Every number in this README was produced by `python3 main.py` and is
reproducible with the fixed seed 2026.

---

## AI usage disclosure

AI was used to produce this assignment. The code, the test suite, and this
README were drafted by an AI coding agent (OpenCode running a large language
model), working from the assignment statement and an agreed design. The author
reviewed the code, ran the full test suite and the demo, and checked every
number reported in this README against the analytic values in Section 3 —
no result is quoted without being reproduced by `python3 main.py`.

The same statement appears as a two-line header comment in every Python file:

```python
# AI disclosure: drafted with AI assistance (OpenCode / LLM); reviewed and
# verified by the author. See README.md, "AI usage disclosure".
```

---

## 1. Quick start

```bash
cd HW10

python3 main.py                     # full report, 1,000,000 Monte Carlo samples (~3 s)
python3 main.py --quick             # same report with 100,000 samples (~1.5 s)
python3 main.py --samples 5000000   # more samples, smaller statistical error
python3 main.py --seed 7            # different random stream
python3 main.py --cells 20          # fixed Riemann grid instead of "auto"
python3 main.py --test              # run the test suite
python3 test_numerics.py            # the same tests, standalone
```

Requirements: Python 3.8+ and NumPy (already used by HW8 in this course).
No other dependencies.

---

## 2. Mathematics

### 2.1 Single-variable differentiation

Three finite differences of step `h`:

```
forward     f'(x) ≈ (f(x+h) - f(x)) / h        truncation error  -h/2 · f''(ξ)
backward    f'(x) ≈ (f(x) - f(x-h)) / h        truncation error  +h/2 · f''(ξ)
central     f'(x) ≈ (f(x+h) - f(x-h)) / (2h)   truncation error  -h²/6 · f'''(ξ)
```

Central differences are one order more accurate per unit of work, and they are
*exact* for quadratics and cubics because the third derivative vanishes.

Richardson extrapolation exploits the even-power error series of the central
difference and cancels the `h²` term:

```
D_R(h) = (4·D(h/2) − D(h)) / 3          truncation error O(h⁴)
```

Smaller `h` is not always better: the truncation error falls but cancellation
in `f(x+h) − f(x−h)` amplifies rounding. The total error is U-shaped in `h`,
which the demo table shows directly (minimum around `h = 10⁻⁵`).

### 2.2 Single-variable integration

Composite rules on `n` subintervals of `[a, b]`, `h = (b−a)/n`:

```
trapezoid   h·[ f(a)/2 + f(a+h) + ... + f(b−h) + f(b)/2 ]      error O(h²)
simpson     h/3·[ f(a) + 4f(a+h) + 2f(a+2h) + ... + f(b) ]     error O(h⁴)
            (n even)
gauss       Σ wᵢ·f(xᵢ)  on k nodes, mapped from [-1,1] to [a,b]  exact for
            polynomials of degree ≤ 2k−1
```

Simpson integrates cubics exactly; Gauss-Legendre with `k` nodes integrates
polynomials up to degree `2k−1` exactly. Both are therefore machine-precision
on `f(x) = x²`, while the trapezoid rule keeps a visible `O(h²)` error.

### 2.3 n-variable gradient

`gradient` applies the central difference coordinate by coordinate:

```
∂f/∂xᵢ ≈ (f(x + h·eᵢ) − f(x − h·eᵢ)) / (2h)
```

with `eᵢ` the i-th unit vector. Cost: `2n` evaluations (`n+1` for the one-sided
forms, because `f(x)` is reused). For `f(x) = Σ xᵢ²` the central formula is
exact up to rounding, so the error is pure floating-point noise — at `n = 100`
it is `1.7×10⁻¹⁰` relative with only 200 evaluations.

### 2.4 Riemann integral in n dimensions

The required function is

```python
integral(f, low, high)
```

where `n = len(low) = len(high)`. It splits every axis into `m` equal cells and
evaluates `f` once per cell centre (the midpoint rule by default):

```
∫ f dV ≈ (∏ Δxᵢ) · Σ_{j₁=0}^{m−1} ... Σ_{jₙ=0}^{m−1}
                        f(low + ((j₁+½)Δx₁, ..., (jₙ+½)Δxₙ))
```

where `Δxᵢ = (highᵢ − lowᵢ)/m`. **The cost is exactly `mⁿ` evaluations**, and
that exponent is the whole story of this homework. The `"auto"` rule picks the
largest `m ≤ max_cells` with `mⁿ ≤ budget` (`budget = 100 000`,
`max_cells = 1000` by default), which gives:

| n | 1 | 2 | 5 | 10 | 100 |
|---|---|---|---|---|---|
| cells chosen by `"auto"` | 1000 | 316 | 10 | 3 | 1 |
| evaluations | 10³ | 9.99×10⁴ | 10⁵ | 5.9×10⁴ | 1 |

The `max_cells` cap is what stops `n = 1` at 1000 cells; the budget is what
stops `n = 5` at 10 cells; and at `n = 100` neither matters, because `2¹⁰⁰`
already exceeds every sane budget. A grid above `max_evals = 10⁷` raises
`ValueError` instead of running for hours.

Two implementation details matter:

* the grid is traversed by an odometer (`itertools.product`), so memory is
  `O(n)`, not `O(mⁿ)`;
* the rule can be `"left"`, `"mid"` or `"right"`, which makes the textbook
  left/right Riemann sums available and shows their `O(h)` vs `O(h²)` bias.

### 2.5 Monte Carlo integration

Draw `N` uniform points `Xᵢ` in the box and average:

```
estimate = V · (1/N) Σ f(Xᵢ),        V = ∏ (highᵢ − lowᵢ)
stderr   = V · σ / √N,               σ² = Var[f(X)] over the box
```

The standard error shrinks as `1/√N` and — unlike the Riemann grid — does not
depend on the dimension. For `f(x) = Σ xᵢ²` on `[0,1]ⁿ`, each coordinate
contributes `Var(x²) = 1/5 − 1/9 = 4/45`, so

```
stderr = √(4n / (45N)).
```

At `N = 10⁶`: `2.98×10⁻⁴` for `n = 1` and `2.98×10⁻³` for `n = 100` — the
absolute error grows like `√n`, but the *relative* error shrinks like `1/√n`.

`mc_integral` accepts two styles of `f`: point-wise (`f(point) -> float`) or
batch-wise (`f(points) -> (k,)`). It probes the function once with a
deterministic batch, then evaluates the chosen way in chunks; both styles
produce bit-identical results for the same seed.

---

## 3. Exact value used everywhere

For `f(x) = x₁² + ... + xₙ²`, `low = 0`, `high = 1`:

```
∫_{[0,1]ⁿ} Σ xᵢ² dV = Σᵢ ∫₀¹ xᵢ² dxᵢ · ∏_{j≠i} ∫₀¹ dxⱼ = n · (1/3) = n/3
```

| n | 1 | 2 | 5 | 100 |
|---|---|---|---|---|
| exact value | 0.333333… | 0.666667… | 1.666667… | 33.333333… |

For this particular `f` the midpoint rule has a closed-form error too. On one
axis, `(1/m)Σ ((j+½)/m)² = 1/3 − 1/(12m²)`, and summing the `n` coordinates
gives

```
estimate = n/3 − n/(12m²)      ⇒      relative error = −1/(4m²)
```

which is exactly what the demo table shows: `−2.5×10⁻⁷`, `−2.5×10⁻⁶`,
`−2.5×10⁻³`, `−2.5×10⁻¹` for `m = 1000, 316, 10, 1`.

---

## 4. API reference

### `differentiate.py`

| Function | Signature | Returns |
|---|---|---|
| `derivative` | `derivative(f, x, h=1e-5, method="central")` | `float`, estimate of `f'(x)` |
| `richardson_derivative` | `richardson_derivative(f, x, h=1e-2)` | `float`, `O(h⁴)` estimate |
| `gradient` | `gradient(f, x, h=1e-5, method="central")` | `ndarray(n)`, estimate of `∇f(x)` |

Raises `ValueError` for `h ≤ 0`, an unknown method, or an `x` that is not a
non-empty 1-D point.

### `quadrature.py`

| Function | Signature | Rule / error |
|---|---|---|
| `trapezoid` | `trapezoid(f, a, b, n=1000)` | composite trapezoid, `O(h²)` |
| `simpson` | `simpson(f, a, b, n=1000)` | composite Simpson, `O(h⁴)`, `n` must be even |
| `gauss_legendre` | `gauss_legendre(f, a, b, order=16)` | Gauss-Legendre, exact for degree `≤ 2·order−1` |

Raises `ValueError` for `trapezoid(n < 1)`, `simpson(n < 2)`, `simpson(odd n)`
and `gauss_legendre(order < 1)`.

### `riemann.py`

| Function | Signature | Purpose |
|---|---|---|
| `integral` | `integral(f, low, high, cells="auto", rule="mid", budget=100_000, max_cells=1000, max_evals=10_000_000)` | n-variable Riemann sum |
| `choose_cells` | `choose_cells(n, budget=100_000, max_cells=1000)` | largest `m` with `mⁿ ≤ budget` |
| `as_bounds` | `as_bounds(low, high)` | normalise scalar or array bounds |

`integral` accepts scalars (`n = 1`) or equal-length sequences. In one
dimension `f` is called with a `float`; in n dimensions with a length-`n`
array. Raises `ValueError` for mismatched or empty bounds, a bad rule, `cells`
above `max_evals`, or a non-positive `cells`. Reversed bounds flip the sign;
zero-width bounds return `0`.

### `monte_carlo.py`

| Function | Signature | Returns |
|---|---|---|
| `mc_integral` | `mc_integral(f, low, high, n_samples=1_000_000, seed=2026, chunk=10_000)` | `MCResult(estimate, stderr, n_samples, dimension)` |

Raises `ValueError` for `n_samples < 2`, `chunk < 1`, or bad bounds.

---

## 5. Results

### 5.1 Full report

`python3 main.py` (verbatim; timings are from the author's machine and vary):

```
HW10 -- numerical differentiation and integration
==============================================================================

== 1. Single-variable differentiation ==
f(x) = sin(x) at x = 1, exact f'(1) = cos(1) = 0.5403023059

        h         forward      |err|         central      |err|      richardson      |err|
    1e+00    0.0678264420   4.72e-01    0.4546487134   8.57e-02    0.5392096929   1.09e-03
    5e-01    0.3120480036   2.28e-01    0.5180694480   2.22e-02    0.5402324756   6.98e-05
    2e-01    0.4300545382   1.10e-01    0.5346917187   5.61e-03    0.5402979170   4.39e-06
    1e-01    0.4973637525   4.29e-02    0.5394022522   9.00e-04    0.5403021933   1.13e-07
    1e-02    0.5360859810   4.22e-03    0.5402933009   9.00e-06    0.5403023059   1.13e-11
    1e-03    0.5398814804   4.21e-04    0.5403022158   9.01e-08    0.5403023059   3.54e-14
    1e-05    0.5402980985   4.21e-06    0.5403023059   1.11e-11    0.5403023059   1.11e-11
    1e-07    0.5403022640   4.18e-08    0.5403023057   1.94e-10    0.5403023049   9.34e-10

Four functions at h = 1e-5 (estimate, exact value in column 3):
     f(x)     x           exact         forward         central      richardson
      x^2   0.7    1.4000000000    1.4000100000    1.4000000000    1.4000000000
      x^3   2.0   12.0000000000   12.0000600003   12.0000000002   11.9999999998
   sin(x)   1.0    0.5403023059    0.5402980985    0.5403023059    0.5403023059
   exp(x)   0.5    1.6487212707    1.6487295143    1.6487212707    1.6487212707

== 2. Single-variable integration ==
(a) f(x) = x^2 on [0, 1], exact = 1/3 = 0.3333333333333333
method           parameter               estimate   abs error
trapezoid             n=10     0.3350000000000001    1.67e-03
trapezoid            n=100     0.3333500000000000    1.67e-05
simpson               n=10     0.3333333333333335    1.67e-16
simpson              n=100     0.3333333333333334    1.11e-16
gauss-legendre     order=4     0.3333333333333333    5.55e-17
gauss-legendre    order=16     0.3333333333333333    5.55e-17
monte carlo      N=1,000,000     0.3330415088263089    2.92e-04

(b) f(x) = sin(x) on [0, pi], exact = 2 (ratio = previous error / current error)
method               param               estimate   abs error   ratio
trapezoid            n=100     1.9998355038874436    1.64e-04       -
trapezoid            n=200     1.9999588764792162    4.11e-05    4.00
trapezoid            n=400     1.9999897191515132    1.03e-05    4.00
simpson              n=100     2.0000000108245044    1.08e-08       -
simpson              n=200     2.0000000006764731    6.76e-10   16.00
simpson              n=400     2.0000000000422751    4.23e-11   16.00
gauss-legendre     order=4     1.9999842284577227    1.58e-05       -
gauss-legendre     order=8     1.9999999999999933    6.66e-15       -
gauss-legendre    order=16     2.0000000000000009    8.88e-16       -

== 3. n-variable differentiation (gradient) ==
f(x) = sum x_i^2, x_i = (i+1)/(n+1), exact gradient = 2x
   n   evals    max |err|   max rel err      time
   1       2     1.78e-12      1.78e-12     0.0 ms
   2       4     2.37e-12      1.78e-12     0.0 ms
   5      10     1.35e-11      8.08e-12     0.0 ms
 100     200     3.34e-10      1.69e-10     1.0 ms

== 4. n-variable integration by Riemann sums ==
f(x) = sum x_i^2 on [0,1]^n, exact = n/3
   n  cells        evals             estimate      exact   rel error      time
   1   1000        1,000       0.333333250000     0.3333   -2.50e-07     4.8 ms
   2    316       99,856       0.666664997597     0.6667   -2.50e-06   402.2 ms
   5     10      100,000       1.662500000000     1.6667   -2.50e-03   399.1 ms
 100      1            1      25.000000000000    33.3333   -2.50e-01     0.6 ms

  n = 100 forces cells = 1: one midpoint cell, estimate 25.000000, relative error -25.0%.

== 5. n-variable integration by Monte Carlo ==
same f and box, N = 1,000,000, seed = 2026
   n             estimate      exact   abs error     stderr       z      time
   1       0.333041508826     0.3333    2.92e-04   2.98e-04   -0.98     7.0 ms
   2       0.666458208239     0.6667    2.08e-04   4.22e-04   -0.49    50.1 ms
   5       1.665744552383     1.6667    9.22e-04   6.67e-04   -1.38   103.9 ms
 100      33.333791464935    33.3333    4.58e-04   2.98e-03   +0.15  1206.5 ms

== 6. Cost of a 100-dimensional Riemann grid ==
cells per axis, total evaluations, and time at 1e9 evaluations/s
 cells m      m^100      seconds      years
       1   1.00e+00     1.00e-09   3.17e-17
       2   1.27e+30     1.27e+21   4.02e+13
       3   5.15e+47     5.15e+38   1.63e+31
       4   1.61e+60     1.61e+51   5.09e+43

At n = 100 the Riemann estimate is 25.0000 (rel. error -25.0%), while Monte Carlo with 1,000,000 samples gives 33.333791 +- 2.98e-03.
```

### 5.2 What the numbers show

**Differentiation.** Halving `h` divides the forward error by 2 and the central
error by 4, exactly as the `O(h)` / `O(h²)` theory predicts. Richardson
extrapolation cancels the next term as well: at `h = 10⁻³` its error is
`3.5×10⁻¹⁴` against `9.0×10⁻⁸` for the plain central difference. Below
`h ≈ 10⁻⁵` rounding takes over and all three curves bend upward — the classic
U-shape.

**Quadrature.** Simpson and Gauss are at machine precision on `x²` (exact for
cubics and for polynomials up to degree `2k−1`), while the trapezoid error
falls by exactly 4 per doubling of `n`. On `sin` the observed ratios are
`4.00` and `16.00`, the textbook values.

**Gradient.** The central difference is exact for `Σ xᵢ²` up to rounding; at
`n = 100` a 200-evaluation gradient reaches `1.7×10⁻¹⁰` relative error. Cost is
linear in the dimension.

**Riemann vs Monte Carlo at 100 dimensions.**

| n | Riemann (cells) | Riemann evaluations | Riemann rel. error | Monte Carlo evaluations | MC rel. error |
|---|---|---|---|---|---|
| 1 | 1000 | 10³ | −2.5×10⁻⁷ | 10⁶ | 8.8×10⁻⁴ |
| 2 | 316 | 99 856 | −2.5×10⁻⁶ | 10⁶ | 3.1×10⁻⁴ |
| 5 | 10 | 10⁵ | −2.5×10⁻³ | 10⁶ | 5.5×10⁻⁴ |
| 100 | 1 | 1 | −2.5×10⁻¹ | 10⁶ | 1.4×10⁻⁵ |

Up to `n = 2` the grid is far more accurate for less work. At `n = 5` the two
methods are comparable (`4.2×10⁻³` with `10⁵` evaluations versus `9.2×10⁻⁴`
with `10⁶`). At `n = 100` the grid cannot even run: one cell is the only
affordable grid, and one cell is not integration — it is a single sample of
`f` at the centre of the box.

---

## 6. Why the 100-D Riemann answer is 25.0

With one cell per axis the sum has a single term, evaluated at the centre
`(½, …, ½)`:

```
estimate = 1 · f(½, …, ½) = n · (½)² = n/4
```

For `n = 100` that is `25`, against the exact `n/3 ≈ 33.33` — a 25 % error,
because `(n/4)/(n/3) = 3/4`. This is not a bug in the code; it is the exact
value of the only Riemann sum with `m = 1`.

Moving to `m = 2` costs `2¹⁰⁰ ≈ 1.27×10³⁰` evaluations. At one billion
evaluations per second that is `1.27×10²¹` seconds, or about `4×10¹³` years —
roughly 3000 times the age of the universe. The full cost table is printed as
section 6 of the report.

This is the **curse of dimensionality**: a tensor-product grid needs `mⁿ`
points to keep a fixed resolution `h = 1/m`, so its cost is exponential in
`n`. Monte Carlo replaces the grid with random samples and its error,
`σ/√N`, has no `n` in the exponent. At `n = 100` it reaches
`33.3338 ± 0.0030` with one million samples and 1.2 s, where the grid cannot
reach `m = 2` at all.

The price of Monte Carlo is that its error is statistical and only decays as
`1/√N`: one extra decimal digit costs 100× more samples. Riemann sums are
deterministic and, in low dimensions, far more accurate per evaluation.

---

## 7. Testing

`python3 test_numerics.py` (also `python3 main.py --test`) runs 62 checks:

| Group | What is verified |
|---|---|
| 1-D differentiation | values against analytic derivatives of `x²`, `x³`, `sin`, `exp`; error ratios `≈ 2` (forward) and `≈ 4` (central) when `h` halves; Richardson error `< 10⁻⁵` at `h = 0.1` (actual `1.1×10⁻⁷`); invalid `h` and methods rejected |
| Gradient | `Σ xᵢ² → 2x` for `n = 1, 2, 5, 100`; 2-D `sin(x)cos(y)` against the analytic gradient; evaluation counts `2n` (central) and `n+1` (forward); forward error ratio `≈ 2`; empty and 2-D points rejected |
| Quadrature | exactness for a line (trapezoid), a cubic (Simpson), a degree-15 polynomial (Gauss with 8 nodes); `sin` on `[0,π]`; convergence ratios `≈ 4` and `≈ 16`; odd `n`, `n < 1`, `order < 1` rejected |
| Riemann | `x²` on `[0,1]` and `sin` on `[0,π]`; `n = 2, 5` against `n/3`; `choose_cells → 1000, 316, 10, 1`; `n = 100` gives exactly `25.0` and `−25 %`; evaluation count is exactly `mⁿ`; grids above `max_evals`, mismatched/empty bounds and unknown rules rejected; reversed bounds flip the sign; `left < mid < right` |
| Monte Carlo | 1-D and 100-D estimates within `4σ`; `stderr` matches `√(Var/N)` within 10 %; batch-wise and point-wise `f` agree exactly; same seed reproduces the result; constant `f` is exact with zero `stderr`; scalar vs length-1 bounds agree; invalid inputs rejected |
| Demo | all four dimensions present in both tables; every estimate finite; `n = 100` uses one cell; all `z`-scores below 5 |

Last lines of a run:

```
62 passed, 0 failed
```

Every check is deterministic: Monte Carlo tests use fixed seeds, and the
statistical tolerances are 4 standard errors.

---

## 8. Limitations

* `integral` is a fixed-grid midpoint (or left/right) rule. It does not adapt,
  and its cost is always `mⁿ`; for `n > ~8` it is a demonstration, not a
  practical integrator.
* The 100-D Riemann result is reported honestly as the one-cell value `25.0`.
  It is not an approximation anyone should use — it is the measurement of why
  grids fail in high dimensions.
* `gauss_legendre` is only as good as the smoothness of `f`; it is poor for
  functions with singularities or sharp peaks.
* Monte Carlo here is plain uniform sampling. Variance reduction (importance
  sampling, antithetic variates) and quasi-Monte Carlo would improve the
  constant, not the `1/√N` rate, and are out of scope.
* Finite differences degrade on noisy data; automatic differentiation or the
  complex-step method would be exact but are out of scope.
* In one dimension `integral` and `mc_integral` call `f` with a `float`; in
  n dimensions with a length-`n` array. Batch-aware Monte Carlo functions
  receive `(k, n)` arrays.

---

## 9. References

* R. L. Burden, J. D. Faires, *Numerical Analysis*, 10th ed. — finite
  differences, Richardson extrapolation, composite quadrature.
* P. J. Davis, P. Rabinowitz, *Methods of Numerical Integration*, 2nd ed. —
  Gaussian quadrature and error terms.
* W. H. Press et al., *Numerical Recipes*, 3rd ed., ch. 4 — practical
  quadrature and step-size selection.
* N. Metropolis, S. Ulam, *The Monte Carlo Method*, J. Amer. Statist. Assoc.
  44(247), 1949.
* R. E. Caflisch, *Monte Carlo and quasi-Monte Carlo methods*, Acta Numerica
  7, 1998 — why Monte Carlo beats grids in high dimensions.
* C. P. Robert, G. Casella, *Monte Carlo Statistical Methods*, 2nd ed. —
  estimator variance and standard errors.
