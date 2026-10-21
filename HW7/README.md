# HW7: File Diff — Dynamic Programming vs. Myers' Algorithm (non-DP)

Compare two files line by line and report the differences: **`diff`**.

The same problem is solved twice, once with **dynamic programming** and once with a
**non-DP** algorithm (Myers' greedy edit-graph search):

| Approach | File | Type |
|---|---|---|
| LCS dynamic programming | [`diff_dp.py`](diff_dp.py) | dynamic programming |
| Myers' algorithm | [`diff_myers.py`](diff_myers.py) | non-DP (greedy BFS on an edit graph) |
| Shared unified-diff renderer | [`diff_format.py`](diff_format.py) | helper |
| CLI, examples, benchmark | [`main.py`](main.py), [`examples/`](examples/) | runner |

---

## 1. Problem statement

Given two files `A` and `B` (as sequences of lines), find the **shortest edit
script** that turns `A` into `B`, using only two operations:

* **delete** a line of `A`
* **insert** a line of `B`

Every unchanged line is kept in place, so a script is fully described by a list of
`(tag, line)` pairs:

| tag | meaning |
|---|---|
| `common` | the line appears unchanged in both files |
| `delete` | the line exists only in `A` |
| `insert` | the line exists only in `B` |

The number of `insert` + `delete` operations is the **edit distance** `D`.
A script with the smallest possible `D` is an *optimal diff*. (Real diff tools
also count a "replace" as delete+insert; changing one line costs 2 edits.)

`A` and `B` share `LCS(A, B)` lines in order (their *longest common
subsequence*), so the optimal `D` is

```
D = n + m - 2 * LCS(A, B)        n = |A|, m = |B|
```

Both implementations below compute the same optimal `D` and are cross-checked
against each other (and against Python's `difflib`) by `main.py`.

---

## 2. Approach 1 — Longest Common Subsequence, Dynamic Programming

### Principle

`dp[i][j]` = length of the LCS of the prefixes `A[:i]` and `B[:j]`.
The recurrence looks at the last line of each prefix:

```
dp[0][j] = 0
dp[i][0] = 0
dp[i][j] = dp[i-1][j-1] + 1                if A[i-1] == B[j-1]
dp[i][j] = max(dp[i-1][j], dp[i][j-1])     otherwise
```

This is dynamic programming because the problem has:

* **optimal substructure** — the LCS of two prefixes is built from the LCS of
  smaller prefixes,
* **overlapping subproblems** — `dp[i-1][j]`, `dp[i][j-1]`, `dp[i-1][j-1]`
  are each reused by several cells.

After filling the `(n+1) × (m+1)` table, we **backtrack** from `dp[n][m]` to
recover the script: a diagonal step keeps a line (`common`), an up step is an
`insert`, a left step is a `delete`.

### Worked example

`A = ["a", "b", "c"]`, `B = ["a", "c", "d"]`

```
        ""   a    c    d
  ""    0    0    0    0
  a     0    1    1    1
  b     0    1    1    1
  c     0    1    2    2      <- LCS length = 2 ("a", "c")
```

Backtracking from `dp[3][3]` (preferring "up" on ties):

```
(3,3): A[2]="c" ≠ B[2]="d", dp[2][3]=1 < dp[3][2]=2  -> insert "d"
(3,2): A[2]="c" == B[1]="c"                            -> common "c"
(2,1): A[1]="b" ≠ B[0]="a", dp[1][1]=1 ≥ dp[2][0]=0   -> delete "b"
(1,1): A[0]="a" == B[0]="a"                            -> common "a"
```

Script: `common a, delete b, common c, insert d`  →  `D = 2` ✓

### Complexity (n = lines in A, m = lines in B)

* **Time: O(n·m)** — every prefix pair is compared exactly once, *always*,
  regardless of how similar the files are.
* **Space: O(n·m)** — the whole table is kept for backtracking
  (a row-by-row version can reduce it to O(m), but loses backtracking;
  Hirschberg's divide-and-conquer restores backtracking in O(n+m) space at
  the price of doubling the time).

Simple, predictable, guaranteed minimal — but quadratic time **and** memory,
which is fatal for large files (100k lines → 10¹⁰ table cells).

---

## 3. Approach 2 — Myers' Algorithm (non-DP)

### Principle: shortest path in the edit graph

Myers (1986) models the problem as a grid of `(x, y)` points, `x` indexing `A`,
`y` indexing `B`:

* **horizontal edge** `(x,y) → (x+1,y)` = delete `A[x]`
* **vertical edge** `(x,y) → (x,y+1)` = insert `B[y]`
* **diagonal edge** `(x,y) → (x+1,y+1)` = free move, exists only where
  `A[x] == B[y]` (a "snake")

A path from `(0,0)` to `(n,m)` is an edit script; a **shortest** path is an
optimal diff.

Instead of tabulating every cell (DP), Myers does a **greedy breadth-first
search by edit distance**: for `d = 0, 1, 2, …` it finds, for every diagonal
`k = x − y`, the *furthest* point reachable with exactly `d` edits, storing one
number `v[k]` per diagonal. The moment some path reaches `(n, m)` at sweep `d`,
`D = d` is proven. The greedy rule is: to enter diagonal `k`, come from the
diagonal that is furthest along (`v[k−1] + 1` moving right, or `v[k+1]` moving
down), then slide along the snake for free.

### Worked example (same input as above)

`A = ["a", "b", "c"]`, `B = ["a", "c", "d"]` — diagonals exist at `(0,0)` (`a==a`)
and `(2,1)` (`c==c`).

```
d=0  k=0: (0,0) ->snake-> (1,1)                          v[0]=1
d=1  k=1: right from (1,1) -> (2,1)  [delete "b"]
          ->snake-> (3,2)                                v[1]=3   (not at goal)
d=2  k=0: down  from (3,2) -> (3,3)  [insert "d"]        v[0]=3   (x≥3,y≥3 → DONE)
```

Recovered path: `common "a", delete "b", common "c", insert "d"` → `D = 2`,
identical to the DP result.

### Complexity (n = lines in A, m = lines in B, D = edit distance)

* **Time: O((n+m)·D)** — `D+1` sweeps, each touching ~`D` diagonals plus the
  (disjoint) snake matches, so snakes cost at most `n+m` per sweep.
  When files are *similar* (small `D`, the usual case), this is nearly linear;
  in the worst case (`D ≈ n+m`) it degrades to O((n+m)²), like the DP table.
* **Space: O((n+m)·D)** in this implementation — one `V` array of `2(n+m)+3`
  entries plus a snapshot per sweep, kept for backtracking. The forward pass
  alone is O(n+m); Myers' divide-and-conquer refinement removes the trace to
  reach O(n+m) total space (with recomputation).

This is the algorithm family behind GNU `diff` and `git diff`.

---

## 4. Comparison

| | **LCS DP** | **Myers** |
|---|---|---|
| Strategy | fill the whole `n×m` table | greedy BFS over diagonals, stop at distance `D` |
| Time | **O(n·m)** always | **O((n+m)·D)** → near-linear for similar files, O(n·m) worst case |
| Time, identical files (`D=0`) | O(n·m) | **O(n+m)** |
| Time, disjoint files (`D≈n+m`) | O(n·m) | ~O(n·m) with a worse constant |
| Space | O(n·m) | O((n+m)·D) with trace (O(n+m) forward-only) |
| Difficulty | simple, textbook | subtle (parity of diagonals, backtracking) |
| Best when | teaching, tiny inputs, guaranteed bound | real-world diffing of large, mostly-similar files |

**Key insight:** DP's cost depends only on the file sizes; Myers' cost depends
on how *different* the files are. Real files being edited are almost always
nearly identical, so Myers wins by orders of magnitude — the benchmark below
makes this concrete. DP only pays off when the inputs are small or when the
files are completely unrelated (and even then, by a small constant).

### Benchmark (run with `python3 main.py --benchmark`)

"changed" = probability that a line differs between the two files.

```
 lines  changed  D edits     DP(s)  Myers(s)  speedup
   500     0.00       10    0.027s    0.000s    60.9x
   500     0.05       52    0.023s    0.001s    35.5x
   500     0.50      483    0.024s    0.080s     0.3x
   500     1.00     1000    0.022s    0.180s     0.1x
  1000     0.00       29    0.115s    0.000s   245.3x
  1000     0.05      135    0.126s    0.006s    21.5x
  1000     0.50     1029    0.135s    0.269s     0.5x
  1000     1.00     2000    0.116s    0.714s     0.2x
  2000     0.00       41    0.507s    0.004s   124.3x
  2000     0.05      252    0.528s    0.018s    29.5x
  2000     0.50     2061    0.526s    1.114s     0.5x
```

* DP time is flat for a given `n` — it always fills `n·m` cells.
* Myers time tracks `D`: up to **245× faster** on near-identical files, and it
  only falls behind when files are almost entirely different.

---

## 5. How to run

```bash
cd HW7

python3 main.py                       # diff examples/a.txt vs examples/b.txt
                                      # with BOTH algorithms + cross-check
python3 main.py --algo dp             # dynamic programming only
python3 main.py --algo myers          # Myers' algorithm only
python3 main.py --file1 X --file2 Y   # diff any two files
python3 main.py --benchmark           # timing comparison on synthetic files
```

### Sample output (`python3 main.py --algo myers`)

```
=== Myers' Algorithm (non-DP) ===
edit distance D = 9 (insertions + deletions)
--- examples/a.txt
+++ examples/b.txt
@@ -1,14 +1,17 @@
 def greet(name):
-    message = "Hello, " + name + "!"
+    message = "Hi, " + name + "!"
     print(message)
     return message
 
+def farewell(name):
+    print("Goodbye, " + name + "!")
 
+
 def main():
-    names = ["Alice", "Bob", "Charlie"]
+    names = ["Alice", "Bob", "Charlie", "Dana"]
     for name in names:
         greet(name)
-    print("Done.")
+    print("All done.")
 
 
 if __name__ == "__main__":
```

`python3 main.py` runs **both** algorithms and ends with a cross-check:

```
--- Cross-check ---
[OK] both scripts are valid and minimal (D = 9)
[INFO] outputs differ only in tie-breaking; both are minimal
```

(The two algorithms always agree on `D`; their printed hunk order may differ
when ties exist in the optimal script — e.g. delete-before-insert vs.
insert-before-delete — but both scripts are minimal.)

---

## 6. Correctness testing

`main.py` verifies every script by

1. **reconstruction** — replaying the script against `A` must reproduce `B`
   exactly (catches wrong/misordered operations), and
2. **minimality cross-check** — Myers' `D` must equal the DP's `D`, which is
   provably `n + m − 2·LCS`, with an extra sanity bound from
   `difflib.SequenceMatcher`.

Additionally the implementations were fuzz-tested on 20 000+ random small
inputs (including empty files, identical files, and disjoint files).

---

## 7. References

* E. W. Myers, *An O(ND) Difference Algorithm and Its Variations*,
  Algorithmica 1(2), 1986.
* W. Miller, E. W. Myers, *A File Comparison Program*, Software—Practice and
  Experience 15(11), 1985.
* Cormen, Leiserson, Rivest, Stein, *Introduction to Algorithms* — the LCS
  dynamic-programming formulation (§15.4).
* Python `difflib` documentation (used only as an independent reference).
