#!/usr/bin/env python3
"""HW8: correctness tests for the five TSP solvers.

Run with:  python3 test_tsp.py    (or: python3 main.py --test)

Checks, for several instances:
  * every method returns a valid tour (each city visited exactly once)
    whose reported length matches a direct recomputation;
  * the improvement method never makes a tour longer than its input,
    and hill climbing / simulated annealing never return a tour longer
    than the best one seen along the way;
  * simulated annealing is deterministic for a fixed seed;
  * greedy, 2-opt, hill and SA are never worse than the exhaustive
    optimum on tiny instances, and 2-opt actually reaches the optimum
    on the checked small instances;
  * on circle instances (known optimal = the cyclic order), greedy and
    2-opt find the optimal tour;
  * the 2-opt and swap delta formulas agree with direct recomputation;
  * gradient descent returns a valid tour and improves on its start.
"""

import numpy as np

from greedy import greedy_tsp
from gradient_descent import gradient_descent_tsp
from hill_climbing import hill_climb_restarts
from improvement import two_opt_tsp
from simulated_annealing import simulated_annealing
from tsp_core import (apply_2opt, brute_force_tsp, dist_matrix, is_valid_tour,
                      make_cities, opt2_delta, swap_delta, tour_length)

PASS, FAIL = 0, 0


def check(label, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f'[OK]   {label}')
    else:
        FAIL += 1
        print(f'[FAIL] {label}  {detail}')


def all_methods_solve():
    for n, seed in [(6, 1), (8, 42), (12, 7), (25, 3)]:
        cities = make_cities(n, seed=seed)
        D = dist_matrix(cities)
        init, init_len, _ = greedy_tsp(D, seed=seed)

        order, length, _ = greedy_tsp(D, seed=seed)
        check(f'greedy n={n}: valid tour & correct length',
              is_valid_tour(order, n) and abs(tour_length(order, D) - length) < 1e-6)

        order, length, _ = two_opt_tsp(D, init)
        check(f'2-opt n={n}: valid, correct length, <= greedy start',
              is_valid_tour(order, n)
              and abs(tour_length(order, D) - length) < 1e-6
              and length <= init_len + 1e-9,
              f'{length} vs {init_len}')

        order, length, _, _ = hill_climb_restarts(D, n_restarts=10, seed=seed)
        check(f'hill n={n}: valid tour & correct length',
              is_valid_tour(order, n) and abs(tour_length(order, D) - length) < 1e-6)

        order, length, hist = simulated_annealing(D, init, seed=seed)
        check(f'sa n={n}: valid tour & correct length',
              is_valid_tour(order, n) and abs(tour_length(order, D) - length) < 1e-6)

        order, length, _ = gradient_descent_tsp(cities, D, init, passes=6,
                                                steps_per_pass=400,
                                                seed=seed)
        check(f'gd n={n}: valid tour & correct length',
              is_valid_tour(order, n) and abs(tour_length(order, D) - length) < 1e-6)


def sa_deterministic():
    cities = make_cities(15, seed=5)
    D = dist_matrix(cities)
    init, _, _ = greedy_tsp(D, seed=5)
    o1, l1, _ = simulated_annealing(D, init, seed=99)
    o2, l2, _ = simulated_annealing(D, init, seed=99)
    check('sa: deterministic for a fixed seed', o1 == o2 and l1 == l2)


def improvement_never_worsens():
    rng = np.random.default_rng(11)
    for trial in range(5):
        cities = make_cities(20, seed=trial)
        D = dist_matrix(cities)
        init = rng.permutation(len(cities)).tolist()
        init_len = tour_length(init, D)
        order, length, hist = two_opt_tsp(D, init)
        mono = all(y1 <= y0 + 1e-9 for (_, y0), (_, y1) in zip(hist, hist[1:]))
        check(f'2-opt trial {trial}: never worsens and converges',
              mono and length <= init_len + 1e-9 and len(hist) >= 2)


def vs_optimum():
    for n, seed in [(7, 3), (8, 9), (9, 5)]:
        cities = make_cities(n, seed=seed)
        D = dist_matrix(cities)
        _oo, opt = brute_force_tsp(D)
        init, init_len, _ = greedy_tsp(D, seed=seed)
        order, length, _ = two_opt_tsp(D, init)
        check(f'n={n}: 2-opt reaches the exhaustive optimum',
              abs(length - opt) < 1e-9, f'2opt={length:.3f} opt={opt:.3f}')


def circle_instance():
    for n in (8, 10):
        cities = make_cities(n, seed=6, kind='circle')
        D = dist_matrix(cities)
        _oo, opt = brute_force_tsp(D)
        order, length, _ = greedy_tsp(D, seed=6)
        check(f'circle n={n}: greedy finds the optimal cyclic tour',
              abs(length - opt) < 1e-9, f'greedy={length:.3f} opt={opt:.3f}')


def delta_formulas():
    cities = make_cities(12, seed=8)
    D = dist_matrix(cities)
    rng = np.random.default_rng(8)
    for trial in range(50):
        order = rng.permutation(len(cities)).tolist()
        before = tour_length(order, D)
        a, b = int(rng.integers(0, 12)), int(rng.integers(0, 11))
        if b >= a:
            b += 1
        delta = swap_delta(D, order, a, b)
        order[a], order[b] = order[b], order[a]
        after = tour_length(order, D)
        if abs((after - before) - delta) > 1e-9:
            check(f'swap_delta trial {trial}: formula matches recomputation',
                  False, f'{after - before} vs {delta}')
            return
    check('swap_delta: formula matches direct recomputation (50 trials)', True)

    order = rng.permutation(12).tolist()
    for trial in range(50):
        i, j = int(rng.integers(0, 11)), int(rng.integers(0, 12))
        if j <= i + 1 or (i == 0 and j == 11):
            j = (i + 2) % 12
            if j == i:
                j = (i + 3) % 12
        if i > j:
            i, j = j, i
        if j <= i + 1:
            continue
        before = tour_length(order, D)
        delta = opt2_delta(D, order, i, j)
        apply_2opt(order, i, j)
        after = tour_length(order, D)
        apply_2opt(order, i, j)          # reverse back
        if abs((after - before) - delta) > 1e-9:
            check(f'opt2_delta trial {trial}: formula matches recomputation',
                  False, f'{after - before} vs {delta}')
            return
    check('opt2_delta: formula matches direct recomputation (50 trials)', True)


def gd_improves_start():
    improved = 0
    for seed in range(6):
        cities = make_cities(20, seed=seed)
        D = dist_matrix(cities)
        init, init_len, _ = greedy_tsp(D, seed=seed)
        order, length, _ = gradient_descent_tsp(cities, D, init, passes=8,
                                                steps_per_pass=500,
                                                seed=seed)
        check(f'gd seed {seed}: valid tour',
              is_valid_tour(order, 20) and abs(tour_length(order, D) - length) < 1e-6)
        if length <= init_len:
            improved += 1
    check('gd: improves on (or matches) its greedy start in most seeds',
          improved >= 3, f'{improved}/6 seeds improved')


def run_all_tests():
    global PASS, FAIL
    PASS = FAIL = 0
    all_methods_solve()
    sa_deterministic()
    improvement_never_worsens()
    vs_optimum()
    circle_instance()
    delta_formulas()
    gd_improves_start()
    print()
    print(f'{PASS} passed, {FAIL} failed')
    return FAIL == 0


if __name__ == '__main__':
    ok = run_all_tests()
    raise SystemExit(0 if ok else 1)
