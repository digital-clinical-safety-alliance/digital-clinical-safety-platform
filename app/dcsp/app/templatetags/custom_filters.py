from django import template
from typing import Mapping, Any

register = template.Library()

from app.functions.general_fuctions import (
    kebab_to_title,
)


@register.filter(name="has_tag")
def has_tag(messages: list[Any], tag: str) -> bool:
    if not messages:
        return False
    return any(message.tags == tag for message in messages)


@register.filter(name="starts_with")
def starts_with(messages: str, tag: str) -> bool:
    return messages.startswith(tag)


@register.filter(name="get")
def get(mapping: Mapping[str, str], key: str) -> str:
    return str(mapping.get(key, ""))


@register.filter(name="split")
def split(value: str, index: int) -> str:
    """
    Custom filter to return the nth element of a split using pipe '|'
    as separator.

    Usage: {{ your_string_variable|split:"index" }}
    """
    elements: list[str] = []

    if value:
        elements = value.split("|")
        if 0 <= index < len(elements):
            return elements[index]
    return ""


@register.filter(name="remove_first_element")
def remove_first_element(mapping: str) -> str:
    """Remove the first item in a list"""
    return mapping[1:]


@register.filter(name="kebab_to_title")
def kebab_to_title_filter(value: str) -> str:
    value = kebab_to_title(value)
    return value


@register.filter(name="a_an")
def choose_a_an(word: str) -> str:
    vowels = "aeiouAEIOU"
    return "an" if word and word[0] in vowels else "a"
