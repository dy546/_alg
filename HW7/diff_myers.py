"""Approach 2: Myers' greedy shortest-edit-script algorithm (NON-DP).

Idea
----
Instead of filling an ``n x m`` table, Myers (1986) views the problem as
a shortest path in the *edit graph*: a grid of ``(x, y)`` points where
``x`` indexes lines of A and ``y`` indexes lines of B.

    * a horizontal edge  (x, y) -> (x+1, y)   means "delete A[x]"
    * a vertical edge    (x, y) -> (x, y+1)   means "insert B[y]"
    * diagonal edges     (x, y) -> (x+1, y+1) are FREE and exist
      wherever A[x] == B[y]  ("snakes")

A shortest path from (0, 0) to (n, m) is a minimum edit script.

The algorithm does a greedy breadth-first search *by edit distance*:
for d = 0, 1, 2, ... it finds, for every diagonal ``k = x - y``, the
furthest point reachable with exactly ``d`` edits, storing just one
number ``v[k]`` per diagonal (the furthest x).  Reaching the goal at
sweep ``d`` proves the edit distance is exactly ``d``.  Because each
sweep only looks at diagonals ``-d, -d+2, ..., d`` and diagonal matches
are consumed for free, the work is proportional to ``(n + m) * D`` where
``D`` is the final edit distance -- small for *similar* files, which is
the case that matters in practice.  This is the algorithm behind GNU
``diff`` and ``git diff``.

Complexity (n = lines in A, m = lines in B, D = edit distance)
--------------------------------------------------------------
Time:  O((n+m) * D)  -- D+1 sweeps, each visiting ~D diagonals plus the
      snake matches; near-linear when the files are similar (D small).
      Worst case (files share nothing) D ~ n+m and it degrades to
      O((n+m)^2), like the DP table.
Space: O((n+m) * D)  -- one V-array of 2(n+m)+1 entries plus a snapshot
      of it per sweep, kept for backtracking.  (The forward pass alone
      is O(n+m); Myers' divide-and-conquer refinement removes the trace
      to get O(n+m) total.)
"""

__all__ = ['myers_diff', 'diff_files_myers']

from diff_format import render_unified_text


def myers_diff(a, b):
    """Return ``(edit_script, edit_distance)`` for line sequences a and b."""
    n, m = len(a), len(b)
    max_d = n + m
    offset = max_d + 1        # diagonal k is stored at index k + offset

    # v[k + offset] = furthest x reachable on diagonal k so far.
    # One extra zero slot on each side acts as the "unreachable diagonal"
    # sentinel and keeps every read in bounds (needed for the n = m = 0
    # corner case, where diagonal -d+1 would otherwise fall off the end).
    v = [0] * (2 * max_d + 3)
    trace = []                # snapshot of v before each sweep (backtracking)

    d_found = None
    for d in range(max_d + 1):
        trace.append(v[:])
        # Diagonals step by 2: with exactly d edits, x - y has the
        # same parity as d.
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[offset + k - 1] < v[offset + k + 1]):
                # arrive by moving DOWN from diagonal k+1 (insert a B line)
                x = v[offset + k + 1]
            else:
                # arrive by moving RIGHT from diagonal k-1 (delete an A line)
                x = v[offset + k - 1] + 1
            y = x - k
            # Snake: extend for free while lines match.
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            v[offset + k] = x
            if x >= n and y >= m:      # reached the goal with d edits
                d_found = d
                break
        if d_found is not None:
            break

    ops = _backtrack(trace, d_found, a, b)
    return ops, d_found


def _backtrack(trace, d_found, a, b):
    """Reconstruct the edit script from the saved V-array snapshots.

    At sweep ``d`` the decision rule is the mirror image of the forward
    pass, but applied to the *pre-sweep* snapshot ``trace[d]`` (this is
    valid because diagonals k-1 and k+1 are never touched inside sweep d
    itself -- the loop steps by 2).
    """
    n, m = len(a), len(b)
    offset = n + m + 1
    x, y = n, m
    ops = []
    for d in range(d_found, 0, -1):
        v = trace[d]
        k = x - y
        if k == -d or (k != d and v[offset + k - 1] < v[offset + k + 1]):
            prev_k = k + 1          # the previous move was DOWN (insert)
        else:
            prev_k = k - 1          # the previous move was RIGHT (delete)
        prev_x = v[offset + prev_k]
        prev_y = prev_x - prev_k
        # Walk the snake backwards: diagonal moves are common lines.
        while x > prev_x and y > prev_y:
            ops.append(('common', a[x - 1]))
            x -= 1
            y -= 1
        # Exactly one non-diagonal step remains to undo.
        if x == prev_x:             # down -> line B[prev_y] was inserted
            ops.append(('insert', b[prev_y]))
        else:                       # right -> line A[prev_x] was deleted
            ops.append(('delete', a[prev_x]))
        x, y = prev_x, prev_y
    # The leading snake from (0, 0).
    while x > 0 and y > 0:
        ops.append(('common', a[x - 1]))
        x -= 1
        y -= 1
    ops.reverse()
    return ops


def diff_files_myers(path_a, path_b, context=3):
    """Diff two files (given by path) with Myers' algorithm.

    Returns the unified diff as a single string.
    """
    with open(path_a, encoding='utf-8') as f:
        a = f.read().splitlines()
    with open(path_b, encoding='utf-8') as f:
        b = f.read().splitlines()
    ops, _ = myers_diff(a, b)
    return render_unified_text(ops, path_a, path_b, context=context)
