# SPDX-License-Identifier: MIT
"""Build fonts and proofs from source curves.

Source paths are unskewed; the slant is applied exactly once here.
The generated UFO and SVG paths already include this slant.
"""

import json
import math
import tomllib
import unicodedata as ud
from pathlib import Path
from types import SimpleNamespace

from fontTools.agl import UV2AGL
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.pointPen import SegmentToPointPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from fontTools.ufoLib import UFOWriter


def build(root: Path, output: Path):
    SRC = root / "sources"
    OUT = output
    OUT.mkdir(parents=True, exist_ok=True)
    config = tomllib.loads((root / "font.toml").read_text())["font"]
    D = json.loads((SRC / "glyphs.json").read_text())
    N = {c: UV2AGL.get(ord(c), f"uni{ord(c):04X}") for c in D["glyphs"]}
    N["\u00a0"] = "nbspace"
    N["\u00ad"] = "softhyphen"
    G = {}
    SVG = {}
    ADV = {}
    for c, g in D["glyphs"].items():
        rec = RecordingPen()
        parse_path(g["path"], TransformPen(rec, (1, 0, D["slant"], 1, 0, 0)))
        G[c] = rec
        ADV[c] = g["advance"]
        p = SVGPathPen(None)
        rec.replay(p)
        SVG[c] = p.getCommands()

    def base(c):
        return {"ø": "o", "Ø": "O", "æ": "a", "Æ": "A", "œ": "o", "Œ": "O", "ı": "i", "ȷ": "j"}.get(
            c, ud.normalize("NFD", c)[0]
        )

    K = {}

    def kern(left, right, value):
        for left_char in left:
            for right_char in right:
                K[left_char + right_char] = value

    for pair, v in D["kerning"].items():
        K[base(pair[0]) + base(pair[1])] = v
    kern("AVWY", "AVWY", -35)
    kern("A", "VYW", -55)
    kern("VYW", "A", -55)
    kern("T", "acegopqsu", -45)
    kern("T", "r", -24)
    kern("VY", "acegopqsu", -35)
    kern("W", "acegopqsu", -22)
    kern("F", "acegopqs", -25)
    kern("F", "A", -35)
    kern("P", "A", -45)
    kern("P", "aeo", -18)
    kern("L", "TVWY", -45)
    kern("KX", "COG", -20)
    kern("OQC", "AVWY", -20)
    kern("VY", "COG", -22)
    kern("r", "aceo", -10)
    kern("vwy", "aeo", -14)
    kern("aceo", "vwy", -12)
    kern("ft", "aeo", -12)
    kern("f", "iı", -8)
    kern("k", "aceo", -10)
    kern("AVWYTFP", ".,", -35)
    kern("vwy", ".,", -18)
    kern(".,", "TVWY", -20)
    K["no"] = -14
    K["ot"] = -8
    K["te"] = -10
    K["mo"] = -12
    K["om"] = -8
    K["me"] = -8
    K["on"] = -12
    K["nt"] = -12
    allkern = {}
    for left_char in G:
        if ud.combining(left_char):
            continue
        for right_char in G:
            if ud.combining(right_char):
                continue
            v = K.get(base(left_char) + base(right_char))
            if v is not None:
                allkern[(N[left_char], N[right_char])] = v
    fea = "languagesystem DFLT dflt;\nlanguagesystem latn dflt;\nlanguagesystem latn FRA;\n"
    above = [c for c in G if ud.combining(c) and c != "\u0327"]
    fea += "@ABOVE=[" + " ".join(N[c] for c in above) + "];\n"
    fea += f"feature ccmp {{ sub i' @ABOVE by {N['ı']}; sub j' @ABOVE by {N['ȷ']}; }} ccmp;\n"
    fea += (
        "feature kern {\n"
        + "".join(
            f"pos {left_name} {right_name} {v};\n" for (left_name, right_name), v in allkern.items()
        )
        + "} kern;\n"
    )
    for c in above:
        fea += f"markClass {N[c]} <anchor 0 0> @TOP;\n"
    fea += f"markClass {N[chr(0x327)]} <anchor 0 0> @BOTTOM;\nfeature mark {{\n"
    for c in G:
        if not c.isalpha() or ud.combining(c):
            continue
        b = base(c)
        top = 775 if c.isupper() else 570
        if b in "bdfhklþð":
            top = 775
        if b in "ij":
            top = 735
        if b == "t":
            top = 735
        if c in "ıȷ":
            top = 570
        if len(ud.normalize("NFD", c)) > 1 and c not in "çÇ":
            top += 180
        # Font coordinates include the slant, including mark anchors.
        x = (121 if c in "iı" else 169 if c in "jȷ" else ADV[c] / 2 + (51 if b == "e" else 0)) + D[
            "slant"
        ] * top
        fea += f"pos base {N[c]} <anchor {round(x)} {top}> mark @TOP <anchor {round(ADV[c] / 2)} 0> mark @BOTTOM;\n"
    fea += "} mark;\n"
    (OUT / "features.fea").write_text(fea)

    order = [".notdef"] + list(N.values())
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    glyphs = {}
    metrics = {}
    for c, rec in G.items():
        pen = TTGlyphPen(None)
        rec.replay(Cu2QuPen(pen, max_err=0.6, reverse_direction=True))
        g = pen.glyph()
        g.recalcBounds(None)
        glyphs[N[c]] = g
        metrics[N[c]] = (ADV[c], getattr(g, "xMin", 0))
    missing = TTGlyphPen(None)
    for points in [
        [(70, 0), (70, 650), (470, 650), (470, 0)],
        [(130, 60), (410, 60), (410, 590), (130, 590)],
    ]:
        missing.moveTo(points[0])
        for xy in points[1:]:
            missing.lineTo(xy)
        missing.closePath()
    glyphs[".notdef"] = missing.glyph()
    metrics[".notdef"] = (540, 70)
    fb.setupCharacterMap({ord(c): name for c, name in N.items()})
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=1050, descent=-300, lineGap=0)
    fb.setupNameTable(
        {
            "familyName": config["family"],
            "styleName": config["style"],
            "typographicFamily": config["family"],
            "typographicSubfamily": config["style"],
            "uniqueFontIdentifier": f"{config['postscript_name']}-{config['version']}",
            "fullName": f"{config['family']} {config['style']}",
            "psName": config["postscript_name"],
            "version": f"Version {config['version']}",
            "description": "Rounded proportional typeface.",
            "copyright": config["copyright"],
            "licenseDescription": config["license_description"],
            "licenseInfoURL": config.get("license_url", ""),
        }
    )
    fb.setupOS2(
        version=4,
        sTypoAscender=1050,
        sTypoDescender=-300,
        sTypoLineGap=0,
        usWinAscent=1050,
        usWinDescent=300,
        sxHeight=490,
        sCapHeight=700,
        usWeightClass=config["weight"],
        fsSelection=0xA0,
        fsType=config["fs_type"],
    )
    fb.setupPost(italicAngle=-math.degrees(math.atan(D["slant"])))
    fb.setupMaxp()
    addOpenTypeFeaturesFromString(fb.font, fea)
    fb.font["head"].fontRevision = float(config["version"])
    fb.font["head"].macStyle = 1
    # Consistent timestamps for reproducible generation.
    fb.font["head"].created = fb.font["head"].modified = 3878064000
    fb.font.recalcTimestamp = False
    fb.save(str(OUT / f"{config['file_stem']}.ttf"))
    fb.font.flavor = "woff2"
    fb.font.save(str(OUT / f"{config['file_stem']}.woff2"))
    fb.font.flavor = None

    # Editable UFO with cubic/quadratic outlines before conversion to TTF.
    ufo = OUT / "dotmemo-mijote.ufo"
    writer = UFOWriter(ufo, formatVersion=3)
    writer.writeInfo(
        SimpleNamespace(
            familyName=config["family"],
            styleName=config["style"],
            unitsPerEm=1000,
            ascender=700,
            descender=-250,
            xHeight=490,
            capHeight=700,
            italicAngle=-math.degrees(math.atan(D["slant"])),
            versionMajor=int(config["version"].split(".")[0]),
            versionMinor=int(config["version"].split(".")[1]),
            copyright=config["copyright"],
            openTypeNameLicense=config["license_description"],
            openTypeNameLicenseURL=config.get("license_url", ""),
            openTypeOS2WeightClass=config["weight"],
            openTypeOS2Type=[bit for bit in range(16) if config["fs_type"] & (1 << bit)],
            openTypeHheaAscender=1050,
            openTypeHheaDescender=-300,
            openTypeOS2TypoAscender=1050,
            openTypeOS2TypoDescender=-300,
            openTypeOS2WinAscent=1050,
            openTypeOS2WinDescent=300,
        )
    )
    gs = writer.getGlyphSet()
    for c, rec in G.items():
        gs.writeGlyph(
            N[c],
            SimpleNamespace(width=ADV[c], height=0, unicodes=[ord(c)]),
            lambda pointpen, rec=rec: rec.replay(SegmentToPointPen(pointpen)),
        )
    missingrec = RecordingPen()
    glyphs[".notdef"].draw(missingrec, None)
    gs.writeGlyph(
        ".notdef",
        SimpleNamespace(width=540, height=0, unicodes=[]),
        lambda pointpen: missingrec.replay(SegmentToPointPen(pointpen)),
    )
    gs.writeContents()
    writer.writeLayerContents()
    writer.writeKerning(allkern)
    writer.writeFeatures(fea)
    writer.writeLib({"public.glyphOrder": order})
    writer.close()

    from .proofs import write_proofs
    from .validate import manifest

    (OUT / "OFL.txt").write_text((root / "OFL.txt").read_text())
    write_proofs(root, OUT, config, D, SVG)
    report = manifest(OUT, config, len(G), len(allkern))
    return report
