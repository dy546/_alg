# iterative3.py
"""
Exercise Implementation using iter_framework.py
Problem: Compute sqrt(S) for S = 612 using Heron's / Newton-Raphson Iteration.
"""

import math
from iter_framework import iterative_solver

def solve_square_root(S: float, initial_guess: float = 1.0) -> None:
    """
    Computes sqrt(S) using Heron's iterative method integrated with iter_framework.
    """
    print(f"Solving sqrt({S}) using Fixed-Point Iterative Framework...\n")

    # Define update rule g(x) = 0.5 * (x + S / x)
    def heron_update(x: float) -> float:
        return 0.5 * (x + S / x)

    # Invoke generic framework engine
    result = iterative_solver(
        update_func=heron_update,
        x0=initial_guess,
        tol=1e-10,
        max_iter=50,
        error_type="absolute",
        verbose=True
    )

    # Verification against standard library math.sqrt
    exact_val = math.sqrt(S)
    calc_val = result["solution"]
    diff = abs(calc_val - exact_val)

    print("=== Exercise Results Summary ===")
    print(f"Target Value S   : {S}")
    print(f"Calculated Root  : {calc_val:.10f}")
    print(f"Exact Root (math): {exact_val:.10f}")
    print(f"Absolute Diff    : {diff:.10e}")
    print(f"Total Iterations : {result['iterations']}")
    print(f"Convergence Status: {result['converged']}")

if __name__ == "__main__":
    # Example: Calculate sqrt(612) with an initial guess x0 = 10.0
    solve_square_root(S=612.0, initial_guess=10.0)