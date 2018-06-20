# coding=utf-8
from django import template

register = template.Library()


@register.filter(expects_localtime=True, is_safe=True)
def check_perms(perm_obj):
    pass


@register.filter(expects_localtime=True, is_safe=True)
def status_css_selector(status):
    success = ('available', 'active', 'in-use')
    warning = ('creating', 'attaching')
    error = ('error', 'deleted')
    if status in success:
        return 'success'
    elif status in warning:
        return 'warning'
    elif status in error:
        return 'danger'
    else:
        return 'primary'


@register.filter(is_safe=True)
def label_css_decorator(label, cls):
    return label.label_tag(attrs={'class': cls})
