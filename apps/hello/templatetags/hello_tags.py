# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def edit_link(object):
    """
    Get object and render link to it admin edit page
    """
    return reverse('admin:%s_%s_change' % (object._meta.app_label,
                                           object.__class__.__name__.lower()),
                   args=(object.id,))
