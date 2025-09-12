#!/usr/bin/env python
"""
Download the Lucide zip and include only optimized icons (SVGs).
- If a version is provided: try that, then fall back to the latest.
- If no version is provided: use the latest automatically.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

GITHUB_API_LATEST = "https://api.github.com/repos/lucide-icons/lucide/releases/latest"
USER_AGENT_HDR = ["-H", "User-Agent: dj-lucide-updater"]
ACCEPT_HDR = ["-H", "Accept: application/vnd.github+json"]


def _curl_bytes(url: str) -> bytes | None:
    proc = subprocess.run(
        ["curl", "--fail", "--silent", "--location", *USER_AGENT_HDR, url],
        stdout=subprocess.PIPE,
    )
    return proc.stdout if proc.returncode == 0 else None


def _get_latest_tag() -> str | None:
    data = _curl_bytes(GITHUB_API_LATEST)
    if not data:
        return None
    try:
        js = json.loads(data.decode("utf-8"))
        # Usually looks like "v0.469.0"
        tag = js.get("tag_name")
        return str(tag) if tag else None
    except Exception:
        return None


def _download_release_zip_by_tag(tag: str) -> bytes | None:
    """
    Lucide assets are named without the leading 'v' in the filename.
    Release URL path uses the tag verbatim (may include 'v').
    """
    version_no_v = tag.lstrip("v")
    url = f"https://github.com/lucide-icons/lucide/releases/download/{tag}/lucide-icons-{version_no_v}.zip"
    return _curl_bytes(url)


def _try_download_with_variants(version: str) -> tuple[str, bytes] | tuple[None, None]:
    """
    Try the exact input as a tag, try adding/removing 'v' as needed,
    then fall back to latest tag from the API.
    Returns (resolved_tag, zip_bytes) on success, (None, None) on failure.
    """
    candidates: list[str] = []
    if version:
        candidates.append(version)
        if not version.startswith("v"):
            candidates.append("v" + version)
        else:
            candidates.append(version.lstrip("v"))

    # If no version provided, or the explicit ones fail, use latest.
    tried: set[str] = set()
    for tag in candidates:
        if not tag or tag in tried:
            continue
        tried.add(tag)
        data = _download_release_zip_by_tag(tag)
        if data:
            return tag if tag.startswith("v") else "v" + tag.lstrip("v"), data

    # Fallback to latest
    latest_tag = _get_latest_tag()
    if latest_tag and latest_tag not in tried:
        data = _download_release_zip_by_tag(latest_tag)
        if data:
            return latest_tag, data

    return None, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("version", nargs="?", help="dotted version or tag (e.g. 0.469.0 or v0.469.0). Omit to use latest.")
    args = parser.parse_args(argv)
    requested_version: str | None = args.version

    resolved_tag, zip_bytes = _try_download_with_variants(requested_version or "")
    if not zip_bytes:
        if requested_version:
            print(f"❌ Could not download Lucide for '{requested_version}', and latest fallback failed.")
        else:
            print("❌ Could not determine or download the latest Lucide release.")
        raise SystemExit(1)

    # Inform which version we ended up using
    print(f"ℹ️ Using Lucide release tag: {resolved_tag}")

    input_zip = ZipFile(BytesIO(zip_bytes))
    input_prefix = "icons/"
    output_path = "src/lucide/lucide.zip"

    try:
        os.remove(output_path)
    except FileNotFoundError:
        pass

    with ZipFile(output_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as output_zip:
        for name in sorted(input_zip.namelist()):
            if name.startswith(input_prefix) and name.endswith(".svg"):
                info = input_zip.getinfo(name)
                data = input_zip.read(name).replace(b' data-slot="icon"', b"")
                new_name = name[len(input_prefix):]
                info.filename = new_name
                output_zip.writestr(info, data)
                print(new_name)

    print("\n✅ Written!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
