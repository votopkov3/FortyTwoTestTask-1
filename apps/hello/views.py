# -*- coding: utf-8 -*-
import json
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http.response import HttpResponse
from django.shortcuts import render
from apps.hello.forms import ProfileForm
from models import Profile
from models import Requests
import logging
from django.core.exceptions import ObjectDoesNotExist


logger = logging.getLogger(__name__)


def main(request):
    profile = Profile.objects.first()
    user_form = ProfileForm(instance=profile)
    context = {'profile': profile, 'user_form': user_form}
    return render(request, 'hello/index.html', context)


@login_required()
def edit_profile(request):
    identify = request.POST.get('id', 1)
    try:
        profile = Profile.objects.get(id=identify)
    except ObjectDoesNotExist:
        profile = Profile.objects.first()
    form = ProfileForm(request.POST, request.FILES, instance=profile)
    logger.info(form)
    profile_to_json = {'status': "error",
                       'image_src': profile.photo.url
                       if profile.photo else ' '}
    if request.POST and form.is_valid():
        form.save()
        profile_to_json['status'] = "success"
        return HttpResponse(json.dumps(profile_to_json),
                            content_type="application/json")
    if request.POST and not form.is_valid():
        return HttpResponse(json.dumps(profile_to_json),
                            content_type="application/json")
    user_form = ProfileForm(instance=profile)
    context = dict(profile=profile, user_form=user_form)
    return render(request, 'hello/edit_profile.html', context)


def request_list(request):
    if request.is_ajax():
        last_request = int(request.GET.get('last_request'))
        data = serializers.serialize(
            "json",
            Requests.objects.filter(id__gt=last_request).reverse()[:10]
        )
        return HttpResponse(data, content_type="application/json")
    requests = Requests.objects.all()[:10]
    context = {'requests': requests}
    return render(request, 'hello/request_list.html', context)
