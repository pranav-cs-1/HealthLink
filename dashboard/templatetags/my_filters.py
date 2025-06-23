from django import template

register = template.Library()

@register.filter(name='has_attr')
def has_attr(value, arg):
    """
    Returns True if the object 'value' has an attribute named 'arg'.
    Usage in template: {% if user|has_attr:"medicalprofessional" %}
    """
    return hasattr(value, arg)
