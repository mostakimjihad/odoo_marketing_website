"""Small template helpers for the core app."""
from django import template

register = template.Library()


@register.filter(name="get_item")
def get_item(dictionary, key):
    """Return ``dictionary[key]`` or ``''`` if missing.

    Used by the home page to look up a service's workflow steps from
    the ``service_workflows`` dict keyed by service slug.
    """
    if not dictionary:
        return ""
    return dictionary.get(key, "")
