# SPDX-License-Identifier: MIT
"""Curve operations shared by the drawing recipe and regressions."""

import pathops
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path


def path(commands):
    outline = pathops.Path()
    parse_path(commands, outline.getPen())
    return outline


def union(*parts):
    combined = pathops.Path()
    # Normalize each operand: reflected winding must not cancel overlapping ink.
    for part in parts:
        pathops.simplify(part, clockwise=False).draw(combined.getPen())
    return pathops.simplify(combined)


def transform(outline, sx=1, sy=1, dx=0, dy=0):
    transformed = pathops.Path()
    outline.draw(TransformPen(transformed.getPen(), (sx, 0, 0, sy, dx, dy)))
    return transformed
