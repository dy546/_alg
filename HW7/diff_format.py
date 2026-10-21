"""Shared helpers for rendering an edit script as a unified diff.

Both algorithms (``diff_dp.py`` and ``diff_myers.py``) produce the same
kind of output -- a list of ``(tag, line)`` pairs called an *edit script*:

    tag        meaning
    --------   -------------------------------------------------
    'common'   the line appears unchanged in both files
    'delete'   the line exists only in file A
    'insert'   the line exists only in file B

This module turns such a script into the familiar unified-diff format
(the one printed by ``diff -u`` and ``git diff``), so the two approaches
can be compared output-for-output.
"""


def count_prefixes(ops):
    """Prefix line counts over the script.

    Returns ``(pref_a, pref_b)`` where ``pref_a[i]`` is the number of
    file-A lines covered by ``ops[:i]`` and ``pref_b[i]`` likewise for
    file B.  Used to compute hunk line numbers.
    """
    pref_a = [0]
    pref_b = [0]
    for tag, _ in ops:
        pref_a.append(pref_a[-1] + (1 if tag in ('common', 'delete') else 0))
        pref_b.append(pref_b[-1] + (1 if tag in ('common', 'insert') else 0))
    return pref_a, pref_b


def render_unified(ops, file_a='a', file_b='b', context=3):
    """Render an edit script as a list of unified-diff lines.

    ``context`` is how many unchanged lines to print around each hunk,
    matching ``diff -u``'s default of 3.
    """
    n = len(ops)

    if all(tag == 'common' for tag, _ in ops):
        return [f'--- {file_a}',
                f'+++ {file_b}',
                '(files are identical)']

    pref_a, pref_b = count_prefixes(ops)
    changed = [i for i, (tag, _) in enumerate(ops) if tag != 'common']

    # Group nearby changes into hunks: two changes whose context windows
    # would overlap (or touch) belong to the same hunk.
    regions = []
    start = changed[0]
    prev = changed[0]
    for idx in changed[1:]:
        if idx - prev > 2 * context + 1:
            regions.append((start, prev))
            start = idx
        prev = idx
    regions.append((start, prev))

    def fmt(start, length):
        # GNU style: ",len" is omitted when the hunk covers one line.
        return str(start) if length == 1 else f'{start},{length}'

    out = [f'--- {file_a}', f'+++ {file_b}']
    for cs, ce in regions:
        hs = max(0, cs - context)
        he = min(n - 1, ce + context)
        a_start = pref_a[hs] + 1
        b_start = pref_b[hs] + 1
        a_len = pref_a[he + 1] - pref_a[hs]
        b_len = pref_b[he + 1] - pref_b[hs]

        out.append(f'@@ -{fmt(a_start, a_len)} +{fmt(b_start, b_len)} @@')
        for i in range(hs, he + 1):
            tag, line = ops[i]
            if tag == 'common':
                out.append(' ' + line)
            elif tag == 'delete':
                out.append('-' + line)
            else:  # insert
                out.append('+' + line)
    return out


def render_unified_text(ops, file_a='a', file_b='b', context=3):
    """Like :func:`render_unified` but returns a single string."""
    return '\n'.join(render_unified(ops, file_a, file_b, context))
