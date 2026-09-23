import os
import subprocess
import sys
import time

from power2n import power2n, power2n_2a, power2n_2b, power2n_3, _table

HERE = os.path.dirname(os.path.abspath(__file__))


def verify_correctness():
    print("=" * 60)
    print("正確性驗證（與內建 2**n 比較，n = 0 ~ 20）")
    print("=" * 60)
    ok = True
    for n in range(21):
        expected = 2 ** n
        results = {
            "power2n   (方法1)": power2n(n),
            "power2n_2a(方法2a)": power2n_2a(n),
            "power2n_2b(方法2b)": power2n_2b(n),
            "power2n_3 (方法3)": power2n_3(n),
        }
        for name, got in results.items():
            if got != expected:
                ok = False
                print(f"  [FAIL] {name}: n={n}, expected={expected}, got={got}")
    print("  全部通過" if ok else "  有錯誤！")
    print()


def timeit(func, n, repeat=5):
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        func(n)
        best = min(best, time.perf_counter() - start)
    return best


def benchmark_fast(n=100):
    print("=" * 60)
    print(f"效率測試（n = {n}，各測 5 次取最快）")
    print("=" * 60)

    # 方法 1：2**n
    t1 = timeit(power2n, n)

    # 方法 2b：2*power2n(n-1)
    t2b = timeit(power2n_2b, n)

    # 方法 3：遞迴 + 查表（每次清空表格，測冷啟動成本）
    def run_3(n):
        _table.clear()
        return power2n_3(n)

    t3 = timeit(run_3, n)

    results = [
        ("方法 1  ：2**n（直接運算）", t1),
        ("方法 2b ：2*power2n(n-1)", t2b),
        ("方法 3  ：遞迴 + 查表", t3),
    ]
    results.sort(key=lambda x: x[1])

    print(f"  {'方法':<28}{'耗時 (秒)':>16}")
    print("  " + "-" * 44)
    for name, t in results:
        print(f"  {name:<28}{t:>16.9f}")
    print()

    print(f"  n={n} 時 2^n = {power2n(n)}")
    print(f"  （數字長度：{len(str(power2n(n)))} 位數）")
    print()


def benchmark_2a():
    print("=" * 60)
    print("方法 2a：power2n(n-1)+power2n(n-1)（指數成長）")
    print("=" * 60)
    print(f"  {'n':<6}{'呼叫次數 2^(n+1)-1':>24}{'耗時 (秒)':>14}")
    print("  " + "-" * 46)
    for n in [10, 15, 20, 25]:
        t = timeit(power2n_2a, n, repeat=3)
        calls = 2 ** (n + 1) - 1
        print(f"  {n:<6}{calls:>24,d}{t:>14.6f}")
    print()


def benchmark_2a_n100(timeout=10):
    print("=" * 60)
    print(f"方法 2a 挑戰 n = 100（超過 {timeout} 秒就算「跑不出來」）")
    print("=" * 60)
    code = "from power2n import power2n_2a; print(power2n_2a(100))"
    try:
        start = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            timeout=timeout,
            cwd=HERE,
        )
        elapsed = time.perf_counter() - start
        print(f"  竟然在 {elapsed:.3f} 秒內完成，結果 = {proc.stdout.decode().strip()}")
    except subprocess.TimeoutExpired:
        print(f"  n=100 需要 {2**101 - 1:,} 次遞迴呼叫，")
        print(f"  等超過 {timeout} 秒仍然「出不來」，強制終止。")
    print()


def main():
    verify_correctness()
    benchmark_fast(n=100)
    benchmark_2a()
    benchmark_2a_n100()

    print("=" * 60)
    print("結論")
    print("=" * 60)
    print("  * 方法 1（2**n）最快：O(1)，瞬間完成。")
    print("  * 方法 2b、方法 3 都只要 O(n) 次呼叫，n=100 毫無壓力。")
    print("  * 方法 2a 是 O(2^n)，n=100 需 2^101-1 次呼叫，根本跑不完。")


if __name__ == "__main__":
    main()
