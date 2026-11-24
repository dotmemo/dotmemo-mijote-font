# Contributing

Use English for code and documentation. Keep specimen text in its own language.

Run `uv sync --locked`, then `make check`, `make test` and `make lint`.
For a focused test use `uv run --locked pytest tests/test_font.py -k nine`.

Edit `sources/glyphs.json` for outlines and advances. Source paths use a 1000-unit
em with y pointing up; the builder applies the slant once. UFO and SVG exports
are generated files, not additional editable authorities.

For drawing changes provide codepoints, before/after proofs and a reason.
Review related accented forms, case variants and shared components. Check spacing,
counters, intersections and rasterization at several sizes.

For repertoire additions document required characters and combining sequences,
update validation expectations, add shaping examples and verify both input
normalization forms where applicable. Character mappings alone do not prove
correct shaping. Use text and artwork with documented redistribution rights.

Reference changes must be narrow and reviewed. Do not regenerate reference hashes
merely to make a failing test pass. Keep generated builds out of source commits.
