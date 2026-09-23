import time

from recurrence import (
    t1, t2, t3, t4,
    t1_closed, t2_closed, t3_closed, t4_closed,
    is_power_of_two,
)


def verify_correctness():
    print("=" * 64)
    print("Correctness check (recurrence vs. closed form)")
    print("=" * 64)

    cases = [
        ("T(n) = T(n-1) + 8    ", t1, t1_closed, list(range(1, 51))),
        ("T(n) = 2*T(n-1) + 9  ", t2, t2_closed, list(range(1, 26))),
    ]

    powers_of_two = [2 ** k for k in range(0, 15)]
    cases.append(("T(n) = 2*T(n/2) + 1  ", t3, t3_closed, powers_of_two))
    cases.append(("T(n) = T(n/2) + 1    ", t4, t4_closed, powers_of_two))

    all_ok = True
    for name, recur, closed, ns in cases:
        ok = True
        for n in ns:
            got = recur(n)
            expected = closed(n)
            if got != expected:
                ok = False
                all_ok = False
                print(f"  [FAIL] {name} n={n}: recurrence={got}, closed form={expected}")
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name} (n = {ns[0]} .. {ns[-1]}, {len(ns)} values)")
    print()


def print_solutions():
    print("=" * 64)
    print("Solutions")
    print("=" * 64)
    print("  1. T(n) = T(n-1) + 8,   T(1) = 1")
    print("     T(n) = 1 + 8(n-1) = 8n - 7")
    print("     T(10) = 73, T(100) = 793")
    print()
    print("  2. T(n) = 2*T(n-1) + 9, T(1) = 1")
    print("     T(n) = 2^(n-1) + 9*(2^(n-1) - 1) = 10*2^(n-1) - 9")
    print("     T(10) = 5,111, T(20) = 5,242,871")
    print()
    print("  3. T(n) = 2*T(n/2) + 1, T(1) = 1   (n = 2^k)")
    print("     T(n) = 2n - 1")
    print("     T(1024) = 2,047")
    print()
    print("  4. T(n) = T(n/2) + 1,   T(1) = 1   (n = 2^k)")
    print("     T(n) = log2(n) + 1")
    print("     T(1024) = 11")
    print()


def print_complexity_table():
    print("=" * 64)
    print("Complexity")
    print("=" * 64)
    rows = [
        ("T(n) = T(n-1) + 8", "8n - 7", "O(n)"),
        ("T(n) = 2*T(n-1) + 9", "10*2^(n-1) - 9", "O(2^n)"),
        ("T(n) = 2*T(n/2) + 1", "2n - 1", "O(n)"),
        ("T(n) = T(n/2) + 1", "log2(n) + 1", "O(log n)"),
    ]
    print(f"  {'Recurrence':<24}{'Closed form':<20}{'Big O':<10}")
    print("  " + "-" * 54)
    for rec, closed, bigo in rows:
        print(f"  {rec:<24}{closed:<20}{bigo:<10}")
    print()


def timeit(func, n, repeat=5):
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        func(n)
        best = min(best, time.perf_counter() - start)
    return best


def benchmark():
    print("=" * 64)
    print("Benchmark (best of 5 runs, Python)")
    print("=" * 64)

    # 1. T(n) = T(n-1) + 8 grows linearly: n up to 900 (recursion limit).
    print("  1. T(n) = T(n-1) + 8  (linear, O(n))")
    print(f"     {'n':<8}{'time (s)':>14}")
    for n in [100, 300, 600, 900]:
        t = timeit(t1, n)
        print(f"     {n:<8}{t:>14.6f}")
    print()

    # 2. T(n) = 2*T(n-1) + 9 grows exponentially: stop early.
    print("  2. T(n) = 2*T(n-1) + 9  (exponential, O(2^n))")
    print(f"     {'n':<8}{'calls 2^(n-1)-1':>18}{'time (s)':>14}")
    for n in [10, 15, 20, 25]:
        t = timeit(t2, n, repeat=3)
        print(f"     {n:<8}{2 ** (n - 1) - 1:>18,}{t:>14.6f}")
    print()

    # 3. T(n) = 2*T(n/2) + 1: linear, huge n possible.
    print("  3. T(n) = 2*T(n/2) + 1  (linear, O(n))")
    print(f"     {'n':<10}{'time (s)':>14}")
    for n in [2 ** k for k in (8, 10, 12, 14)]:
        t = timeit(t3, n)
        print(f"     {n:<10}{t:>14.6f}")
    print()

    # 4. T(n) = T(n/2) + 1: logarithmic, enormous n possible.
    print("  4. T(n) = T(n/2) + 1  (logarithmic, O(log n))")
    print(f"     {'n':<10}{'time (s)':>14}")
    for n in [2 ** k for k in (8, 12, 16, 20)]:
        t = timeit(t4, n)
        print(f"     {n:<10}{t:>14.6f}")
    print()


def main():
    verify_correctness()
    print_solutions()
    print_complexity_table()
    benchmark()


if __name__ == "__main__":
    main()
