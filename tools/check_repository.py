# SPDX-License-Identifier: MIT
"""Check public source hygiene, local documentation links."""

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


def check_repository(root):
    files = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root
        )
        .decode()
        .split("\0")
    )
    files = sorted(set(name for name in files if name))
    failures = []
    private_roots = ["/" + part + "/" for part in ["home", "Users"]]
    ignored_dirs = {"work", "build", "dist", ".venv", ".pixel", ".uv-cache", ".mmo"}
    for name in files:
        path = root / name
        if path.parts[len(root.parts)] in ignored_dirs:
            failures.append(f"Private/generated directory in public source: {name}")
        if path.is_symlink():
            if not path.resolve().is_relative_to(root):
                failures.append(f"External symlink: {name}")
            continue
        if path.stat().st_size > 2_000_000:
            failures.append(f"Unexpected large source file: {name}")
        if path.suffix in {".png", ".ttf", ".woff2", ".pdf"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"Unrecognized binary file: {name}")
            continue
        if any(marker in content for marker in private_roots):
            failures.append(f"Workstation path found: {name}")
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", content):
                target = target.strip("<>")
                if target.startswith("#") or urlsplit(target).scheme:
                    continue
                target = unquote(target.split("#", 1)[0])
                if target and not (path.parent / target).exists():
                    failures.append(f"Broken relative link in {name}: {target}")
        if path.suffix in {".yaml", ".yml"}:
            try:
                yaml.load(content, Loader=yaml.BaseLoader)
            except yaml.YAMLError as error:
                failures.append(f"Invalid YAML in {name}: {error}")
    print(json.dumps({"public_source_files": len(files), "failures": failures}, indent=2))
    return not failures


if __name__ == "__main__":
    raise SystemExit(0 if check_repository(Path(__file__).resolve().parents[1]) else 1)
