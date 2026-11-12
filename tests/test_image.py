from __future__ import annotations

import numpy as np
from PIL import Image

from simple_glyph.image import ink_mask
from simple_glyph.skeleton import resample


def test_ink_mask_black_on_white():
    image = Image.new("RGB", (40, 30), "white")
    for y in range(10, 20):
        for x in range(5, 35):
            image.putpixel((x, y), (0, 0, 0))
    mask = ink_mask(image, threshold=200)
    assert mask.sum() == 300
    assert mask[15, 20]
    assert not mask[2, 2]


def test_ink_mask_respects_alpha():
    image = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    image.putpixel((5, 5), (0, 0, 0, 255))
    mask = ink_mask(image, threshold=200)
    assert mask.sum() == 1
    assert mask[5, 5]


def test_resample_keeps_endpoints():
    points = np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 10.0]])
    out = resample(points, spacing=2.0)
    assert np.allclose(out[0], points[0])
    assert np.allclose(out[-1], points[-1])
    assert len(out) >= 10
