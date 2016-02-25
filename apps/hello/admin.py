# -*- coding: utf-8 -* -
from django.contrib import admin
from .models import Profile, Requests, LogEntrry


admin.site.register(Profile)
admin.site.register(Requests)
admin.site.register(LogEntrry)
