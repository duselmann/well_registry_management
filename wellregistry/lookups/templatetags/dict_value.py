from django import template


register = template.Library()


@register.simple_tag(name='dict_value')
def dict_value(a_dict, key):
    """Try to fetch from the dict, and if it's not found return an empty string."""
    return a_dict.get(key, '')
