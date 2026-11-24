# Licensing

| Material | Licence |
| --- | --- |
| Font binaries, UFO exports, glyph SVG exports and `sources/` | SIL Open Font License 1.1 ([OFL.txt](../OFL.txt)) |
| Procedural drawing source `tools/regenerate_drawings.py` and `specimens/current.svg` | SIL Open Font License 1.1 |
| Independent build/validation tools, tests, configuration and documentation | MIT ([LICENSE-MIT](../LICENSE-MIT)) |

No Reserved Font Names are declared. The drawing recipe is font source, even
though it is stored alongside tooling. Running the independent MIT tools does
not change the OFL licence of generated fonts.

Generated font distributions include `OFL.txt`. Keep copyright and licence
notices with redistributed materials. Font embedding flags are unrestricted
(`fsType = 0`), consistent with the OFL distribution terms.

Run `make release-check` before a release and verify copyright and licence
metadata in each output format.

`LICENSE` contains the full OFL text for the typeface. `LICENSE-MIT` contains
the MIT text for independent tooling. These are separate scopes, not a choice
between two licences for the same files. `OFL.txt` accompanies font distributions.
