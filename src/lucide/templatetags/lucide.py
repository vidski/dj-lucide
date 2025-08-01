from __future__ import annotations

from django import template
from django.template import Context, Template, TemplateSyntaxError
from django.utils.safestring import SafeString, mark_safe

import lucide as _lucide

register = template.Library()


@register.simple_tag(takes_context=True)  # Added takes_context=True
def lucide(context: Context, name: str, *, size: int | None = 24, **kwargs: object) -> str:
    return _render_icon(context, name, size, **kwargs)  # Pass context


def _render_icon(context: Context, name: str, size: int | None, **kwargs: object) -> str:
    processed_kwargs = {}
    for key, value in kwargs.items():
        # Original SafeString to str conversion logic
        value_to_process = value + "" if isinstance(value, SafeString) else value

        if isinstance(value_to_process, str) and \
            ("{" in value_to_process and ("{{" in value_to_process or "{%" in value_to_process)):
            # If the string value appears to contain Django template syntax,
            # try to render it using the current template context.
            try:
                # Create a Template object from the attribute value and render it
                attr_template = Template(value_to_process)
                processed_kwargs[key] = attr_template.render(context)
            except TemplateSyntaxError:
                # In case of a syntax error within the attribute's template string,
                # fall back to using the original (un-rendered) string.
                # This prevents breaking templates with unintentional or malformed template syntax in attributes.
                processed_kwargs[key] = value_to_process
        else:
            # Value is not a string or does not appear to contain template syntax.
            # Use it as is (after SafeString conversion if applicable).
            processed_kwargs[key] = value_to_process

    return mark_safe(_lucide._render_icon(name, size, **processed_kwargs))
