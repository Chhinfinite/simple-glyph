from __future__ import annotations

import numpy as np

from simple_glyph.models import Glyph, Stroke


def test_glyph_roundtrip():
    glyph = Glyph(
        character="测",
        canvas=(100, 120),
        strokes=[
            Stroke("1", "横", np.array([[10.0, 20.0], [60.0, 25.0]]), "#c62828"),
            Stroke("2", "竖", np.array([[30.0, 5.0], [35.0, 90.0]]), "#1565c0", label_at=(40, 40)),
        ],
        source={"image_size": [100, 120]},
    )
    data = glyph.to_dict()
    again = Glyph.from_dict(data)
    assert again.character == "测"
    assert again.canvas == (100, 120)
    assert len(again.strokes) == 2
    assert np.allclose(again.strokes[0].points, glyph.strokes[0].points)
    assert again.strokes[1].label_at == (40.0, 40.0)
    assert again.strokes[0].length > 0


def test_unique_stroke_ids_rejected():
    import pytest

    with pytest.raises(ValueError):
        Glyph(
            character="x",
            canvas=(10, 10),
            strokes=[
                Stroke("1", "a", np.array([[0.0, 0.0], [1.0, 1.0]])),
                Stroke("1", "b", np.array([[1.0, 0.0], [2.0, 1.0]])),
            ],
        )
