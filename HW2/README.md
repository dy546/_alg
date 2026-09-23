# HW2: Solving Recurrence Equations

Solve the following recurrence equations and determine the complexity of the
corresponding algorithms, either as an exact number or in Big O notation.

## The four recurrences

| # | Recurrence | Base case |
|---|------------|-----------|
| 1 | `T(n) = T(n-1) + 8` | `T(1) = 1` |
| 2 | `T(n) = 2*T(n-1) + 9` | `T(1) = 1` |
| 3 | `T(n) = 2*T(n/2) + 1` | `T(1) = 1` |
| 4 | `T(n) = T(n/2) + 1` | `T(1) = 1` |

## Solutions

### 1. T(n) = T(n-1) + 8, T(1) = 1

Unroll:

```
T(n) = T(n-1) + 8
     = T(n-2) + 8 + 8
     = ...
     = T(1) + 8(n-1)
     = 1 + 8(n-1)
```

**T(n) = 8n - 7**, e.g. T(10) = 73, T(100) = 793.

Complexity: **O(n)** — linear.

### 2. T(n) = 2*T(n-1) + 9, T(1) = 1

Unroll:

```
T(n) = 2*T(n-1) + 9
     = 2*(2*T(n-2) + 9) + 9
     = 4*T(n-2) + 2*9 + 9
     = ...
     = 2^(n-1)*T(1) + 9*(2^(n-2) + ... + 2 + 1)
     = 2^(n-1) + 9*(2^(n-1) - 1)
```

**T(n) = 10·2^(n-1) - 9**, e.g. T(10) = 5,111, T(20) = 5,242,871.

Complexity: **O(2^n)** — exponential.

### 3. T(n) = 2*T(n/2) + 1, T(1) = 1 (n = 2^k)

Unroll k = log2(n) levels:

```
T(n) = 2*T(n/2) + 1
     = 2*(2*T(n/4) + 1) + 1
     = 4*T(n/4) + 2 + 1
     = ...
     = n*T(1) + (n/2 + n/4 + ... + 2 + 1)
     = n + (n - 1)
```

**T(n) = 2n - 1**, e.g. T(1024) = 2,047.

Complexity: **O(n)** — linear (Master theorem case 1).

### 4. T(n) = T(n/2) + 1, T(1) = 1 (n = 2^k)

Unroll k = log2(n) levels, adding 1 each time:

```
T(n) = T(n/2) + 1
     = T(n/4) + 2
     = ...
     = T(1) + log2(n)
```

**T(n) = log2(n) + 1**, e.g. T(1024) = 11.

Complexity: **O(log n)** — logarithmic.

## Summary table

| Recurrence | Closed form | Big O |
|------------|-------------|-------|
| `T(n) = T(n-1) + 8` | `8n - 7` | O(n) |
| `T(n) = 2*T(n-1) + 9` | `10*2^(n-1) - 9` | O(2^n) |
| `T(n) = 2*T(n/2) + 1` | `2n - 1` | O(n) |
| `T(n) = T(n/2) + 1` | `log2(n) + 1` | O(log n) |

## Files

| File | Contents |
|------|----------|
| `recurrence.py` | The four recurrences implemented recursively, plus closed-form functions for verification |
| `main.py` | Main program: correctness check, solutions, complexity table, benchmark |
| `README.md` | This document |

## How to run

```bash
cd HW2
python3 main.py
```

The output shows:

1. **Correctness check** — each recursive implementation is compared against
   its closed form for a range of `n` values.
2. **Solutions** — the closed form and sample values for each recurrence.
3. **Complexity table** — closed form and Big O for all four.
4. **Benchmark** — timing of each recurrence, showing linear, exponential,
   linear, and logarithmic growth respectively.

## Notes

- Recurrences 3 and 4 use `n // 2` and assume `n` is a power of 2 so that the
  division is exact.
- Recurrence 2 grows so fast that the benchmark only goes up to n = 25;
  each additional n doubles the number of recursive calls (2^(n-1) - 1 calls).
