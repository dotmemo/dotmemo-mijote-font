# SPDX-License-Identifier: MIT
"""Offline, self-contained review page and outline-based SVG proofs."""

import base64
import csv
import html
import json
import unicodedata


def write_proofs(root, output, config, source, paths):
    stem = config["file_stem"]
    font = base64.b64encode((output / f"{stem}.woff2").read_bytes()).decode()
    template = (root / "specimens/template.html").read_text()
    english = (root / "specimens/texts/en.txt").read_text().strip()
    french = (root / "specimens/texts/fr.txt").read_text().strip()
    en_lines, fr_lines = english.splitlines(), french.splitlines()
    replacements = {
        "__FONT_DATA__": font,
        "__FAMILY__": html.escape(config["family"]),
        "__STYLE__": html.escape(config["style"]),
        "__VERSION__": html.escape(config["version"]),
        "__SUPPORTED__": json.dumps(list(source["glyphs"]), ensure_ascii=True),
        "__CHARACTERS__": html.escape("".join(source["glyphs"])),
        "__ENGLISH__": html.escape(english),
        "__FRENCH__": html.escape(french),
        "__EN_TITLE__": html.escape(en_lines[0]),
        "__FR_TITLE__": html.escape(fr_lines[0]),
        "__EN_NOTE__": html.escape(en_lines[2]),
        "__FR_NOTE__": html.escape(fr_lines[2]),
        "__CALCULATION__": html.escape(en_lines[-1]),
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    (output / "index.html").write_text(template, encoding="utf-8")
    with (output / "coverage.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["codepoint", "character", "unicode_name", "advance"])
        for character, glyph in source["glyphs"].items():
            writer.writerow(
                [
                    f"U+{ord(character):04X}",
                    character,
                    unicodedata.name(character, "UNNAMED"),
                    glyph["advance"],
                ]
            )
    svg_dir = output / "glyphs-svg"
    svg_dir.mkdir(exist_ok=True)
    for character, path in paths.items():
        width = max(source["glyphs"][character]["advance"] + 400, 700)
        (svg_dir / f"U{ord(character):04X}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-200 -1100 {width} 1450">'
            f"<title>U+{ord(character):04X} {html.escape(character)}</title>"
            f'<g transform="scale(1,-1)"><path d="{path}"/></g></svg>\n'
        )
    cover = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1500" '
        'viewBox="0 0 1200 1500"><title>dotmemo mijote - unreleased Bold proof</title>'
        '<rect width="1200" height="1500" fill="#f5f0e6"/>'
        '<g fill="#1d382f"><text x="65" y="65" font-family="sans-serif" '
        'font-size="18">DOTMEMO MIJOTE / BOLD</text>'
    ]

    def line(text, baseline, size):
        width = sum(source["glyphs"][c]["advance"] for c in text)
        size = min(size, 1080 * 1000 / max(width, 1))
        x = 60
        for character in text:
            cover.append(
                f'<path d="{paths[character]}" '
                f'transform="translate({x:.3f} {baseline}) '
                f'scale({size / 1000} {-size / 1000})"/>'
            )
            x += source["glyphs"][character]["advance"] * size / 1000

    line("dotmemo", 340, 230)
    line("mijote", 570, 230)
    line(en_lines[0], 780, 130)
    line(fr_lines[0], 960, 115)
    line("0123456789", 1140, 130)
    line("69 96 99 / 9 q g", 1280, 100)
    line("€ £ ¥ ¢ $ / æ œ", 1420, 95)
    cover.append("</g></svg>\n")
    (output / "specimen.svg").write_text("".join(cover), encoding="utf-8")
