from __future__ import annotations

from typing import Any

import django
from django.conf import settings
from django.template import Context
from django.template import Template

settings.configure(
    ROOT_URLCONF=__name__,  # Make this module the urlconf
    SECRET_KEY="insecure",
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": False,
        },
    ],
    INSTALLED_APPS=["lucide"],
)
urlpatterns: list[Any] = []
django.setup()


def test_success_icon():
    template = Template('{% load lucide %}{% lucide "a-arrow-down" %}')

    result = template.render(Context())
    assert result.startswith("<svg")
    assert result.endswith("</svg>")


def test_success_icon_path_attr():
    template = Template(
        "{% load lucide %}" + '{% lucide "a-arrow-down" stroke_linecap="butt" %}'
    )

    result = template.render(Context())
    assert result.startswith("<svg")
    assert result.endswith("</svg>")


def test_success_icon_complete():
    template = Template(
        "{% load lucide %}"
        + '{% lucide "a-arrow-down" size=48 class="h-4 w-4" '
        + 'data_test="a < 2" %}'
    )

    result = template.render(Context())
    assert result.startswith("<svg")
    assert result.endswith("</svg>")

def test_success_icon_size_none():
    template = Template("{% load lucide %}" + '{% lucide "a-arrow-down" size=None %}')

    result = template.render(Context())
    assert result.startswith("<svg")
    assert result.endswith("</svg>")
