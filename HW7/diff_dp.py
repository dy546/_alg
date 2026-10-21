"""Approach 1: LCS-based file diff using DYNAMIC PROGRAMMING.

Idea
----
Treat each file as a sequence of lines.  The lines the two files have
in common, in order, form their *longest common subsequence* (LCS).
Everything in A that is not part of the LCS must be deleted, and
everything in B that is not part of the LCS must be inserted, so a
shortest edit script is:

    LCS(A, B)  ->  lines kept ('common')
    A \\ LCS    ->  lines deleted
    B \\ LCS    ->  lines inserted

The LCS is computed with the classic DP recurrence.  ``dp[i][j]`` is the
length of the LCS of the prefixes ``A[:i]`` and ``B[:j]``:

    dp[0][j] = 0                          for all j   (empty A)
    dp[i][0] = 0                          for all i   (empty B)
    dp[i][j] = dp[i-1][j-1] + 1           if A[i-1] == B[j-1]
    dp[i][j] = max(dp[i-1][j], dp[i][j-1]) otherwise

The table has optimal substructure (each cell depends only on its three
neighbours) and overlapping subproblems (prefix comparisons are reused),
which is exactly what makes it dynamic programming.  After the table is
filled we walk backwards from ``dp[n][m]`` to recover the script.

Complexity (n = lines in A, m = lines in B)
-------------------------------------------
Time:  O(n*m)   -- every pair of prefixes is compared exactly once,
                  no matter how similar the files are.
Space: O(n*m)   -- the whole table is kept for backtracking.
"""

from diff_format import render_unified_text

__all__ = ['diff_dp', 'lcs_table', 'backtrack', 'diff_files_dp']


def lcs_table(a, b):
    """Build the ``(n+1) x (m+1)`` LCS DP table."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        ai = a[i - 1]
        row_prev, row_cur = dp[i - 1], dp[i]
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                row_cur[j] = row_prev[j - 1] + 1
            elif row_prev[j] >= row_cur[j - 1]:
                row_cur[j] = row_prev[j]
            else:
                row_cur[j] = row_cur[j - 1]
    return dp


def backtrack(a, b, dp):
    """Recover one optimal edit script by walking the DP table backwards.

    Tie-breaking note: when both ``dp[i-1][j]`` and ``dp[i][j-1]`` work,
    we prefer the *delete*; any tie-break yields an equally minimal
    script, only the order of operations changes.
    """
    ops = []
    i, j = len(a), len(b)
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            ops.append(('common', a[i - 1]))
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            ops.append(('delete', a[i - 1]))
            i -= 1
        else:
            ops.append(('insert', b[j - 1]))
            j -= 1
    while i > 0:                      # leftover lines of A
        ops.append(('delete', a[i - 1]))
        i -= 1
    while j > 0:                      # leftover lines of B
        ops.append(('insert', b[j - 1]))
        j -= 1
    ops.reverse()
    return ops


def diff_dp(a, b):
    """Return ``(edit_script, edit_distance)`` for line sequences a and b.

    ``edit_distance`` D = number of insertions + deletions in the script
    (= n + m - 2 * LCS length), the minimum possible.
    """
    dp = lcs_table(a, b)
    ops = backtrack(a, b, dp)
    d = sum(1 for tag, _ in ops if tag != 'common')
    return ops, d


def diff_files_dp(path_a, path_b, context=3):
    """Diff two files (given by path) with the DP approach.

    Returns the unified diff as a single string.
    """
    with open(path_a, encoding='utf-8') as f:
        a = f.read().splitlines()
    with open(path_b, encoding='utf-8') as f:
        b = f.read().splitlines()
    ops, _ = diff_dp(a, b)
    return render_unified_text(ops, path_a, path_b, context=context)
