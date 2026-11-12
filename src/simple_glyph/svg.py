"""SVG writers for open centerline strokes and a small reveal animation."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Optional

import numpy as np

from .models import Glyph, Stroke


def _num(value: float) -> str:
    text = f"{float(value):.2f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def path_d(points: np.ndarray, closed: bool = False) -> str:
    pts = np.asarray(points, dtype=np.float64)
    if len(pts) < 2:
        raise ValueError("a path needs at least 2 points")
    body = "M " + " L ".join(f"{_num(x)} {_num(y)}" for x, y in pts)
    return body + (" Z" if closed else "")


def _label(stroke: Stroke, index: int) -> tuple[float, float]:
    if stroke.label_at is not None:
        return stroke.label_at
    x, y = stroke.points[0]
    return float(x + 16), float(y - 16)


def centerline_svg(
    glyph: Glyph,
    colored: bool = False,
    labels: bool = False,
    animate: bool = False,
    background: Optional[str] = None,
    stroke_width: float = 3.0,
) -> str:
    """Build an SVG string.

    Static centerlines are always open paths with ``fill="none"``.  The
    optional animation uses normalized path lengths and a CSS dash animation,
    so it works in browsers without JS or external assets.
    """
    w, h = glyph.canvas
    title = f"{glyph.character} · stroke centerlines" if glyph.character else "stroke centerlines"
    desc = (
        "Open centerline paths in stroke order. "
        "No fill, no closed contours, no background by default."
    )
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f"<title>{escape(title)}</title>",
        f"<desc>{escape(desc)}</desc>",
    ]
    if background:
        parts.append(f'<rect width="{w}" height="{h}" fill="{escape(background)}"/>')

    durations: list[float] = []
    if animate:
        for stroke in glyph.strokes:
            durations.append(max(0.22, stroke.length / 360.0))
        parts.append(
            "<style>"
            "@keyframes sg-draw{to{stroke-dashoffset:0}}"
            ".sg-stroke{stroke-dasharray:1;stroke-dashoffset:1;"
            "animation:sg-draw var(--dur) ease-in-out forwards;"
            "animation-delay:var(--delay)}"
            "</style>"
        )

    parts.append(
        f'<g fill="none" stroke-linecap="round" stroke-linejoin="round" '
        f'stroke-width="{_num(stroke_width)}">'
    )
    delay = 0.08
    for i, stroke in enumerate(glyph.strokes):
        color = stroke.color if colored else "#111111"
        attrs = [
            f'id="stroke-{escape(stroke.id)}"',
            f'data-order="{i + 1}"',
            f'data-label="{escape(stroke.label)}"',
            'fill="none"',
            f'stroke="{escape(color)}"',
            f'd="{path_d(stroke.points)}"',
        ]
        if animate:
            dur = durations[i]
            attrs.append('pathLength="1"')
            attrs.append(f'class="sg-stroke" style="--dur:{dur:.2f}s;--delay:{delay:.2f}s"')
            delay += dur + 0.12
        parts.append("<path " + " ".join(attrs) + "/>")
    parts.append("</g>")

    if labels:
        parts.append(
            '<g font-family="Arial, Helvetica, sans-serif" font-size="18" '
            'font-weight="600" text-anchor="middle">'
        )
        for i, stroke in enumerate(glyph.strokes):
            x, y = _label(stroke, i)
            parts.append(
                f'<circle cx="{_num(x)}" cy="{_num(y)}" r="11" fill="#ffffff" fill-opacity="0.9"/>'
            )
            parts.append(
                f'<text x="{_num(x)}" y="{_num(y + 6)}" fill="#111111" '
                f'stroke="#ffffff" stroke-width="3" paint-order="stroke">{escape(stroke.id)}</text>'
            )
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def write_svg(svg: str, path: str | Path) -> None:
    Path(path).write_text(svg, encoding="utf-8")
