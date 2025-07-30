from django import template

register = template.Library()

@register.filter
def replace_br(value):
    """Replaces slashes with <br>"""
    return value.replace('/', '<br>')
