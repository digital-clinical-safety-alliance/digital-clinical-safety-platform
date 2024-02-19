from django import template
from django.contrib import messages

from typing import Mapping, Any

register = template.Library()

from app.functions.text_manipulation import (
    kebab_to_sentense,
)


@register.filter(name="has_tag")
def has_tag(messages: list[Any], tag: str) -> bool:
    if not messages:
        return False

    if not isinstance(messages, list):
        return False

    if tag == "":
        return False

    for message in messages:
        if not hasattr(message, "tags"):
            return False

    return any(message.tags == tag for message in messages)


@register.filter(name="starts_with")
def starts_with(test_str: str, tag: str) -> bool:
    return test_str.startswith(tag)


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

    if not value:
        return ""

    if not "|" in value:
        return ""

    if not isinstance(index, int):
        return ""

    if index < 0:
        return ""

    elements = value.split("|")

    if 0 <= index < len(elements):
        return elements[index]
    else:
        return ""


@register.filter(name="remove_first_element")
def remove_first_element(mapping: str) -> str:
    """Remove the first item in a list"""
    return mapping[1:]


@register.filter(name="kebab_to_sentense")
def kebab_to_sentense_filter(value: str) -> str:
    value = kebab_to_sentense(value)
    return value


@register.filter(name="a_an")
def choose_a_an(word: str) -> str:
    if word == "":
        return ""
    vowels = "aeiouAEIOU"
    return "an" if word and word[0] in vowels else "a"
