from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active(context, url_name):
    """
    Returns 'active' if the current request.path matches or starts with the reversed URL.
    """
    request = context.get('request', None)  # Ambil request dari context
    if not request:
        return ''  # Jika tidak ada request, kembalikan string kosong

    try:
        url = reverse(url_name)  # URL dari nama view
        if request.path.startswith(url):  # Cocokkan request.path
            return 'active'
    except NoReverseMatch:
        # Jika url_name tidak valid, kembalikan string kosong
        return ''
    return ''

