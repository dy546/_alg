# HW5

Four Python programs demonstrating recursion, iteration, higher-order functions, and symbolic differentiation.

## Files

| File | Description |
|---|---|
| `hanoi_recursive.py` | Tower of Hanoi solved with recursion |
| `hanoi_iterative.py` | Tower of Hanoi solved without recursion |
| `map_filter_reduce.py` | Custom `map`/`filter`/`reduce` and a loop-free bubble sort |
| `sym_dif.py` | Symbolic differentiation of expression trees |

## Usage

```bash
python3 hanoi_recursive.py
python3 hanoi_iterative.py
python3 map_filter_reduce.py
python3 sym_dif.py
```

## hanoi_recursive.py

Classic recursive solution using the recurrence `hanoi(n) = 2 * hanoi(n-1) + 1` moves.

- `hanoi_recursive(n, source, target, auxiliary)`
  - Moves `n-1` disks from `source` to `auxiliary`
  - Moves the largest disk from `source` to `target`
  - Moves the `n-1` disks from `auxiliary` to `target`

Time complexity: `O(2^n)`, total moves: `2^n - 1`.

## hanoi_iterative.py

Iterative solution using the alternating-move pattern and three peg stacks.

- `hanoi_iterative(n, source, target, auxiliary)`
  - For `i = 1 .. 2^n - 1`, performs the legal move between a rotating pair of pegs
  - Peg order depends on whether `n` is odd or even
  - Tracks disk stacks to ensure no larger disk is placed on a smaller one

Produces the same move sequence as the recursive version.

## map_filter_reduce.py

Recursive reimplementations of Python's built-in higher-order functions:

- `my_map(func, lst)` — applies `func` to every element
- `my_filter(func, lst)` — keeps elements where `func` returns truthy
- `my_reduce(func, lst, initializer)` — folds the list left-to-right

Built on top of these:

- `bubble_pass(arr)` — one bubble-sort pass using `my_reduce`; returns `(arr, swapped)`
- `bubble_sort_no_loops(arr)` — full bubble sort using only recursion, no `for`/`while` loops

## sym_dif.py

Differentiates an expression represented as nested tuples (`('op', u, v)`).

- `sym_diff(expr, var='x')` — returns the derivative expression (unsimplified)

Supported operators:

| Operator | Rule |
|---|---|
| `+`, `-` | `(u ± v)' = u' ± v'` |
| `*` | Product rule: `u'v + uv'` |
| `/` | Quotient rule: `(u'v - uv') / v²` |
| `^` | Power + chain rule: `n * u^(n-1) * u'` |
| `sin` | `cos(u) * u'` |
| `cos` | `-sin(u) * u'` |

Constants differentiate to `0`; the variable differentiates to `1`.

### Examples

```python
expr1 = ('+', ('*', 'x', 'x'), ('*', 3, 'x'))   # x*x + 3*x
sym_diff(expr1)  # d/dx (x*x + 3*x)

expr2 = ('*', 'x', ('sin', 'x'))                # x * sin(x)
sym_diff(expr2)  # d/dx (x * sin(x))
```
