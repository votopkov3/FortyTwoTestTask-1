# -*- coding: utf-8 -*-
import json
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import render
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
    identify = request.POST.get('id', 1)
    try:
        profile = Profile.objects.get(id=identify)
    except ObjectDoesNotExist:
        profile = Profile.objects.first()
    form = ProfileForm(request.POST, request.FILES, instance=profile)
    logger.info(form)
    profile_to_json = {'status': "error",
                       'image_src': profile.photo.url
                       if profile and profile.photo else ' '}
    if request.POST and form.is_valid():
        try:
            form.save()
            profile_to_json['status'] = "success"
        except IntegrityError:
            profile_to_json['status'] = "error"
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
        requests_data = serializers.serialize(
            "json",
            Requests.objects.all()[:10]
        )
        requests_data = json.loads(requests_data)
        last_request = Requests.objects.order_by('-pk')[:1]
        try:
            last_request_id = [item.id for item in last_request][0]
        except IndexError:
            last_request_id = 0
        data = json.dumps(
            {'last_request_id': last_request_id,
             'requests_data': requests_data})
        return HttpResponse(data,
                            content_type="application/json")
    requests = Requests.objects.all()[:10]
    last_request = Requests.objects.order_by('-pk')[:1]
    last_request = [item.id for item in last_request][0]
    context = {'requests': requests,
               'last_request': last_request}
    return render(request, 'hello/request_list.html', context)
