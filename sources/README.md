# Sources

`glyphs.json` contains unskewed paths, advances and kerning data.
`components.json` contains construction components for the drawing recipe.

Normal builds read these files and write exports under `build/`.
`uv run python tools/regenerate_drawings.py` produces a separate candidate source.
Review it before replacing `glyphs.json`.

Coordinates use a 1000-unit em and y points up. Slant is applied once during the
build. Generated UFO and SVG files already include it; they are not source inputs.

These font sources are licensed under OFL-1.1. See [OFL.txt](../OFL.txt).
