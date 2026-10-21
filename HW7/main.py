#!/usr/bin/env python3
"""HW7: File diff -- Dynamic Programming (LCS) vs Myers' algorithm (non-DP).

Usage examples:
    python3 main.py                       # diff the bundled example files
                                          # with BOTH algorithms + cross-check
    python3 main.py --algo dp             # dynamic programming only
    python3 main.py --algo myers          # Myers' algorithm only
    python3 main.py --file1 X --file2 Y   # diff two arbitrary files
    python3 main.py --benchmark           # timing comparison on synthetic files
"""

import argparse
import os
import random
import time

from diff_dp import diff_dp
from diff_myers import myers_diff
from diff_format import render_unified_text

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_A = os.path.join(HERE, 'examples', 'a.txt')
EXAMPLE_B = os.path.join(HERE, 'examples', 'b.txt')


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def read_lines(path):
    with open(path, encoding='utf-8') as f:
        return f.read().splitlines()


def display_path(p):
    """Show a path relative to the current directory when possible."""
    try:
        rel = os.path.relpath(p)
    except ValueError:
        return p
    return rel if not rel.startswith('..') else p


def apply_ops(a, ops):
    """Reconstruct file B by applying an edit script to file A.

    Used to verify that a script is a valid transformation A -> B.
    """
    out = []
    ai = 0
    for tag, line in ops:
        if tag == 'common':
            assert a[ai] == line, 'common line does not match A'
            out.append(line)
            ai += 1
        elif tag == 'delete':
            assert a[ai] == line, 'deleted line does not match A'
            ai += 1
        else:  # insert
            out.append(line)
    assert ai == len(a), 'script did not consume all of A'
    return out


def difflib_reference_cost(a, b):
    """Upper bound on the optimal edit distance from Python's stdlib.

    ``difflib.SequenceMatcher`` also computes an optimal script, so its
    cost must be >= our D and, in practice, equal to it.  Used only as
    an independent sanity reference.
    """
    import difflib
    sm = difflib.SequenceMatcher(None, a, b)
    cost = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'equal':
            cost += (i2 - i1) + (j2 - j1)
    return cost


def verify(a, b, ops, d, label):
    ok = True
    if apply_ops(a, ops) != b:
        print(f'[FAIL] {label}: script does not transform A into B')
        ok = False
    ref = difflib_reference_cost(a, b)
    if d > ref:
        print(f'[FAIL] {label}: D={d} exceeds reference cost {ref}')
        ok = False
    return ok


def show_diff(title, ops, d, file_a, file_b):
    print(f'=== {title} ===')
    print(f'edit distance D = {d} (insertions + deletions)')
    print(render_unified_text(ops, file_a, file_b))
    print()


# ----------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------

def cmd_diff(args):
    file_a = args.file1 or EXAMPLE_A
    file_b = args.file2 or EXAMPLE_B
    show_a, show_b = display_path(file_a), display_path(file_b)
    a = read_lines(file_a)
    b = read_lines(file_b)
    print(f'--- {show_a}\n+++ {show_b}\n')

    results = {}
    if args.algo in ('dp', 'both'):
        ops, d = diff_dp(a, b)
        results['dp'] = (ops, d)
        show_diff('LCS Dynamic Programming (DP)', ops, d, show_a, show_b)
    if args.algo in ('myers', 'both'):
        ops, d = myers_diff(a, b)
        results['myers'] = (ops, d)
        show_diff("Myers' Algorithm (non-DP)", ops, d, show_a, show_b)

    if len(results) == 2:
        (ops1, d1) = results['dp']
        (ops2, d2) = results['myers']
        print('--- Cross-check ---')
        v1 = verify(a, b, ops1, d1, 'DP')
        v2 = verify(a, b, ops2, d2, 'Myers')
        if v1 and v2 and d1 == d2:
            print(f'[OK] both scripts are valid and minimal (D = {d1})')
        else:
            print(f'[INFO] DP D={d1}, Myers D={d2} (must be equal if both optimal)')
        if (render_unified_text(ops1, file_a, file_b)
                == render_unified_text(ops2, file_a, file_b)):
            print('[OK] both algorithms produced identical diff output')
        else:
            print('[INFO] outputs differ only in tie-breaking; both are minimal')


def make_random_files(n, p, seed=7):
    """Generate a random n-line file A and a file B derived from it.

    ``p`` is the probability that a line of A is *changed* in B
    (replaced by a different random line).  Kept lines additionally get
    a random extra line inserted after them with probability 2%.
    """
    rng = random.Random(seed)
    vocab = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot',
             'golf', 'hotel', 'india', 'juliet']

    def rand_line():
        return ' '.join(rng.choice(vocab) for _ in range(8))

    a = [rand_line() for _ in range(n)]
    b = []
    for line in a:
        if rng.random() < p:
            b.append(rand_line())
        else:
            b.append(line)
            if rng.random() < 0.02:
                b.append(rand_line())
    return a, b


def cmd_benchmark(args):
    print('Benchmark: LCS-DP vs Myers on synthetic files')
    print('"changed" = probability that a line differs between the files')
    print()
    header = (f'{"lines":>6} {"changed":>8} {"D edits":>8} '
              f'{"DP(s)":>9} {"Myers(s)":>9} {"speedup":>8}')
    print(header)
    print('-' * len(header))

    rows = [
        (500, 0.0), (500, 0.05), (500, 0.5), (500, 1.0),
        (1000, 0.0), (1000, 0.05), (1000, 0.5), (1000, 1.0),
        (2000, 0.0), (2000, 0.05), (2000, 0.5),
    ]
    for n, p in rows:
        a, b = make_random_files(n, p)

        t0 = time.perf_counter()
        ops_dp, d_dp = diff_dp(a, b)
        t_dp = time.perf_counter() - t0

        t0 = time.perf_counter()
        ops_my, d_my = myers_diff(a, b)
        t_my = time.perf_counter() - t0

        assert d_dp == d_my, 'algorithms disagree on the edit distance!'
        assert apply_ops(a, ops_my) == b and apply_ops(a, ops_dp) == b

        print(f'{n:>6} {p:>8.2f} {d_dp:>8} {t_dp:>8.3f}s {t_my:>8.3f}s '
              f'{t_dp / t_my:>7.1f}x')
    print()
    print('Observation: Myers is O((n+m)*D), so it crushes DP when the files')
    print('are similar (small D) and only falls behind when the files are')
    print('almost entirely different (D approaches n+m).')


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--algo', choices=['dp', 'myers', 'both'],
                        default='both',
                        help='which algorithm to run (default: both)')
    parser.add_argument('--file1',
                        help='first file (default: examples/a.txt)')
    parser.add_argument('--file2',
                        help='second file (default: examples/b.txt)')
    parser.add_argument('--benchmark', action='store_true',
                        help='run the timing benchmark instead of a diff')
    args = parser.parse_args(argv)

    if args.benchmark:
        cmd_benchmark(args)
    else:
        cmd_diff(args)


if __name__ == '__main__':
    main()
