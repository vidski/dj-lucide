from __future__ import annotations

import os
import shutil
import tempfile
from xml.etree import ElementTree

import lucide
import pytest
from django.template import Template, Context
from django.test import override_settings
from django.utils.safestring import mark_safe
from lucide.templatetags import lucide as tagmod


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


def test_tag_happy_with_safestring(monkeypatch):
    # ensure happy path and SafeString conversion branch run
    tpl = Template('{% load lucide %}{% lucide "a-arrow-down" class=klass data_test=dt %}')
    out = tpl.render(Context({"klass": mark_safe("h-4 w-4"), "dt": mark_safe("v")}))
    assert out.startswith("<svg")
    assert out.endswith("</svg>")
    assert 'class="h-4 w-4"' in out
    assert 'data-test="v"' in out  # underscores -> dashes handled in core render


def test_tag_fallback_to_alert_triangle(monkeypatch):
    # Force first call to fail, second (alert-triangle) to succeed
    def fake_render(name, size, **kw):
        if name == "missing-icon":
            raise KeyError("nope")
        if name == "alert-triangle":
            return "<svg><path d='fallback'/></svg>"
        raise AssertionError("unexpected icon")

    monkeypatch.setattr(tagmod._lucide, "_render_icon", fake_render)
    tpl = Template('{% load lucide %}{% lucide "missing-icon" %}')
    out = tpl.render(Context())
    assert out == "<svg><path d='fallback'/></svg>"


def test_tag_double_fallback_to_span(monkeypatch):
    # Force both original and alert-triangle to fail
    def always_fail(*a, **kw):
        raise KeyError("nope")

    monkeypatch.setattr(tagmod._lucide, "_render_icon", always_fail)
    tpl = Template('{% load lucide %}{% lucide "still-missing" %}')
    out = tpl.render(Context())
    assert out == "<span class='lucide-fallback'>still-missing</span>"
