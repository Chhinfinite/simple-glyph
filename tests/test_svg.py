from __future__ import annotations

import numpy as np

from simple_glyph.models import Glyph, Stroke
from simple_glyph.svg import centerline_svg


def _glyph():
    return Glyph(
        character="央",
        canvas=(200, 200),
        strokes=[
            Stroke("1", "竖", np.array([[50.0, 20.0], [55.0, 90.0]]), "#c62828", label_at=(40, 40)),
            Stroke("2", "横折", np.array([[50.0, 20.0], [150.0, 30.0], [150.0, 100.0]]), "#1565c0"),
        ],
    )


def test_static_svg_is_open_and_unfilled():
    svg = centerline_svg(_glyph())
    assert svg.count("<path") == 2
    assert svg.count('fill="none"') >= 2
    assert " Z" not in svg
    assert "<rect" not in svg
    assert 'id="stroke-1"' in svg


def test_colored_labels():
    svg = centerline_svg(_glyph(), colored=True, labels=True)
    assert 'stroke="#c62828"' in svg
    assert "<text" in svg
    assert ">1</text>" in svg


def test_animation_has_css_dash():
    svg = centerline_svg(_glyph(), animate=True)
    assert "@keyframes sg-draw" in svg
    assert 'pathLength="1"' in svg
    assert "sg-stroke" in svg
