from django import template

register = template.Library()


@register.filter(name="has_tag")
def has_tag(messages, tag):
    return any(message.tags == tag for message in messages)
