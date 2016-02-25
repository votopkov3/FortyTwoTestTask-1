# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import Profile


def main(request):
    profile = Profile.objects.first()
    context = {'profile': profile}
    return render(request, 'hello/index.html', context)
