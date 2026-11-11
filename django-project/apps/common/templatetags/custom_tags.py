from django import template
from django.urls import resolve, reverse, Resolver404, NoReverseMatch
from django.utils import translation

register = template.Library()

@register.filter
def get_obj_attr(obj, attr_path):
    """
    Get attribute from object by path like 'customer_info.name' or 'customer_info__name'
    """
    try:
        # Change __ to . for nested attribute
        # Example: customer_info__name -> customer_info.name
        path = attr_path.replace('__', '.')
        for part in path.split('.'):
            obj = getattr(obj, part)
        return obj
    except (AttributeError, TypeError):
        return ""


@register.simple_tag(takes_context=True)
def change_lang(context, lang=None, *args, **kwargs):
    """
    Get active page's url by a specified language
    Usage: {% change_lang 'en' %}
    """
    path = context['request'].path
    url_parts = resolve(path)

    url = path
    cur_language = translation.get_language()
    try:
        translation.activate(lang)
        url = reverse(url_parts.view_name, kwargs=url_parts.kwargs)
    except Resolver404:
        # Fallback to the current path if resolution fails (e.g. 404 page)
        pass
    except Exception:
        pass
    finally:
        translation.activate(cur_language)

    return url
