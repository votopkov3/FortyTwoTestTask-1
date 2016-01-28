# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from PIL import Image, ImageOps


class Profile(models.Model):
    url_height = models.PositiveIntegerField(editable=False, default=200)
    url_width = models.PositiveIntegerField(editable=False, default=200)
    user = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=250, default="Eneter your name")
    last_name = models.CharField(max_length=250,
                                 default="Eneter your last name")
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='images/',
                              blank=True,
                              null=True)
    bio = models.TextField(blank=True, null=True, default=" ")

    email = models.EmailField(blank=True, null=True)
    jabber = models.CharField(max_length=250, blank=True, null=True)
    skype = models.CharField(max_length=250, blank=True, null=True)
    other_contacts = models.TextField(blank=True, null=True, default=" ")

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __unicode__(self):
        return self.last_name

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        if self.photo:
            image = Image.open(self.photo)
            imagefit = ImageOps.fit(image, (200, 200), Image.ANTIALIAS)
            imagefit.save(self.photo.path, 'JPEG', quality=75)


class Requests(models.Model):
    title = models.CharField(max_length=250, default='Http_request')
    request = models.TextField()
    path = models.CharField(max_length=250, blank=True, null=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __unicode__(self):
        return self.title
