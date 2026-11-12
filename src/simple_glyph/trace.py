"""High-level tracing entry point."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image

from .hints import HintSet, load_hints
from .image import ink_mask, load_rgb
from .models import Glyph, Stroke
from .skeleton import trace_strokes


def trace_glyph(
    image: Image.Image | str | Path,
    hints: HintSet | str | Path,
    character: Optional[str] = None,
    threshold: int = 200,
    method: str = "medial_axis",
    sigma: float = 2.2,
    spacing: float = 2.5,
) -> Glyph:
    """Trace a glyph from an image and a hint set.

    Parameters
    ----------
    image:
        PIL image or path.  RGB/RGBA are both accepted.
    hints:
        HintSet or path to a JSON hint file.
    character:
        Optional display character; defaults to the hint file's character.
    threshold:
        Ink is ``gray < threshold``.
    method:
        ``medial_axis`` (recommended) or ``skeletonize``.
    """
    if isinstance(image, (str, Path)):
        image = load_rgb(image)
    if isinstance(hints, (str, Path)):
        hints = load_hints(hints)
    mask = ink_mask(image, threshold=threshold)
    strokes: list[Stroke] = trace_strokes(
        mask, hints, method=method, sigma=sigma, spacing=spacing
    )
    return Glyph(
        character=character or hints.character or "untitled",
        canvas=(image.width, image.height),
        strokes=strokes,
        source={
            "image_size": [image.width, image.height],
            "threshold": threshold,
            "method": method,
            "note": "Medial-axis trace from manual stroke waypoints; not a general OCR/segmentation model.",
        },
    )
