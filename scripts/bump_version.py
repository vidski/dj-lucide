#!/usr/bin/env python3
"""
Bump the version field in pyproject.toml (PEP 621) and print the new version.

Usage:
  python scripts/bump_version.py            # default: patch bump
  python scripts/bump_version.py --type minor
  python scripts/bump_version.py --type major
  python scripts/bump_version.py --set 1.2.3
  python scripts/bump_version.py --file pyproject.toml   # custom path

It preserves toml formatting (uses tomlkit).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import tomlkit


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--file", default="pyproject.toml", help="Path to pyproject.toml")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--set", dest="set_version", help="Set explicit version like 1.2.3")
    group.add_argument("--type", choices=["major", "minor", "patch"], default="patch")
    return p.parse_args()


def _is_numeric_triplet(v: str) -> bool:
    return bool(re.fullmatch(r"\d+\.\d+\.\d+", v))


def bump(ver: str, bump_type: str) -> str:
    parts = ver.split(".")
    # normalize to 3 numeric parts
    while len(parts) < 3:
        parts.append("0")
    try:
        major, minor, patch = map(int, parts[:3])
    except ValueError:
        # If current is non-numeric (e.g., "1.2.3rc1"), reset intelligently: keep major/minor numeric, patch +1
        m = re.match(r"(\d+)\.(\d+)\.(\d+)", ver)
        if not m:
            # fallback to 0.1.0 for minor, 0.0.1 for patch, 1.0.0 for major
            return {"major": "1.0.0", "minor": "0.1.0", "patch": "0.0.1"}[bump_type]
        major, minor, patch = map(int, m.groups())

    if bump_type == "major":
        return f"{major + 1}.0.0"
    if bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"  # patch


def main() -> int:
    args = _parse_args()
    path = Path(args.file)
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 2

    data = tomlkit.parse(path.read_text(encoding="utf-8"))
    project = data.get("project") or {}
    current = project.get("version") or "0.0.0"

    if args.set_version:
        new_ver = args.set_version
    else:
        new_ver = bump(current, args.type)

    if not _is_numeric_triplet(new_ver):
        print("error: version must be numeric triplet like 1.2.3", file=sys.stderr)
        return 3

    project["version"] = new_ver
    data["project"] = project
    path.write_text(tomlkit.dumps(data), encoding="utf-8")

    # Print for GitHub Actions consumption
    print(new_ver)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
