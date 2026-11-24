# SPDX-License-Identifier: MIT
"""Baseline geometry, shaping, rasterization and export checks.

This intentionally validates the reference reference repertoire; new glyphs require
an explicit baseline/version policy change, not a silent golden-file refresh.
"""

import hashlib
import json
import tomllib
import unicodedata as ud
from types import SimpleNamespace

import pathops
import uharfbuzz as hb
from fontTools.pens.pointPen import PointToSegmentPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
from fontTools.ufoLib import UFOReader
from PIL import Image, ImageDraw, ImageFont


def validate(root, output):
    SRC = root / "sources"
    OUT = output
    config = tomllib.loads((root / "font.toml").read_text())["font"]
    f = TTFont(OUT / f"{config['file_stem']}.ttf", checkChecksums=2)
    cmap = f.getBestCmap()
    spec = json.loads((SRC / "glyphs.json").read_text())
    assert set(cmap) == {ord(c) for c in spec["glyphs"]}
    assert set(range(32, 127)) <= set(cmap), "ASCII character missing"
    assert set(range(160, 256)) <= set(cmap), "Latin-1 character missing"
    for cp in "ŒœŸ€’‘“”«»–—…\u202f":
        assert ord(cp) in cmap, cp
    assert len(cmap) == 225, len(cmap)
    for cp, name in cmap.items():
        g = f["glyf"][name]
        if chr(cp).isspace():
            assert g.numberOfContours == 0
        else:
            assert g.numberOfContours > 0, (chr(cp), name)
            assert g.yMax <= f["OS/2"].usWinAscent, (name, g.yMax)
            assert g.yMin >= -f["OS/2"].usWinDescent, (name, g.yMin)
    assert f["OS/2"].version >= 4
    assert f["name"].getDebugName(6) == config["postscript_name"]
    assert f["name"].getDebugName(1) == config["family"]
    assert f["name"].getDebugName(4) == config["family"] + " " + config["style"]
    assert config["version"] in f["name"].getDebugName(5)
    assert abs(f["head"].fontRevision - float(config["version"])) < 0.0001
    for c in "agq":
        assert f["glyf"][cmap[ord(c)]].numberOfContours == 2, c
    topology = {
        "€": 1,
        "£": 1,
        "¥": 1,
        "¢": 2,
        "$": 3,
        "æ": 3,
        "œ": 3,
        "Æ": 2,
        "Œ": 2,
        "ø": 3,
        "Ø": 3,
        "ð": 2,
        "p": 2,
        "þ": 2,
        "Þ": 2,
        "µ": 1,
        "©": 3,
        "®": 4,
    }
    for c, count in topology.items():
        assert f["glyf"][cmap[ord(c)]].numberOfContours == count, (c, count)
    components = json.loads((SRC / "components.json").read_text())

    def canonical(d):
        p = pathops.Path()
        parse_path(d, p.getPen())
        p = pathops.simplify(p)
        pen = SVGPathPen(None)
        p.draw(pen)
        return pen.getCommands()

    for c in "demnot":
        assert canonical(components["glyphs"][c]["path"]) == canonical(spec["glyphs"][c]["path"]), c
        assert components["glyphs"][c]["advance"] == spec["glyphs"][c]["advance"]
    p = pathops.Path()
    for part in ["e", "acute"]:
        parse_path(components["glyphs"][part]["path"], p.getPen())
    pen = SVGPathPen(None)
    pathops.simplify(p).draw(pen)
    assert canonical(pen.getCommands()) == canonical(spec["glyphs"]["é"]["path"])
    data = (OUT / f"{config['file_stem']}.ttf").read_bytes()
    face = hb.Face(data)
    font = hb.Font(face)
    font.scale = (1000, 1000)

    def shape(s, features=None):
        b = hb.Buffer()
        b.add_str(s)
        b.guess_segment_properties()
        hb.shape(font, b, features)
        return [
            (i.codepoint, p.x_advance, p.x_offset, p.y_offset)
            for i, p in zip(b.glyph_infos, b.glyph_positions)
        ]

    texts = [(root / f"specimens/texts/{language}.txt").read_text() for language in ["en", "fr"]]
    texts = [line for text in texts for line in text.splitlines() if line]
    for s in texts:
        assert all(row[0] for row in shape(s)), s
    for c in "àâäçéèêëîïôöùûüÿÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ":
        assert shape(c) == shape(ud.normalize("NFD", c)), c
    assert sum(r[1] for r in shape("AVATAR ToTo")) < sum(
        r[1] for r in shape("AVATAR ToTo", {"kern": False})
    )
    mark = shape("m\u0301")
    assert len(mark) == 2 and mark[1][1] == 0 and mark[1][3] > 0, mark
    pilfont = ImageFont.truetype(str(OUT / f"{config['file_stem']}.ttf"), 96)
    for s in texts:
        assert pilfont.getmask(s).getbbox() is not None
    probe_font = ImageFont.truetype(str(OUT / f"{config['file_stem']}.ttf"), 1000)

    def silhouette(c):
        canvas = Image.new("L", (1400, 1500))
        ImageDraw.Draw(canvas).text((200, 1100), c, font=probe_font, fill=255, anchor="ls")
        return canvas

    def ink_at(image, y):
        return image.crop((0, 1100 - y, 1400, 1101 - y)).getbbox()

    euro, cee = silhouette("€"), silhouette("C")
    for y in range(100, 651, 5):
        assert abs(ink_at(euro, y)[0] - ink_at(cee, y)[0]) <= 2, ("euro exterior bump", y)
    for crossed, plain in [("ø", "o"), ("Ø", "O")]:
        one, two = silhouette(crossed), silhouette(plain)
        for y in range(20, 471 if plain == "o" else 681, 5):
            a, b = ink_at(one, y), ink_at(two, y)
            assert abs(a[0] - b[0]) <= 2 and abs(a[2] - b[2]) <= 2, (crossed, y)
    reader = UFOReader(OUT / "dotmemo-mijote.ufo")
    info = SimpleNamespace(copyright="", openTypeNameLicense="")
    reader.readInfo(info)
    assert info.familyName == config["family"]
    assert info.styleName == config["style"]
    assert info.openTypeOS2WeightClass == config["weight"]
    assert info.openTypeOS2Type == [bit for bit in range(16) if config["fs_type"] & (1 << bit)]
    assert info.copyright == config["copyright"]
    assert info.openTypeNameLicense == config["license_description"]
    gs = reader.getGlyphSet()
    for codepoint, name in cmap.items():
        rec = RecordingPen()
        # GLIF omits an advance element for zero-width combining marks.
        ufo_glyph = SimpleNamespace(width=0, unicodes=[])
        gs.readGlyph(name, ufo_glyph, PointToSegmentPen(rec))
        reference = RecordingPen()
        parse_path(
            spec["glyphs"][chr(codepoint)]["path"],
            TransformPen(reference, (1, 0, spec["slant"], 1, 0, 0)),
        )
        actual_path, expected_path = SVGPathPen(None), SVGPathPen(None)
        rec.replay(actual_path)
        reference.replay(expected_path)
        assert canonical(actual_path.getCommands()) == canonical(expected_path.getCommands()), name
        assert ufo_glyph.width == spec["glyphs"][chr(codepoint)]["advance"]
        assert ufo_glyph.unicodes == [codepoint]
    assert ".notdef" in gs
    reader.close()
    report = {
        "unicode_characters": len(cmap),
        "ascii_complete": True,
        "latin1_complete": True,
        "french_punctuation": True,
        "reference_outlines_unchanged": True,
        "outlines_and_vertical_bounds": True,
        "harfbuzz_french_samples": True,
        "NFC_NFD_equivalence": True,
        "kerning_effective": True,
        "combining_mark_positioned": True,
        "freetype_rasterization": True,
        "ufo_roundtrip": True,
        "ttf_bytes": len(data),
    }

    baseline = json.loads((root / "tests/data/shape-reference.json").read_text())
    for character, glyph in spec["glyphs"].items():
        reference = baseline["glyphs"][f"U+{ord(character):04X}"]
        digest = hashlib.sha256(
            json.dumps(glyph, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        assert digest == reference["source_sha256"], ("source changed", character)
        name = cmap[ord(character)]
        assert (
            hashlib.sha256(f["glyf"][name].compile(f["glyf"])).hexdigest()
            == reference["ttf_outline_sha256"]
        ), ("compiled outline changed", character)
        assert list(f["hmtx"][name]) == reference["hmtx"], ("advance or bearing changed", character)
    assert f["OS/2"].usWeightClass == config["weight"] == 800
    assert f["OS/2"].fsType == config["fs_type"]
    assert f["OS/2"].fsSelection & 32 and not f["OS/2"].fsSelection & 64
    assert f["head"].macStyle & 1
    assert f["name"].getDebugName(16) == config["family"]
    assert f["name"].getDebugName(17) == config["style"]
    assert f["name"].getDebugName(0) == config["copyright"]
    assert (f["name"].getDebugName(13) or "") == config["license_description"]
    assert f["name"].getDebugName(14) == config["license_url"]
    assert info.openTypeNameLicenseURL == config["license_url"]
    assert (OUT / "OFL.txt").read_bytes() == (root / "OFL.txt").read_bytes()
    assert config["fs_type"] == 0
    webfont = TTFont(OUT / f"{config['file_stem']}.woff2")
    assert webfont.getBestCmap() == cmap
    for name in f.getGlyphOrder():
        assert webfont["glyf"][name].getCoordinates(webfont["glyf"]) == f["glyf"][
            name
        ].getCoordinates(f["glyf"]), name
        assert webfont["hmtx"][name] == f["hmtx"][name], name
    webfont.close()
    report["all_225_baseline_outlines_and_metrics_unchanged"] = True
    report["woff2_geometry_roundtrip"] = True
    report["provisional_bold_metadata"] = True
    report["public_release_ready"] = False
    f.close()
    (OUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def manifest(output, config, characters, kern_pairs):
    files = {}
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name not in {"manifest.json", "verification.json"}:
            files[path.relative_to(output).as_posix()] = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
    report = {
        "family": config["family"],
        "style": config["style"],
        "version": config["version"],
        "unicode_characters": characters,
        "expanded_kerning_pairs": kern_pairs,
        "status": "unreleased",
        "files": files,
    }
    (output / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    return {key: value for key, value in report.items() if key != "files"}
