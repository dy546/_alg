#!/usr/bin/env python3
"""HW8: core utilities shared by all five TSP solvers.

City generation, the distance matrix, tour costs, the two local-move
operators used by the search methods (swap and 2-opt), an exhaustive
solver for tiny instances, and dependency-free SVG plotting.
"""

import itertools
import math
import os

import numpy as np

# ----------------------------------------------------------------------
# City generation
# ----------------------------------------------------------------------

def make_cities(n, seed=42, kind='uniform'):
    """Return an (n, 2) float array of city coordinates.

    kind:
      'uniform' -- uniform random points in the [0, 100]^2 square
      'circle'  -- points on a circle (the cyclic order is known optimal)
      'cluster' -- points drawn around a few Gaussian cluster centers
    """
    rng = np.random.default_rng(seed)
    if kind == 'uniform':
        pts = rng.uniform(0.0, 100.0, size=(n, 2))
    elif kind == 'circle':
        ang = rng.uniform(0.0, 2.0 * math.pi, size=n)
        pts = np.column_stack([50.0 + 50.0 * np.cos(ang),
                               50.0 + 50.0 * np.sin(ang)])
    elif kind == 'cluster':
        k = max(1, min(4, n // 8))
        centers = rng.uniform(10.0, 90.0, size=(k, 2))
        pts = np.vstack([centers[i % k] + rng.normal(0.0, 6.0, size=2)
                         for i in range(n)])
    else:
        raise ValueError(f'unknown city kind: {kind!r}')
    return pts.astype(float)


def dist_matrix(cities):
    """Euclidean distance matrix D with D[i, j] = distance(city i, city j)."""
    d = cities[:, None, :] - cities[None, :, :]
    return np.sqrt((d * d).sum(axis=2))


# ----------------------------------------------------------------------
# Tour handling
# ----------------------------------------------------------------------

def tour_length(order, D):
    """Length of a closed tour (list of city indices) under distance matrix D."""
    n = len(order)
    return float(sum(D[order[i], order[(i + 1) % n]] for i in range(n)))


def is_valid_tour(order, n):
    """True if `order` visits every city 0..n-1 exactly once."""
    return (isinstance(order, list) and len(order) == n
            and sorted(order) == list(range(n)))


def random_tour(n, seed=None):
    """A uniformly random permutation of the n cities."""
    return np.random.default_rng(seed).permutation(n).tolist()


# ----------------------------------------------------------------------
# Local moves: swap and 2-opt
# ----------------------------------------------------------------------

def swap_delta(D, order, a, b):
    """Change in tour length if the cities at positions a and b are swapped.

    Only the four edges incident to positions a and b are affected, so the
    delta is computed in O(1).  The tour is not modified.
    """
    if a == b:
        return 0.0
    if a > b:
        a, b = b, a
    n = len(order)

    def incident(a_pos, b_pos):
        # edges touching positions a_pos and b_pos, as unordered pairs
        return {(min(order[a_pos], order[(a_pos - 1) % n]),
                 max(order[a_pos], order[(a_pos - 1) % n])),
                (min(order[a_pos], order[(a_pos + 1) % n]),
                 max(order[a_pos], order[(a_pos + 1) % n])),
                (min(order[b_pos], order[(b_pos - 1) % n]),
                 max(order[b_pos], order[(b_pos - 1) % n])),
                (min(order[b_pos], order[(b_pos + 1) % n]),
                 max(order[b_pos], order[(b_pos + 1) % n]))}

    old = incident(a, b)
    order[a], order[b] = order[b], order[a]
    new = incident(a, b)
    order[a], order[b] = order[b], order[a]          # restore
    return float(sum(D[u, v] for u, v in new)
                 - sum(D[u, v] for u, v in old))


def opt2_delta(D, order, i, j):
    """Length change of a 2-opt move: reverse the segment order[i+1 .. j].

    The move removes edges (a, b) and (c, d) and adds (a, c) and (b, d):
        ... a - b ... c - d ...   ->   ... a - c ... b - d ...
    """
    n = len(order)
    a, b = order[i], order[i + 1]
    c, d = order[j], order[(j + 1) % n]
    return float(D[a, c] + D[b, d] - D[a, b] - D[c, d])


def apply_2opt(order, i, j):
    """Reverse segment order[i+1 .. j] in place."""
    order[i + 1:j + 1] = reversed(order[i + 1:j + 1])


# ----------------------------------------------------------------------
# Exact solver for tiny instances (used as a reference in tests/benchmarks)
# ----------------------------------------------------------------------

def brute_force_tsp(D):
    """Exact optimal tour by exhaustive enumeration (city 0 fixed as start).

    Only suitable for n <= 10: (n-1)! permutations.
    """
    n = len(D)
    if n > 10:
        raise ValueError('brute force is limited to n <= 10')
    best_len, best_order = None, None
    for perm in itertools.permutations(range(1, n)):
        order = (0,) + perm
        length = tour_length(order, D)
        if best_len is None or length < best_len:
            best_len, best_order = length, list(order)
    return best_order, best_len


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------

def downsample(points, keep=400):
    """Keep at most `keep` evenly spaced points of a (x, y) series."""
    if len(points) <= keep:
        return points
    k = len(points) / keep
    return [points[int(i * k)] for i in range(keep - 1)] + [points[-1]]


def format_time(t):
    if t < 1e-4:
        return f'{t * 1e6:6.0f} us'
    if t < 1.0:
        return f'{t * 1e3:5.1f} ms'
    return f'{t:5.2f} s'


# ----------------------------------------------------------------------
# Dependency-free SVG plotting
# ----------------------------------------------------------------------

DEFAULT_COLORS = {
    'greedy': '#e6194b',
    '2opt':   '#3cb44b',
    'hill':   '#4363d8',
    'sa':     '#f58231',
    'gd':     '#911eb4',
}


def _esc(text):
    return (str(text).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;'))


def write_tour_svg(cities, tours, title, out_path, size=(640, 420)):
    """Draw cities and one or more tours as SVG.

    tours: list of (label, order, color) tuples.
    """
    W, H = size
    xs, ys = cities[:, 0], cities[:, 1]
    xmin, xmax, ymin, ymax = xs.min(), xs.max(), ys.min(), ys.max()
    dx = max(xmax - xmin, 1e-9)
    dy = max(ymax - ymin, 1e-9)
    m = 30.0
    s = min((W - 2 * m) / dx, (H - 2 * m) / dy)
    cx = (W - s * (xmin + xmax)) / 2.0
    cy = (H + s * (ymin + ymax)) / 2.0

    def X(x):
        return cx + s * x

    def Y(y):
        return cy - s * y

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="sans-serif">',
             f'<rect width="{W}" height="{H}" fill="white"/>',
             f'<text x="{W / 2:.0f}" y="22" text-anchor="middle" font-size="15" '
             f'font-weight="bold">{_esc(title)}</text>']
    for x, y in cities:
        parts.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3.2" fill="#555"/>')
    for label, order, color in tours:
        pts = ' '.join(f'{X(cities[i, 0]):.1f},{Y(cities[i, 1]):.1f}'
                       for i in order)
        pts += f' {X(cities[order[0], 0]):.1f},{Y(cities[order[0], 1]):.1f}'
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                     f'stroke-width="2.2"/>')
        sx, sy = X(cities[order[0], 0]), Y(cities[order[0], 1])
        parts.append(f'<rect x="{sx - 4:.1f}" y="{sy - 4:.1f}" width="8" '
                     f'height="8" fill="{color}"/>')
    lx = 12.0
    for label, _order, color in tours:
        parts.append(f'<line x1="{lx:.0f}" y1="{H - 14}" x2="{lx + 22:.0f}" '
                     f'y2="{H - 14}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{lx + 27:.0f}" y="{H - 10}" font-size="12">'
                     f'{_esc(label)}</text>')
        lx += 27 + 7.2 * len(label) + 16
    parts.append('</svg>')
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))


def _nice_ticks(lo, hi, k=5):
    span = hi - lo
    if span <= 0:
        return [lo]
    step0 = span / k
    mag = 10.0 ** math.floor(math.log10(step0))
    for mult in (1.0, 2.0, 2.5, 5.0, 10.0):
        if step0 / mag <= mult:
            step = mult * mag
            break
    start = math.ceil(lo / step) * step
    return [start + i * step for i in range(int((hi - start) // step) + 1)]


def write_history_svg(histories, title, out_path,
                      xlabel='progress of the run (%)',
                      ylabel='tour length', size=(760, 430)):
    """Line chart of (x, y) series. Each series is rescaled to x in [0, 100].

    histories: list of (label, [(x, y), ...], color) tuples.
    """
    W, H = size
    ml, mr, mt, mb = 64.0, 18.0, 46.0, 46.0
    data = []
    ymin, ymax = float('inf'), -float('inf')
    for label, pts, color in histories:
        if len(pts) < 2:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        lo, hi = min(xs), max(xs)
        nx = [0.0 if hi <= lo else (x - lo) / (hi - lo) * 100.0 for x in xs]
        data.append((label, nx, ys, color))
        ymin = min(ymin, min(ys))
        ymax = max(ymax, max(ys))
    if not data:
        return
    if ymin == ymax:
        ymax = ymin + 1.0
    pad = (ymax - ymin) * 0.06
    ymin, ymax = ymin - pad, ymax + pad

    def X(x):
        return ml + (W - ml - mr) * x / 100.0

    def Y(y):
        return H - mb - (H - mt - mb) * (y - ymin) / (ymax - ymin)

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="sans-serif">',
             f'<rect width="{W}" height="{H}" fill="white"/>',
             f'<text x="{W / 2:.0f}" y="24" text-anchor="middle" font-size="15" '
             f'font-weight="bold">{_esc(title)}</text>']
    for tick in _nice_ticks(ymin, ymax, 5):
        y = Y(tick)
        parts.append(f'<line x1="{ml:.0f}" y1="{y:.1f}" x2="{W - mr:.0f}" '
                     f'y2="{y:.1f}" stroke="#dddddd" stroke-width="1"/>')
        parts.append(f'<text x="{ml - 8:.0f}" y="{y + 4:.1f}" text-anchor="end" '
                     f'font-size="11">{tick:.4g}</text>')
    for tick in (0, 25, 50, 75, 100):
        x = X(tick)
        parts.append(f'<text x="{x:.1f}" y="{H - mb + 16:.0f}" '
                     f'text-anchor="middle" font-size="11">{tick}</text>')
    parts.append(f'<rect x="{ml:.0f}" y="{mt:.0f}" width="{W - ml - mr:.0f}" '
                 f'height="{H - mt - mb:.0f}" fill="none" stroke="#999999"/>')
    for label, nx, ys, color in data:
        pts = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in zip(nx, ys))
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                     f'stroke-width="2"/>')
    lx = ml
    for label, _nx, _ys, color in data:
        parts.append(f'<line x1="{lx:.0f}" y1="{H - 12}" x2="{lx + 22:.0f}" '
                     f'y2="{H - 12}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{lx + 27:.0f}" y="{H - 8}" font-size="12">'
                     f'{_esc(label)}</text>')
        lx += 27 + 7.2 * len(label) + 16
    parts.append(f'<text x="{(ml + W - mr) / 2:.0f}" y="{H - 18:.0f}" '
                 f'text-anchor="middle" font-size="12">{_esc(xlabel)}</text>')
    parts.append(f'<text x="16" y="{(mt + H - mb) / 2:.0f}" text-anchor="middle" '
                 f'font-size="12" transform="rotate(-90 16 {(mt + H - mb) / 2:.0f})">'
                 f'{_esc(ylabel)}</text>')
    parts.append('</svg>')
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))
