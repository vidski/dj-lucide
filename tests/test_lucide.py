from __future__ import annotations

import os
import shutil
import tempfile
from xml.etree import ElementTree

import pytest
from django.test import override_settings

import lucide


def test_load_icon_success_outline():
    svg = lucide._load_icon("a-arrow-down")
    assert isinstance(svg, ElementTree.Element)
    assert svg.tag == ElementTree.QName("svg")


def test_load_icon_success_solid():
    svg = lucide._load_icon("a-arrow-down")
    assert isinstance(svg, ElementTree.Element)
    assert svg.tag == ElementTree.QName("svg")


def test_load_icon_success_mini():
    svg = lucide._load_icon("a-arrow-down")
    assert isinstance(svg, ElementTree.Element)
    assert svg.tag == ElementTree.QName("svg")


def test_load_icon_fail_unknown():
    with pytest.raises(lucide.IconDoesNotExist) as excinfo:
        lucide._load_icon("hoome")

    assert excinfo.value.args == ("The icon 'hoome' does not exist.",)


def make_fake_zip_with_icon(icon_name: str, svg_content: str, path: str):
    from zipfile import ZipFile
    with ZipFile(path, "w") as z:
        z.writestr(f"{icon_name}.svg", svg_content)


def test_icon_loading_from_custom_zip():
    tmp = tempfile.mkdtemp()
    try:
        zip_path = os.path.join(tmp, "lucide-latest.zip")
        ICON = "testicon"
        SVG = '<svg width="24" height="24"><path d="M0 0h24v24H0z"/></svg>'
        make_fake_zip_with_icon(ICON, SVG, zip_path)

        with override_settings(LUCIDE_ICONS_ZIP_PATH=zip_path):
            lucide._load_icon.cache_clear()  # Clear cache for deterministic test
            el = lucide._load_icon(ICON)
            assert el.tag == "svg"
            assert el.attrib["width"] == "24"
    finally:
        shutil.rmtree(tmp)


def test_icon_loading_fallback():
    # This test checks the fallback to built-in zip
    # The default lucide tests already exercise this,
    # but you can still explicitly call without override
    lucide._load_icon.cache_clear()
    el = lucide._load_icon("a-arrow-down")
    assert el.tag == "svg"
