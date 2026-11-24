# Build architecture

`sources/glyphs.json` is authoritative for outlines, advances and initial kerning.
`sources/components.json` supplies construction components used by the drawing
recipe. `font.toml` defines font names, weight, revision and distribution metadata.

The build applies the slant to source coordinates once, expands kerning,
compiles OpenType features and converts curves to TrueType with a 0.6-unit error
tolerance. Generated UFO and SVG paths already contain the slant. Editing these
exports does not update the source JSON.

`uv.lock` pins dependencies. `make check` builds and validates; `make test` runs
geometry, shaping, export and repeatability regressions. Run validation without
Python optimization (`-O`), because validation uses assertions.

`tools/regenerate_drawings.py` writes `build/candidate-glyphs.json`. Compare the
candidate before replacing the authoritative source. The recipe does not overwrite
sources by default.

`tests/data/shape-reference.json` stores per-glyph source and compiled-outline
hashes plus horizontal metrics. Deliberate drawing changes require a narrowly
reviewed reference update. Repertoire expansion also requires updating expected
coverage and meaningful shaping cases. Keep unaffected glyph references intact.

Validation covers character mappings, bounds, counters, intersections, kerning,
accent placement, NFC/NFD shaping, FreeType rasterization, UFO/WOFF2 geometry,
metadata and repeat builds. It does not replace visual review or platform tests.

Fixed OpenType timestamps support repeatable builds. `build/manifest.json` records
relative artifact paths, sizes and hashes. CI builds and tests on Python 3.11 and
3.13 with read-only repository permissions and no publication step.
