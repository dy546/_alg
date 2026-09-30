# HW4 — Unified Iterative Algorithms Framework

Documentation for `iter_framework.py`: a small but general abstraction that
expresses many classical iterative algorithms in terms of a single loop,
showing that seemingly unrelated numerical methods all share the same
"guess → improve → repeat until stable" structure.

---

## Table of Contents

- [Core Framework](#core-framework)
- [How It Works](#how-it-works)
- [The Demos](#the-demos)
- [Exercise: `iterative3.py`](#exercise-iterative3py)
- [State Types Used](#state-types-used)
- [Run It](#run-it)

---

## Core Framework

The entire framework is one function (iter_framework.py:6):

```python
def generic_iterator(transition_func, is_converged, initial_state, max_iter=1000):
    state = initial_state
    for iteration in range(max_iter):
        next_state = transition_func(state)
        if is_converged(state, next_state, iteration):
            return next_state, iteration + 1
        state = next_state
    print("  [警告] 達到最大迭代次數仍未完全收斂")
    return state, max_iter
```

### Parameters

| Parameter          | Type                    | Meaning                                                            |
| ------------------ | ----------------------- | ------------------------------------------------------------------ |
| `transition_func`  | `state -> state`        | The iteration rule / state update function `g(x)`                  |
| `is_converged`     | `(old, new, i) -> bool`| Stopping predicate: has the process converged at step `i`?         |
| `initial_state`    | any (scalar, vector, matrix, tuple) | Starting point `x₀`                                   |
| `max_iter`         | `int`                   | Safety cap on the number of iterations (default 1000)              |

### Returns

A tuple `(final_state, iterations)`:
- `final_state` — the state when the loop stopped (the converged `next_state`,
  or the last state if the iteration cap was hit).
- `iterations` — number of transitions actually performed.

---

## How It Works

1. **Initialize** — `state = initial_state`.
2. **Advance** — compute `next_state = transition_func(state)`.
3. **Check** — if `is_converged(state, next_state, iteration)` is true, the
   loop stops and returns `next_state`. The predicate receives both the old
   and the new state (plus the iteration counter), so it can test
   "change is small enough" style conditions.
4. **Repeat** — otherwise `state = next_state` and loop again.
5. **Give up safely** — if `max_iter` is reached without convergence, a
   warning is printed and the current state is returned.

The design deliberately keeps the framework *generic*: it knows nothing about
fixed points, eigen-decompositions, clustering or ODEs. All the mathematics
lives in the two closures the caller supplies. Each demo below is just a
different choice of `transition_func`, `is_converged` and `initial_state`.

### Convergence Criteria

The stopping rule is *not* hardcoded. Typical choices used in the demos:

- `np.linalg.norm(new - old) < 1e-6` — Euclidean change below tolerance.
- `np.max(np.abs(new - old)) < 1e-6` — max-norm (infinity-norm) change.
- `np.allclose(old, new, atol=1e-6)` — element-wise closeness.
- Domain-specific predicates, e.g. RK4 stops when `t >= t_end`.

Note that convergence checks compare *successive* iterates, so they measure
stagnation rather than error against an exact solution — a standard and
practical choice for these methods.

---

## The Demos

Each demo constructs its `transition` and `converged` closures and then calls
`generic_iterator` exactly once.

| # | Function | Method | State | Iteration rule (transition) |
| - | -------- | ------ | ----- | --------------------------- |
| 1 | `demo_fixed_point` (line 32) | Fixed-point iteration in 2-D | vector | `x ← [0.5x₀ − 0.2x₁ + 0.3, 0.2x₀ + 0.5x₁ + 0.4]` |
| 2 | `demo_newton` (line 40) | Newton's method for `x² − 4 = 0` | scalar | `x ← x − f(x)/f′(x)` |
| 3 | `demo_gauss_seidel` (line 50) | Gauss–Seidel linear solver `Ax = b` | vector | component-wise `xᵢ ← (bᵢ − Σⱼ≠ᵢ aᵢⱼxⱼ)/aᵢᵢ` |
| 4 | `demo_power_iteration` (line 68) | Power iteration (dominant eigenvector) | vector | `v ← Av / ‖Av‖` |
| 5 | `demo_qr_algorithm` (line 84) | QR algorithm (all eigenvalues) | matrix | `A ← R·Q` from `QR` factorization of `A` |
| 6 | `demo_rk4` (line 94) | RK4 ODE integrator `dy/dt = y − t + 1` | tuple `(t, y)` | classic 4-stage Runge–Kutta step |
| 7 | `demo_pagerank` (line 112) | PageRank (random surfer) | vector | `r ← G·r` with Google matrix `G = dM + (1−d)/n·1` |
| 8 | `demo_kmeans` (line 131) | K-Means clustering (hard EM) | matrix (centroids) | E-step assign labels, M-step recompute means |
| 9 | `demo_em_two_coin` (line 151) | EM for the two-coin problem | tuple `(θ_A, θ_B)` | E-step responsibility weights, M-step MLE update |

### 1. Fixed-point iteration
Finds the fixed point of the affine map
`x ← 0.5x₀ − 0.2x₁ + 0.3`, `x₁ ← 0.2x₀ + 0.5x₁ + 0.4`. Because the map is a
contraction (spectral radius of the linear part < 1), iterating converges to
the unique fixed point. Stops when the Euclidean change drops below `1e-6`.

### 2. Newton's method
Solves `x² − 4 = 0` with the update `x ← x − (x²−4)/(2x)`. Convergence is
quadratic near a root; the demo stops when successive iterates differ by less
than `1e-6`. Starting from `x₀ = 1.0` it converges to `+2`.

### 3. Gauss–Seidel
Solves the tridiagonal system `Ax = b`. Unlike Jacobi, each component update
`xᵢ ← (bᵢ − Σⱼ≠ᵢ aᵢⱼxⱼ)/aᵢᵢ` immediately reuses the freshest values
(`x_new` is mutated in place), which usually speeds convergence. The diagonal
dominance of `A` guarantees convergence here.

### 4. Power iteration
Repeatedly applies `A` and normalizes: `v ← Av/‖Av‖`. `v` converges to the
dominant eigenvector, and the Rayleigh quotient `vᵀAv` gives the largest
eigenvalue. The state is always a unit vector, which keeps the iteration
numerically stable.

### 5. QR algorithm
Applies `A ← RQ` (where `A = QR`), i.e. `transition = np.dot(*reversed(qr(A)))`.
Repeated QR steps drive `A` toward an upper-triangular (quasi-)matrix whose
diagonal contains the eigenvalues. The convergence check sums only the
off-diagonal entries, so the loop stops when the matrix is "diagonal enough".

### 6. RK4 ODE integrator
Integrates `dy/dt = y − t + 1` from `t = 0` to `t = 2` with step `h = 0.2`.
Here the "iteration" is time-stepping: each transition advances `t` by `h`
using the classic 4-stage Runge–Kutta formula. Convergence is replaced by a
domain predicate — stop when `t` reaches `t_end`. This demonstrates that
`generic_iterator` doubles as a general loop driver, not just a fixed-point
solver.

### 7. PageRank
Builds the Google matrix `G = d·M + (1−d)/n·1` from the transition matrix `M`
and damping factor `d = 0.85`, then iterates `r ← Gr`. This is power iteration
on a stochastic matrix, so it converges to the stationary distribution (the
PageRank scores).

### 8. K-Means
Hard EM for clustering. The E-step assigns each point to its nearest centroid;
the M-step moves each centroid to the mean of its assigned points. Because the
centroids only move finitely many times before stabilizing, the
successive-change criterion terminates the algorithm.

### 9. EM — two-coin problem
Given 5 trials of 10 flips, estimates the heads-probabilities `θ_A`, `θ_B` of
two coins without knowing which coin was used per trial. The E-step computes
responsibility probabilities `p_A`, `p_B` for each trial; the M-step
re-estimates each `θ` as the weighted fraction of heads. Converges to a local
maximum of the likelihood.

---

## Exercise: `iterative3.py`

`iterative3.py` is the "user-side" exercise: it solves **√S for S = 612** using
Heron's (Babylonian) method and verifies the result against `math.sqrt`. It
demonstrates how a client problem plugs a concrete update rule into the
iterative framework instead of reimplementing the loop.

### The math: Heron's method

Heron's method for √S is the fixed-point iteration

```
g(x) = 0.5 · (x + S/x)
```

which is exactly Newton–Raphson applied to `f(x) = x² − S`. Starting from any
positive guess `x₀`, `g` is a contraction near the root, so `xₖ → √S`
quadratically.

### How the code maps onto the framework

| Framework concept  | What `iterative3.py` supplies                                     |
| ------------------ | ----------------------------------------------------------------- |
| update rule        | `heron_update(x) = 0.5 * (x + S / x)` (iterative3.py:17)          |
| initial state      | `x0 = 10.0` (default `initial_guess` is `1.0`)                    |
| tolerance          | `tol = 1e-10`                                                     |
| safety cap         | `max_iter = 50`                                                   |
| error measure      | `error_type = "absolute"` (difference between successive iterates)|
| verbosity          | `verbose = True` prints each iteration                            |

The engine call (iterative3.py:21):

```python
result = iterative_solver(
    update_func=heron_update, x0=initial_guess, tol=1e-10,
    max_iter=50, error_type="absolute", verbose=True
)
```

returns a dictionary with `solution`, `iterations`, and `converged`, which is
then printed side by side with `math.sqrt(S)` and the absolute difference.

### Run it

```bash
python iterative3.py
```

Expected output for `S = 612.0`, `x0 = 10.0`: both the calculated root and the
exact root ≈ `24.7386337537` (since 24.7² ≈ 612), with `Convergence Status:
True`.

> **Note — API history:** `iterative3.py` imports `iterative_solver` from
> `iter_framework`. The framework originally exposed only
> `generic_iterator(transition_func, is_converged, initial_state, max_iter)`;
> `iterative_solver` is now provided as a compatibility wrapper
> (iter_framework.py:31) built on top of it:
>
> | `iterative_solver` param | equivalent `generic_iterator` role |
> | ------------------------ | ---------------------------------- |
> | `update_func`            | `transition_func`                  |
> | `x0`                     | `initial_state`                    |
> | `tol`, `error_type`      | folded into `is_converged` (`"absolute"` → `abs(new − old) < tol`, `"relative"` → divides by `|new|`) |
> | `max_iter`               | `max_iter`                         |
> | `verbose`                | not in the core loop; the wrapper prints each iterate |
>
> The wrapper returns a dict `{"solution", "iterations", "converged"}`, where
> `converged` is tracked by a closure flag inside the convergence predicate.

---

The same framework handles many state shapes without modification:

| Type | Examples |
| ---- | -------- |
| scalar `float` | Newton's method |
| `numpy` vector | fixed-point, Gauss–Seidel, power iteration, PageRank |
| `numpy` matrix | QR algorithm, K-Means centroids |
| tuple | RK4 `(t, y)`, EM `(θ_A, θ_B)` |

Any state works as long as the two closures agree on its type.

---

## Run It

```bash
python iter_framework.py
```

The `if __name__ == "__main__":` block runs all nine demos in order and prints
each result plus the number of iterations required. Example output excerpt:

```
--- 2. 牛頓法求根 (Newton's Method: x^2 - 4 = 0) ---
結果: 根 x = 2.000000 (耗時 6 次迭代)
```

## Key Takeaways

1. One tiny loop (`generic_iterator`) can express fixed-point solvers,
   eigensolvers, linear solvers, ODE integrators, and EM-family algorithms.
2. The *strategy* (what iteration means) is injected via `transition_func`;
   the *termination policy* is injected via `is_converged`.
3. Checking the change between successive iterates is a universal, practical
   convergence heuristic across all these methods.
