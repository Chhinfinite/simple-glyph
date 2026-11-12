from __future__ import annotations

from pathlib import Path

from simple_glyph.trace import trace_glyph


def test_demo_trace():
    root = Path(__file__).resolve().parents[1]
    image = root / "examples" / "input" / "央.png"
    hints = root / "examples" / "hints" / "央.json"
    glyph = trace_glyph(image, hints, character="央")
    assert glyph.canvas == (800, 720)
    assert len(glyph.strokes) == 5
    assert [s.id for s in glyph.strokes] == ["1", "2", "3", "4", "5"]
    for stroke in glyph.strokes:
        assert stroke.length > 50
        assert stroke.points.min() >= 0
        assert stroke.points[:, 0].max() <= 800
        assert stroke.points[:, 1].max() <= 720
