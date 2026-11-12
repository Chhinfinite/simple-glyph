"""Skeleton graph tracing.

The algorithm is intentionally simple and inspectable:

1. binarise the ink;
2. compute a medial axis / skeleton;
3. snap each manual waypoint to the nearest skeleton pixel;
4. find a shortest path between consecutive snapped points on the 8-neighbour
   skeleton graph;
5. smooth and resample the resulting polyline.

This is not a general automatic stroke segmenter.  The manual waypoints are
what make the decomposition reliable; the graph supplies the actual geometry.
"""

from __future__ import annotations

import math
from collections import deque
from typing import Iterable, List, Sequence, Set, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter1d
from skimage.morphology import medial_axis, skeletonize

from .hints import Hint, HintSet
from .models import Stroke

Node = Tuple[int, int]
Point = Tuple[float, float]


class TraceError(RuntimeError):
    """Raised when a stroke cannot be traced on the skeleton graph."""


def build_nodes(mask: np.ndarray, method: str = "medial_axis") -> Set[Node]:
    """Return the set of skeleton pixels as integer (x, y) nodes."""
    if mask.ndim != 2:
        raise ValueError("mask must be 2-D")
    if not mask.any():
        raise TraceError("ink mask is empty; check the threshold")
    if method == "medial_axis":
        skel = medial_axis(mask)
    elif method == "skeletonize":
        skel = skeletonize(mask)
    else:
        raise ValueError("method must be 'medial_axis' or 'skeletonize'")
    ys, xs = np.nonzero(skel)
    nodes = set(zip(xs.tolist(), ys.tolist()))
    if len(nodes) < 10:
        raise TraceError("skeleton is too small; check the image and threshold")
    return nodes


def nearest_node(point: Point, nodes: Iterable[Node]) -> Node:
    x, y = float(point[0]), float(point[1])
    best: Node | None = None
    best_d = math.inf
    for nx, ny in nodes:
        d = (nx - x) ** 2 + (ny - y) ** 2
        if d < best_d:
            best_d = d
            best = (nx, ny)
    if best is None:
        raise TraceError("no skeleton nodes")
    return best


def bfs_path(start: Node, end: Node, nodes: Set[Node]) -> List[Node]:
    """Shortest 8-neighbour path on the skeleton graph."""
    if start == end:
        return [start]
    q: deque[Node] = deque([start])
    prev = {start: None}
    neighbours = (
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1), (0, 1),
        (1, -1), (1, 0), (1, 1),
    )
    while q:
        cur = q.popleft()
        if cur == end:
            break
        x, y = cur
        for dx, dy in neighbours:
            nb = (x + dx, y + dy)
            if nb in nodes and nb not in prev:
                prev[nb] = cur
                q.append(nb)
    if end not in prev:
        return []
    out: List[Node] = []
    cur = end
    while cur is not None:
        out.append(cur)
        cur = prev[cur]
    return out[::-1]


def resample(points: np.ndarray, spacing: float = 2.5) -> np.ndarray:
    """Resample a polyline at approximately fixed arc-length spacing."""
    pts = np.asarray(points, dtype=np.float64)
    if len(pts) < 2:
        return pts.copy()
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(cum[-1])
    if total <= 0:
        return pts[:1].copy()
    n = max(2, int(math.ceil(total / spacing)) + 1)
    s = np.linspace(0.0, total, n)
    return np.column_stack([
        np.interp(s, cum, pts[:, 0]),
        np.interp(s, cum, pts[:, 1]),
    ])


def path_through_waypoints(waypoints: Sequence[Point], nodes: Set[Node]) -> np.ndarray:
    snapped = [nearest_node(p, nodes) for p in waypoints]
    full: List[Node] = []
    for a, b in zip(snapped[:-1], snapped[1:]):
        seg = bfs_path(a, b, nodes)
        if not seg:
            raise TraceError(f"no skeleton path {a} -> {b}; move a waypoint closer to the ink")
        if full:
            seg = seg[1:]
        full.extend(seg)
    if len(full) < 3:
        raise TraceError("skeleton path is too short")
    return np.asarray(full, dtype=np.float64)


def smooth_and_resample(
    points: np.ndarray,
    sigma: float = 2.2,
    spacing: float = 2.5,
) -> np.ndarray:
    pts = np.asarray(points, dtype=np.float64).copy()
    if len(pts) >= 4:
        pts[:, 0] = gaussian_filter1d(pts[:, 0], sigma, mode="nearest")
        pts[:, 1] = gaussian_filter1d(pts[:, 1], sigma, mode="nearest")
    return resample(pts, spacing)


def trace_strokes(
    mask: np.ndarray,
    hints: HintSet | Sequence[Hint],
    method: str = "medial_axis",
    sigma: float = 2.2,
    spacing: float = 2.5,
) -> List[Stroke]:
    """Trace every hint against the same skeleton graph."""
    hint_list = hints.strokes if isinstance(hints, HintSet) else list(hints)
    nodes = build_nodes(mask, method=method)
    strokes: List[Stroke] = []
    for hint in hint_list:
        pts = path_through_waypoints(hint.waypoints, nodes)
        pts = smooth_and_resample(pts, sigma=sigma, spacing=spacing)
        strokes.append(
            Stroke(
                id=hint.id,
                label=hint.label,
                points=pts,
                color=hint.color,
                label_at=hint.label_at,
            )
        )
    return strokes
