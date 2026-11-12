"""Image loading and ink extraction helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def load_rgb(path: str | Path) -> Image.Image:
    """Load an image as RGB, preserving the original canvas size."""
    return Image.open(path).convert("RGB")


def ink_mask(image: Image.Image, threshold: int = 200) -> np.ndarray:
    """Return a boolean mask for dark ink.

    Threshold means: a pixel is ink when its luminance is strictly below
    ``threshold``.  For images with alpha, transparent pixels are never ink.
    """
    if not 0 <= threshold <= 255:
        raise ValueError("threshold must be in [0, 255]")
    gray = np.asarray(image.convert("L"), dtype=np.uint8)
    mask = gray < threshold
    if "A" in image.getbands():
        alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
        mask &= alpha > 8
    return mask


def alpha_from_luminance(image: Image.Image) -> Image.Image:
    """Make a simple alpha matte for black ink on a light background.

    This is a convenience for preview-only use.  For production, prefer a
    measured background model or a manually corrected alpha matte.
    """
    gray = np.asarray(image.convert("L"), dtype=np.float32)
    alpha = np.clip(255.0 - gray, 0, 255).astype(np.uint8)
    out = image.convert("RGBA")
    out.putalpha(Image.fromarray(alpha, mode="L"))
    return out
