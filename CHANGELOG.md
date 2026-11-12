# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned

- Bézier fitting for centerline simplification.
- Standard-median alignment (affine + DTW + TPS).
- Multi-character canvas and batch naming.
- Optional width/pressure profile.

## [0.1.0] - 2026-11-11

### Added

- Initial public release.
- `simple-glyph trace` command: image + JSON hints → ordered centerlines.
- `simple-glyph render` command: JSON → SVG/PNG bundle.
- `simple-glyph demo` command with a bundled 央 example.
- Medial-axis and skeletonize backends.
- Open SVG centerlines (`fill="none"`, no `Z`).
- CSS/SVG stroke reveal animation.
- PNG checker/white previews and source overlay.
- Tests, CI workflow, issue/PR templates, and documentation.

[Unreleased]: https://github.com/Chhinfinite/simple-glyph/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Chhinfinite/simple-glyph/releases/tag/v0.1.0
