# SPDX-License-Identifier: MIT
"""Report unresolved release metadata without publishing anything."""

import tomllib


def release_check(root):
    config = tomllib.loads((root / "font.toml").read_text())
    release = config["release"]
    blockers = []
    for field in ["copyright_holder", "font_license", "code_license"]:
        if not release.get(field, "").strip():
            blockers.append(f"Missing release.{field}")
    for field in ["font_license_file", "code_license_file"]:
        name = release.get(field, "").strip()
        if not name:
            blockers.append(f"Missing release.{field}")
        elif not (root / name).is_file():
            blockers.append(f"Missing final license file: {name}")
    if release.get("status") != "approved":
        blockers.append("Release decision has not been recorded as approved")
    if not config["font"]["license_description"].strip():
        blockers.append("Missing font license description")
    if not release.get("embedding_reviewed", False):
        blockers.append("Embedding settings need a recorded license review")
    return {
        "ready": not blockers,
        "blockers": blockers,
        "scope": "Metadata preflight only; also complete docs/releasing.md and manual review.",
    }
