# -*- coding: utf-8 -*-
import json
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from apps.hello.forms import ProfileForm
from models import Profile
from models import Requests
import logging


logger = logging.getLogger(__name__)


def main(request):
    profile = Profile.objects.first()
    user_form = ProfileForm(instance=profile)
    context = {'profile': profile, 'user_form': user_form}
    return render(request, 'hello/index.html', context)


@login_required()
def edit_profile(request):
    profile = Profile.objects.first()
    user_form = ProfileForm(instance=profile)
    context = dict(profile=profile, user_form=user_form)
    return render(request, 'hello/edit_profile.html', context)


def request_list(request):
    if request.is_ajax():
        last_request = int(request.GET.get('last_request'))
        data = serializers.serialize(
            "json",
            Requests.objects.filter(id__gt=last_request).order_by('pk')[:10]
        )
        return HttpResponse(data, content_type="application/json")
    requests = Requests.objects.all()[:10]
    context = {'requests': requests}
    return render(request, 'hello/request_list.html', context)


@login_required()
@require_POST
def update_profile(request):
    identify = request.POST.get('id')
    profile = Profile.objects.get(id=identify)
    form = ProfileForm(request.POST, request.FILES, instance=profile)
    logger.info(form)
    if form.is_valid():
        form.save()
        profile = Profile.objects.get(id=int(identify))
        profile_to_json = {'status': "success",
                           'image_src': profile.photo.url
                           if profile.photo else ''}
    else:
        profile_to_json = {'status': "error",
                           'image_src': profile.photo.url
                           if profile.photo else ' '}

    return HttpResponse(json.dumps(profile_to_json),
                        content_type="application/json")
