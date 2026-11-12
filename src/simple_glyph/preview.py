"""PNG previews for quick visual QA."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .models import Glyph


def checkerboard(size: tuple[int, int], cell: int = 20) -> Image.Image:
    im = Image.new("RGB", size, "white")
    d = ImageDraw.Draw(im)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(226, 226, 226))
    return im


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_strokes(
    image: Image.Image,
    glyph: Glyph,
    scale: int,
    colored: bool,
    labels: bool,
    markers: bool,
) -> Image.Image:
    big = image.resize((glyph.canvas[0] * scale, glyph.canvas[1] * scale), Image.LANCZOS)
    if big.mode != "RGBA":
        big = big.convert("RGBA")
    layer = Image.new("RGBA", big.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for stroke in glyph.strokes:
        color = stroke.color if colored else "#111111"
        rgb = tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))
        xy = [(float(x) * scale, float(y) * scale) for x, y in stroke.points]
        d.line(xy, fill=rgb + (255,), width=max(2, 3 * scale), joint="curve")
        if markers:
            r = max(3, 4 * scale // 2)
            d.ellipse(
                [xy[0][0] - r, xy[0][1] - r, xy[0][0] + r, xy[0][1] + r],
                fill=(35, 160, 85, 255),
                outline=(255, 255, 255, 255),
                width=max(1, scale),
            )
            d.ellipse(
                [xy[-1][0] - r, xy[-1][1] - r, xy[-1][0] + r, xy[-1][1] + r],
                fill=(200, 35, 35, 255),
                outline=(255, 255, 255, 255),
                width=max(1, scale),
            )
    big.alpha_composite(layer)
    big = big.resize(glyph.canvas, Image.LANCZOS)

    if labels:
        d = ImageDraw.Draw(big)
        font = _font(max(14, 20))
        for stroke in glyph.strokes:
            if stroke.label_at is not None:
                x, y = stroke.label_at
            else:
                x, y = float(stroke.points[0][0] + 16), float(stroke.points[0][1] - 16)
            r = 11
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255), outline=(30, 30, 30), width=2)
            d.text((x, y), stroke.id, font=font, fill=(10, 10, 10), anchor="mm")
    return big


def render_preview(
    glyph: Glyph,
    background: str = "checker",
    colored: bool = True,
    labels: bool = True,
    markers: bool = True,
    scale: int = 2,
) -> Image.Image:
    """Render a checker/white/transparent preview at the original canvas size."""
    if background == "checker":
        base = checkerboard(glyph.canvas).convert("RGBA")
    elif background == "white":
        base = Image.new("RGBA", glyph.canvas, (255, 255, 255, 255))
    elif background == "transparent":
        base = Image.new("RGBA", glyph.canvas, (0, 0, 0, 0))
    else:
        raise ValueError("background must be checker, white or transparent")
    return _draw_strokes(base, glyph, scale=scale, colored=colored, labels=labels, markers=markers)


def render_overlay(
    source: Image.Image,
    glyph: Glyph,
    colored: bool = True,
    labels: bool = False,
    scale: int = 2,
) -> Image.Image:
    """Draw stroke lines over the source image for QA."""
    base = source.convert("RGBA")
    if base.size != glyph.canvas:
        base = base.resize(glyph.canvas, Image.LANCZOS)
    return _draw_strokes(base, glyph, scale=scale, colored=colored, labels=labels, markers=False)


def save_png(image: Image.Image, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
