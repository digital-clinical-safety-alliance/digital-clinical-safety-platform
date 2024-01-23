from django import template
import re

register = template.Library()


@register.filter(name="has_tag")
def has_tag(messages, tag):
    return any(message.tags == tag for message in messages)


@register.filter(name="starts_with")
def starts_with(messages, tag):
    return messages.startswith(tag)


@register.filter
def get(mapping, key):
    return mapping.get(key, "")
