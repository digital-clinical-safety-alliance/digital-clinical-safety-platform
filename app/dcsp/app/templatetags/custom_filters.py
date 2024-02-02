from django import template
import re

register = template.Library()

from app.functions.general_fuctions import kebab_to_title


@register.filter(name="has_tag")
def has_tag(messages, tag):
    return any(message.tags == tag for message in messages)


@register.filter(name="starts_with")
def starts_with(messages, tag):
    return messages.startswith(tag)


@register.filter(name="get")
def get(mapping, key):
    return mapping.get(key, "")


@register.filter(name="split")
def split(value, index):
    """
    Custom filter to return the nth element of a split using pipe '|'
    as separator.

    Usage: {{ your_string_variable|split:"index" }}
    """
    if value:
        elements = value.split("|")
        if 0 <= index < len(elements):
            return elements[index]
    return ""


@register.filter(name="remove_first_element")
def remove_first_element(mapping):
    """Remove the first item in a list"""
    return mapping[1:]


@register.filter(name="kebab_to_title")
def kebab_to_title_filter(value):
    value = kebab_to_title(value)
    return value
