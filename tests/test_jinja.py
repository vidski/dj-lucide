from __future__ import annotations

from jinja2 import DictLoader
from jinja2 import Environment

from lucide.jinja import lucide


def make_environment(index_template: str) -> Environment:
    env = Environment(loader=DictLoader({"index": index_template}))
    env.globals.update(
        {
            "lucide": lucide,
        }
    )
    return env


def test_success_icon():
    env = make_environment('{{ lucide("a-arrow-down") }}')
    template = env.get_template("index")

    result = template.render()
    assert result.startswith("<svg")
    assert result.endswith("</svg>")


def test_success_icon_path_attr():
    env = make_environment('{{ lucide("a-arrow-down", stroke_linecap="butt") }}')
    template = env.get_template("index")

    result = template.render()
    assert result.startswith("<svg")
    assert result.endswith("</svg>")


def test_success_icon_complete():
    env = make_environment(
        '{{ lucide("a-arrow-down", size=48, class="h-4 w-4", ' + 'data_test="a < 2") }}'
    )
    template = env.get_template("index")

    result = str(template.render())
    assert result.startswith("<svg")
    assert result.endswith("</svg>")


def test_success_icon_size_none():
    env = make_environment('{{ lucide("a-arrow-down", size=None) }}')
    template = env.get_template("index")

    result = template.render()
    assert result.startswith("<svg")
    assert result.endswith("</svg>")
