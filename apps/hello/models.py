# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from PIL import Image


class Profile(models.Model):
    url_height = models.PositiveIntegerField(editable=False, default=200)
    url_width = models.PositiveIntegerField(editable=False, default=200)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=250, default="Eneter your name")
    last_name = models.CharField(max_length=250,
                                 default="Eneter your last name")
    date_of_birth = models.DateField()
    photo = models.ImageField(upload_to='images/',
                              blank=True,
                              null=True)
    bio = models.TextField()

    email = models.EmailField()
    jabber = models.CharField(max_length=250)
    skype = models.CharField(max_length=250)
    other_contacts = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __unicode__(self):
        return self.last_name

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        if self.photo:
            image = Image.open(self.photo)
            image.thumbnail((200, 200), Image.ANTIALIAS)
            image.save(self.photo.path, 'JPEG', quality=75)


class Requests(models.Model):
    title = models.CharField(max_length=250, default='Http_request')
    request = models.TextField()
    path = models.CharField(max_length=250, blank=True, null=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __unicode__(self):
        return self.title
