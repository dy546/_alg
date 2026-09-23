# Boolean Satisfiability (SAT) via Truth Table

Gemini Conversation Link : https://share.gemini.google/0Z7jfGu4ootg

## Overview

`Boolean_Satisfiability.py` solves Boolean Satisfiability (SAT) problems using
brute-force truth-table enumeration. Given a set of Boolean variables and a
propositional formula, it evaluates the formula under **every possible truth
assignment** (all 2^N combinations) and reports whether the formula is
**SATISFIABLE** or **UNSATISFIABLE**.

This is the most straightforward and complete approach to SAT: it never misses
a solution, but it scales exponentially (2^N rows for N variables), so it is
only practical for small numbers of variables.

## How It Works

The core function is `solve_sat_truth_table(variables, formula_str)`.

### 1. Input Validation

Before building the table, the formula string is parsed with Python's `ast`
module (`ast.parse(formula_str, mode="eval")`). The parse tree is walked to
collect every `Name` node — i.e., every variable referenced in the formula.
The function then checks:

- **Syntax**: if the formula is not valid Python, it prints
  `Error: invalid formula syntax: ...` and returns without printing a table.
- **Variables**: if the formula references any name not present in
  `variables`, it prints
  `Error: formula references variable(s) not in [...]` and returns.

This guarantees the evaluation step later can never crash with a `NameError`
mid-table.

### 2. Truth-Table Generation

For `N` variables, `itertools.product([False, True], repeat=N)` generates all
2^N combinations in a systematic order (each variable flips from `False` to
`True` in right-to-left binary counting order). Each combination is zipped
with the variable names into an assignment dictionary, e.g.:

```python
{"A": False, "B": True, "C": False}
```

### 3. Formula Evaluation

The formula string is evaluated under each assignment using:

```python
bool(eval(formula_str, {}, assignment))
```

`eval` is passed an **empty globals dict** and the assignment as locals, so
the formula can only see the variables in the assignment — no builtins or
imports are exposed. The result is coerced to `bool` and stored as the row's
`Result` column.

### 4. Output

The function prints, in order:

1. The formula being tested.
2. A header row with each variable plus a `Result` column, followed by a
   separator line whose width matches the header.
3. One row per assignment (` T ` / ` F ` per variable and for the result).
4. A summary line: `SATISFIABLE (N solution(s) found)` or `UNSATISFIABLE`.
5. If satisfiable, each satisfying assignment is listed as
   `A=False, B=True, ...`.

## Function Signature

```python
solve_sat_truth_table(variables, formula_str)
```

| Parameter     | Type      | Description                                            |
|---------------|-----------|--------------------------------------------------------|
| `variables`   | `list`    | Variable names, e.g. `["A", "B", "C"]`                 |
| `formula_str` | `str`     | Python boolean expression, e.g. `"(A or B) and (not A or C)"` |

Returns `None`; all results are printed to stdout.

## Formula Syntax

The formula is a plain Python boolean expression using the listed variable
names plus the standard operators:

| Operator      | Python syntax |
|---------------|---------------|
| AND           | `and`         |
| OR            | `or`          |
| NOT           | `not`         |

Examples:

- `"(A or B) and (not A or C) and (not B or not C)"`
- `"A and not A"`
- `"A or B or C"`

## Example Output

```
Formula: (A or B) and (not A or C) and (not B or not C)

 A  |  B  |  C  | Result
------------------------
 F  |  F  |  F  |   F
 F  |  F  |  T  |   F
 F  |  T  |  F  |   T
 F  |  T  |  T  |   F
 T  |  F  |  F  |   F
 T  |  F  |  T  |   T
 T  |  T  |  F  |   F
 T  |  T  |  T  |   F
------------------------
Status: SATISFIABLE (2 solution(s) found)

  Solution 1: A=False, B=True, C=False
  Solution 2: A=True, B=False, C=True
```

## Running the Code

```bash
python3 Boolean_Satisfiability.py
```

This runs two built-in demonstrations:

1. **Test Case 1** — `(A or B) and (not A or C) and (not B or not C)`:
   satisfiable with 2 solutions.
2. **Test Case 2** — `A and not A`: a contradiction, reported UNSATISFIABLE.

The function can also be imported and called directly:

```python
from Boolean_Satisfiability import solve_sat_truth_table
solve_sat_truth_table(["A", "B"], "(A or B) and (not A or not B)")
```

## Behavior and Edge Cases

| Case                                     | Behavior                                       |
|------------------------------------------|------------------------------------------------|
| Satisfiable formula                      | Prints table + count + all solutions           |
| Unsatisfiable formula (contradiction)    | Prints table + `UNSATISFIABLE`                 |
| Tautology (e.g. `A or not A`)            | Every row is ` T `; all assignments listed     |
| Formula references undeclared variable   | Error message printed, no table                |
| Invalid Python syntax in formula         | Error message printed, no table                |
| Empty `variables` list with `"True"`     | Single row (2^0 = 1), SATISFIABLE              |
| Lowercase names (e.g. `["a"]`, `"a"`)    | Works; variable names are case-sensitive       |

## Complexity

- **Time**: O(2^N) evaluations, where N is the number of variables.
- **Space**: O(2^N) in the worst case (all assignments satisfying, e.g. a
  tautology), since every solution is stored in `satisfying_assignments`.

## Limitations

- Exponential runtime makes the function impractical beyond roughly 20
  variables (2^20 = ~1 million rows).
- Formulas must be valid Python expressions restricted to the provided
  variable names; only `and`, `or`, and `not` are meaningful for SAT.
