"""Data models for simple-glyph.

A glyph is a set of ordered, open polyline strokes in image coordinates.
No fill, no closed contours: the centerline is the source of truth.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class Stroke:
    id: str
    label: str
    points: np.ndarray
    color: str = "#111111"
    label_at: Optional[Tuple[float, float]] = None

    def __post_init__(self) -> None:
        pts = np.asarray(self.points, dtype=np.float64)
        if pts.ndim != 2 or pts.shape[1] != 2:
            raise ValueError(f"stroke {self.id!r}: points must be Nx2")
        if len(pts) < 2:
            raise ValueError(f"stroke {self.id!r}: needs at least 2 points")
        self.points = pts

    @property
    def length(self) -> float:
        if len(self.points) < 2:
            return 0.0
        return float(np.linalg.norm(np.diff(self.points, axis=0), axis=1).sum())

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": self.id,
            "label": self.label,
            "color": self.color,
            "points": [[round(float(x), 2), round(float(y), 2)] for x, y in self.points],
            "length": round(self.length, 2),
        }
        if self.label_at is not None:
            data["label_at"] = [round(float(self.label_at[0]), 2), round(float(self.label_at[1]), 2)]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Stroke":
        label_at = data.get("label_at")
        if label_at is not None:
            label_at = (float(label_at[0]), float(label_at[1]))
        return cls(
            id=str(data["id"]),
            label=str(data.get("label", data["id"])),
            points=np.asarray(data["points"], dtype=np.float64),
            color=str(data.get("color", "#111111")),
            label_at=label_at,
        )


@dataclass
class Glyph:
    character: str
    canvas: Tuple[int, int]
    strokes: List[Stroke]
    source: Dict[str, Any] = field(default_factory=dict)
    schema: str = "simple-glyph/1"

    def __post_init__(self) -> None:
        w, h = int(self.canvas[0]), int(self.canvas[1])
        if w <= 0 or h <= 0:
            raise ValueError("canvas must be positive")
        self.canvas = (w, h)
        if not self.strokes:
            raise ValueError("glyph needs at least one stroke")
        ids = [s.id for s in self.strokes]
        if len(ids) != len(set(ids)):
            raise ValueError("stroke ids must be unique")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "character": self.character,
            "canvas": [int(self.canvas[0]), int(self.canvas[1])],
            "source": self.source,
            "order": [
                {"index": i, "id": s.id, "label": s.label}
                for i, s in enumerate(self.strokes, 1)
            ],
            "strokes": [s.to_dict() for s in self.strokes],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Glyph":
        canvas = data.get("canvas", [800, 720])
        if isinstance(canvas, dict):
            canvas = (canvas["width"], canvas["height"])
        return cls(
            character=str(data.get("character", "")),
            canvas=(int(canvas[0]), int(canvas[1])),
            strokes=[Stroke.from_dict(s) for s in data["strokes"]],
            source=dict(data.get("source", {})),
            schema=str(data.get("schema", "simple-glyph/1")),
        )


def save_glyph(glyph: Glyph, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(glyph.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_glyph(path: str | Path) -> Glyph:
    return Glyph.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
