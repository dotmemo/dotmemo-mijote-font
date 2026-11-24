# SPDX-License-Identifier: MIT
import hashlib
import json
import subprocess
import sys

import pathops
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.svgLib.path import parse_path

from dotmemo_mijote.build import build
from dotmemo_mijote.geometry import path, transform, union
from dotmemo_mijote.release import release_check
from dotmemo_mijote.validate import validate


def canonical(commands):
    outline = pathops.Path()
    parse_path(commands, outline.getPen())
    pen = SVGPathPen(None)
    pathops.simplify(outline).draw(pen)
    return pen.getCommands()


def test_baseline_geometry_shaping_and_exports(root, built):
    report = validate(root, built)
    assert report["all_225_baseline_outlines_and_metrics_unchanged"]
    assert report["NFC_NFD_equivalence"]
    assert report["woff2_geometry_roundtrip"]


def test_nine_is_the_rotated_six(root):
    glyphs = json.loads((root / "sources/glyphs.json").read_text())["glyphs"]
    rotated = transform(path(glyphs["6"]["path"]), sx=-1, sy=-1, dx=605, dy=700)
    pen = SVGPathPen(None)
    rotated.draw(pen)
    assert canonical(glyphs["9"]["path"]) == canonical(pen.getCommands())
    assert glyphs["9"]["advance"] == glyphs["6"]["advance"] == 605


def test_union_preserves_overlapping_reflected_ink():
    left = path("M0 0H100V100H0Z")
    right = transform(left, sx=-1, dx=150)
    combined = union(left, right)
    # Two 100x100 squares overlap over 50x100; no cancellation is allowed.
    assert abs(combined.area) == 15000
    assert len(list(combined.contours)) == 1


def test_repeated_build_is_identical(root, built, tmp_path):
    build(root, tmp_path)
    for name in [
        "dotmemo-mijote-Bold.ttf",
        "dotmemo-mijote-Bold.woff2",
        "features.fea",
        "index.html",
        "specimen.svg",
        "coverage.csv",
    ]:
        assert (
            hashlib.sha256((built / name).read_bytes()).digest()
            == hashlib.sha256((tmp_path / name).read_bytes()).digest()
        ), name


def test_drawing_recipe_reproduces_reference_source_without_overwriting(root, tmp_path):
    candidate = tmp_path / "candidate.json"
    subprocess.run(
        [sys.executable, str(root / "tools/regenerate_drawings.py"), "--output", str(candidate)],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(candidate.read_text()) == json.loads(
        (root / "sources/glyphs.json").read_text()
    )


def test_release_preflight_reports_missing_metadata(tmp_path):
    (tmp_path / "font.toml").write_text(
        '[font]\nlicense_description = ""\n[release]\nstatus = "unreleased"\n'
    )
    report = release_check(tmp_path)
    assert not report["ready"]
    assert "Missing release.copyright_holder" in report["blockers"]
