# -*- coding: utf-8 -*-
from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    jabber = models.CharField(max_length=250, blank=True, null=True)
    skype = models.CharField(max_length=250, blank=True, null=True)
    other_contacts = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __unicode__(self):
        return self.last_name
