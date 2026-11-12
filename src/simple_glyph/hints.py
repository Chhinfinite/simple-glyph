"""Stroke hint parsing.

A hint file is deliberately small and human-editable.  It contains one
ordered list of waypoints per stroke; the waypoints only need to land near the
ink skeleton.  The final geometry is traced on the skeleton, not through the
waypoints directly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

Point = Tuple[float, float]


@dataclass
class Hint:
    id: str
    label: str
    waypoints: List[Point]
    color: str = "#111111"
    label_at: Optional[Point] = None
    max_width: Optional[float] = None

    def __post_init__(self) -> None:
        if len(self.waypoints) < 2:
            raise ValueError(f"stroke {self.id!r}: needs at least 2 waypoints")
        self.waypoints = [(float(x), float(y)) for x, y in self.waypoints]
        if self.label_at is not None:
            self.label_at = (float(self.label_at[0]), float(self.label_at[1]))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Hint":
        label_at = data.get("label_at")
        return cls(
            id=str(data["id"]),
            label=str(data.get("label", data["id"])),
            waypoints=[tuple(p) for p in data["waypoints"]],
            color=str(data.get("color", "#111111")),
            label_at=tuple(label_at) if label_at is not None else None,
            max_width=float(data["max_width"]) if "max_width" in data else None,
        )


@dataclass
class HintSet:
    character: str
    strokes: List[Hint] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.strokes) < 1:
            raise ValueError("hint set needs at least one stroke")
        ids = [s.id for s in self.strokes]
        if len(ids) != len(set(ids)):
            raise ValueError("stroke ids must be unique")


def load_hints(path: str | Path) -> HintSet:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return HintSet(character="", strokes=[Hint.from_dict(x) for x in data])
    strokes = data.get("strokes", data.get("hints"))
    if not isinstance(strokes, list):
        raise ValueError("hint JSON must contain a 'strokes' list")
    return HintSet(
        character=str(data.get("character", "")),
        strokes=[Hint.from_dict(x) for x in strokes],
    )
