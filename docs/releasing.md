# Releasing

1. Set font naming and revision in `font.toml`.
2. Complete copyright and licence metadata and include the applicable licence files.
3. Confirm embedding flags match the distribution terms.
4. From a clean checkout run `uv sync --locked`, `make lint`, `make check`,
   `make test` and `uv run --locked python tools/check_repository.py`.
5. Run `make release-check` and review the generated font metadata.
6. Visually inspect glyphs, spacing, marks and representative continuous text.
   Test target rendering engines and applications. Run a suitable sanitizer and
   FontBakery profile, recording justified exceptions.
7. Package fonts, source, licences, coverage, changes, specimen and checksums.
8. Tag the reviewed source and publish matching artifacts. Retain prior releases
   for rollback; do not replace tagged assets silently.

CI performs build and regression checks; publication is a separate operation.
