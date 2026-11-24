# SPDX-License-Identifier: MIT
"""Small source-checkout CLI with explicit output paths."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "check", "release-check"])
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--output", type=Path, default=Path("build"))
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    if args.command == "build":
        from .build import build

        report = build(root, output)
    elif args.command == "check":
        from .validate import validate

        report = validate(root, output)
    else:
        from .release import release_check

        report = release_check(root)
        print(json.dumps(report, indent=2))
        raise SystemExit(0 if report["ready"] else 1)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
