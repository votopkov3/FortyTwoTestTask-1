# -*- coding: utf-8 -*-
from django import template
from django.core import urlresolvers

register = template.Library()


@register.simple_tag
def edit_link(profile_id):
    url_to_admin_edit_page = urlresolvers.reverse('admin:hello_profile_change',
                                                  args=(profile_id.id,))
    return url_to_admin_edit_page
