# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = patterns('',
                       url(r'^$', views.main, name='index'),
                       url(r'^request_list/$', views.request_list,
                           name='request_list'),
                       url(r'^edit_profile/$', views.edit_profile,
                           name='edit_profile'),
                       url(r'^login/$', auth_views.login, name='login'),
                       url(r'^logout/$', auth_views.logout, {
                           'next_page': '/'
                       }, name='logout'),
                       )
