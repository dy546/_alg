#!/usr/bin/env python3
"""HW8: Traveling Salesman Problem -- five solving methods.

  greedy     greedy algorithm (nearest neighbour, all starts)
  2opt       improvement method (deterministic 2-opt local search)
  hill       hill climbing (random 2-opt moves, random restarts)
  sa         simulated annealing (Metropolis + geometric cooling)
  gd         gradient descent (projected GD on a soft-assignment relaxation)

Usage:
  python3 main.py                    # demo: all five methods on one instance
  python3 main.py --algo sa          # a single method with a detailed trace
  python3 main.py --n 40 --seed 7    # different instance (default n=30 seed=42)
  python3 main.py --kind circle      # cities on a circle (optimal is known)
  python3 main.py --benchmark        # compare all methods across sizes
  python3 main.py --test             # run the correctness test suite
"""

import argparse
import os
import time

from greedy import greedy_tsp
from gradient_descent import gradient_descent_tsp
from hill_climbing import hill_climb_restarts
from improvement import two_opt_tsp
from simulated_annealing import simulated_annealing
from tsp_core import (DEFAULT_COLORS, brute_force_tsp, dist_matrix,
                      downsample, format_time, is_valid_tour, make_cities,
                      tour_length, write_history_svg, write_tour_svg)

HERE = os.path.dirname(os.path.abspath(__file__))
PLOTS = os.path.join(HERE, 'plots')

METHODS = ['greedy', '2opt', 'hill', 'sa', 'gd']
LABELS = {
    'greedy': 'greedy (nearest neighbour)',
    '2opt':   'improvement (2-opt)',
    'hill':   'hill climbing (restarts)',
    'sa':     'simulated annealing',
    'gd':     'gradient descent (relaxation)',
}


# ----------------------------------------------------------------------
# Running the methods
# ----------------------------------------------------------------------

def run_method(name, cities, D, n, seed):
    """Run one method; return (order, length, history, seconds)."""
    t0 = time.perf_counter()
    if name == 'greedy':
        order, length, history = greedy_tsp(D, seed=seed)
    elif name == '2opt':
        init, _, _ = greedy_tsp(D, seed=seed)
        order, length, history = two_opt_tsp(D, init)
    elif name == 'hill':
        order, length, history, _lengths = hill_climb_restarts(
            D, n_restarts=30, seed=seed)
    elif name == 'sa':
        init, _, _ = greedy_tsp(D, seed=seed)
        order, length, history = simulated_annealing(D, init, seed=seed)
    elif name == 'gd':
        init, _, _ = greedy_tsp(D, seed=seed)
        order, length, history = gradient_descent_tsp(
            cities, D, init, seed=seed)
    else:
        raise ValueError(f'unknown method: {name!r}')
    dt = time.perf_counter() - t0
    assert is_valid_tour(order, n), f'{name}: invalid tour'
    assert abs(tour_length(order, D) - length) < 1e-6, f'{name}: bad length'
    return order, length, history, dt


def run_all(cities, D, n, seed):
    results = {}
    for name in METHODS:
        order, length, history, dt = run_method(name, cities, D, n, seed)
        results[name] = (order, length, history, dt)
    return results


# ----------------------------------------------------------------------
# Output helpers
# ----------------------------------------------------------------------

def print_table(results, n, opt_len=None, kind='uniform', seed=42):
    best = min(res[1] for res in results.values())
    best_name = [m for m in METHODS if results[m][1] <= best + 1e-9][0]
    print(f'TSP instance: n={n} {kind} cities, seed={seed}')
    if opt_len is not None:
        print(f'optimal tour length (exhaustive): {opt_len:.2f}')
    print()
    print(f'{"method":<30} {"length":>10} {"gap vs best":>12} {"time":>9}')
    print('-' * 63)
    for name in METHODS:
        _order, length, _hist, dt = results[name]
        gap = (length - best) / best * 100.0
        print(f'{LABELS[name]:<30} {length:>10.2f} {gap:>+11.2f}% '
              f'{format_time(dt):>9}')
    print('-' * 63)
    print(f'best found: {best:.2f}  (by {LABELS[best_name]})')


def save_plots(cities, results, n, seed):
    os.makedirs(PLOTS, exist_ok=True)
    for name in METHODS:
        order, _length, _hist, _dt = results[name]
        write_tour_svg(cities, [(LABELS[name], order, DEFAULT_COLORS[name])],
                       f'TSP n={n} seed={seed}: {LABELS[name]}',
                       os.path.join(PLOTS, f'tour_{name}.svg'))
    histories = [
        (LABELS[name], downsample([(x, y) for x, y in results[name][2]]),
         DEFAULT_COLORS[name])
        for name in METHODS
    ]
    write_history_svg(histories, f'TSP n={n} seed={seed}: convergence of the five methods',
                      os.path.join(PLOTS, 'convergence.svg'))
    print(f'plots written to {os.path.relpath(PLOTS)}/')


# ----------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------

def cmd_demo(args):
    n, seed = args.n, args.seed
    cities = make_cities(n, seed=seed, kind=args.kind)
    D = dist_matrix(cities)
    opt = None
    if n <= 10:
        _o, opt = brute_force_tsp(D)
    if args.algo == 'all':
        results = run_all(cities, D, n, seed)
        print_table(results, n, opt, kind=args.kind, seed=seed)
        save_plots(cities, results, n, seed)
    else:
        order, length, history, dt = run_method(args.algo, cities, D, n, seed)
        print(f'TSP instance: n={n} {args.kind} cities, seed={seed}')
        if opt is not None:
            print(f'optimal tour length: {opt:.2f}')
        print(f'{LABELS[args.algo]}: length = {length:.2f}  ({format_time(dt)})')
        write_tour_svg(cities, [(LABELS[args.algo], order,
                                 DEFAULT_COLORS[args.algo])],
                       f'TSP n={n} seed={seed}: {LABELS[args.algo]}',
                       os.path.join(PLOTS, f'tour_{args.algo}.svg'))
        write_history_svg(
            [(LABELS[args.algo], downsample(history),
              DEFAULT_COLORS[args.algo])],
            f'TSP n={n} seed={seed}: {LABELS[args.algo]}',
            os.path.join(PLOTS, f'history_{args.algo}.svg'))
        print(f'plot written to {os.path.relpath(PLOTS)}/')


def cmd_benchmark(_args):
    sizes = [10, 20, 40, 80]
    quality = {m: [] for m in METHODS}
    runtime = {m: [] for m in METHODS}
    optima = {}
    bests = {}
    for n in sizes:
        cities = make_cities(n, seed=100 + n)
        D = dist_matrix(cities)
        if n <= 10:
            _o, opt = brute_force_tsp(D)
            optima[n] = opt
        per_size = []
        for m in METHODS:
            _order, length, _hist, dt = run_method(m, cities, D, n, seed=7)
            quality[m].append((n, length))
            runtime[m].append((n, dt))
            per_size.append(length)
        bests[n] = min(per_size)

    print('Benchmark: uniform random cities, fixed seeds (algorithms use seed=7)')
    print()
    print('Tour length  (gap% = above the best of the five methods on that size)')
    header = f'{"method":<30}' + ''.join(f'{n:>14}' for n in sizes)
    print(header)
    print('-' * len(header))
    if 10 in optima:
        print(f'{"optimal (exhaustive)":<30}'
              + ''.join(f'{optima[10]:>14.2f}' if n == 10 else f'{"--":>14}'
                        for n in sizes))
    for m in METHODS:
        row = []
        for n, length in quality[m]:
            gap = (length - bests[n]) / bests[n] * 100.0
            row.append(f'{length:>8.2f} {gap:>+4.1f}%')
        print(f'{LABELS[m]:<30}' + ''.join(f'{cell:>14}' for cell in row))
    print()
    print('Runtime (seconds)')
    print(f'{"method":<30}' + ''.join(f'{n:>14}' for n in sizes))
    print('-' * len(header))
    for m in METHODS:
        row = [format_time(dt) for _n, dt in runtime[m]]
        print(f'{LABELS[m]:<30}' + ''.join(f'{cell:>14}' for cell in row))
    print()
    print('Observations: hill climbing with restarts and simulated annealing')
    print('find the shortest tours; the single deterministic 2-opt pass is')
    print('within a few percent at a tiny fraction of the time; greedy is')
    print('fast but far from optimal on larger instances; gradient descent is')
    print('a continuous-relaxation demonstration -- it improves its greedy')
    print('start on most sizes but is the least competitive method.')


def cmd_test(_args):
    from test_tsp import run_all_tests
    run_all_tests()


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--algo', choices=['all'] + METHODS, default='all',
                        help='method to run (default: all)')
    parser.add_argument('--n', type=int, default=30,
                        help='number of cities (default: 30)')
    parser.add_argument('--seed', type=int, default=42,
                        help='random seed for the city set (default: 42)')
    parser.add_argument('--kind', choices=['uniform', 'circle', 'cluster'],
                        default='uniform',
                        help='city distribution (default: uniform)')
    parser.add_argument('--benchmark', action='store_true',
                        help='run the cross-size comparison')
    parser.add_argument('--test', action='store_true',
                        help='run the correctness test suite')
    args = parser.parse_args(argv)

    if args.test:
        cmd_test(args)
    elif args.benchmark:
        cmd_benchmark(args)
    else:
        cmd_demo(args)


if __name__ == '__main__':
    main()
