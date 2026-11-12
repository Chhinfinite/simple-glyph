"""Command line interface for simple-glyph."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from . import __version__
from .image import load_rgb
from .models import Glyph, load_glyph, save_glyph
from .preview import render_overlay, render_preview, save_png
from .svg import centerline_svg, write_svg
from .trace import trace_glyph


def _bundle(
    glyph: Glyph,
    out_dir: Path,
    stem: Optional[str] = None,
    source_image=None,
    animate: bool = True,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = stem or (glyph.character or "glyph")
    save_glyph(glyph, out_dir / f"{stem}_centerline.json")
    write_svg(centerline_svg(glyph), out_dir / f"{stem}_centerline.svg")
    write_svg(centerline_svg(glyph, colored=True, labels=True), out_dir / f"{stem}_centerline_colored.svg")
    if animate:
        write_svg(centerline_svg(glyph, animate=True), out_dir / f"{stem}_animation.svg")
    save_png(render_preview(glyph, background="checker"), out_dir / f"{stem}_preview_checker.png")
    save_png(render_preview(glyph, background="white"), out_dir / f"{stem}_preview_white.png")
    if source_image is not None:
        save_png(render_overlay(source_image, glyph), out_dir / f"{stem}_overlay.png")
    print(f"wrote {len(glyph.strokes)} strokes to {out_dir}")


def cmd_trace(args: argparse.Namespace) -> int:
    source = load_rgb(args.image)
    glyph = trace_glyph(
        source,
        args.hints,
        character=args.character,
        threshold=args.threshold,
        method=args.method,
        sigma=args.sigma,
        spacing=args.spacing,
    )
    _bundle(glyph, Path(args.out), stem=args.stem, source_image=source, animate=not args.no_animation)
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    glyph = load_glyph(args.data)
    _bundle(glyph, Path(args.out), stem=args.stem, animate=not args.no_animation)
    return 0


def _repo_examples() -> Path:
    here = Path(__file__).resolve()
    for candidate in (here.parents[2] / "examples", Path.cwd() / "examples"):
        if (candidate / "input" / "央.png").exists():
            return candidate
    raise FileNotFoundError("examples/ not found; run from the repository or pass --image/--hints")


def cmd_demo(args: argparse.Namespace) -> int:
    examples = _repo_examples()
    source = load_rgb(examples / "input" / "央.png")
    glyph = trace_glyph(
        source,
        examples / "hints" / "央.json",
        character="央",
        threshold=args.threshold,
        method=args.method,
    )
    _bundle(glyph, Path(args.out), stem="央", source_image=source, animate=not args.no_animation)
    return 0


def cmd_info(_: argparse.Namespace) -> int:
    print(f"simple-glyph {__version__}")
    print("Python", sys.version.split()[0])
    print("Docs: https://github.com/Chhinfinite/simple-glyph")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="simple-glyph",
        description="Turn a calligraphy image into ordered, editable stroke centerlines.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("trace", help="trace an image with a JSON hint file")
    p.add_argument("--image", required=True, help="input PNG/JPEG")
    p.add_argument("--hints", required=True, help="JSON hint file with stroke waypoints")
    p.add_argument("--out", default="output", help="output directory")
    p.add_argument("--character", default=None, help="display character")
    p.add_argument("--stem", default=None, help="output filename stem")
    p.add_argument("--threshold", type=int, default=200, help="ink threshold, gray < N")
    p.add_argument("--method", choices=["medial_axis", "skeletonize"], default="medial_axis")
    p.add_argument("--sigma", type=float, default=2.2)
    p.add_argument("--spacing", type=float, default=2.5)
    p.add_argument("--no-animation", action="store_true")
    p.set_defaults(func=cmd_trace)

    p = sub.add_parser("render", help="render an existing centerline JSON")
    p.add_argument("--data", required=True, help="centerline JSON")
    p.add_argument("--out", default="output")
    p.add_argument("--stem", default=None)
    p.add_argument("--no-animation", action="store_true")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("demo", help="run the bundled 央 example")
    p.add_argument("--out", default="examples/output")
    p.add_argument("--threshold", type=int, default=200)
    p.add_argument("--method", choices=["medial_axis", "skeletonize"], default="medial_axis")
    p.add_argument("--no-animation", action="store_true")
    p.set_defaults(func=cmd_demo)

    p = sub.add_parser("info", help="print version and environment")
    p.set_defaults(func=cmd_info)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
