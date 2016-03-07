# -*- coding: utf-8 -*-
import json
from django.core import serializers
from django.core.urlresolvers import reverse
from django.test import Client, RequestFactory
from django.test import TestCase
from apps.hello.middleware import SaveHttpRequestMiddleware
from apps.hello.models import Requests

client = Client()


class SaveHttpRequestTests(TestCase):

    def setUp(self):
        Requests.objects.create(request='request_1')
        Requests.objects.create(request='request_2')

    def test_request_list(self):
        """
        Testing request list view function
        """
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertEquals(response.status_code, 200)

    def test_request_list_ajax(self):
        """
        Testing request list view function
        """
        # delete all requests
        # create new 10 requests will be 11 requests in db
        Requests.objects.all().delete()
        i = 0
        while i <= 10:
            Requests.objects.create(
                request='request_1',
                path='/path_to_test'
            )
            i += 1
        # get requests
        response = client.get(reverse('hello:request_list'),
                              {'last_request': 0},  # to get 10 last requests
                              content_type='application/json',
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # test getting request list
        self.assertEquals(response.status_code, 200)
        # test first request in response content
        self.assertContains(response, '/path_to_test')
        # get json response and loads it
        response_list = json.loads(response.content)
        # test if 10 requests in response
        self.assertEqual(len(response_list), 10)

        # test queryset
        requests = serializers.serialize(
            "json",
            Requests.objects.filter(id__gt=0).order_by('pk')[:10]
        )
        self.assertEqual(response.content, requests)

    def test_last_requests(self):
        """
        Testing the requests in the right order
        """
        # test count of requests in db
        self.assertEqual(Requests.objects.all().count(), 2)
        # test if new request is the first
        self.assertEqual(Requests.objects.first().id, 2)

    def test_save_request(self):
        """
        Test SaveHttpRequestMiddleware()
        """
        # create client and savehttpr... instance
        self.save_http = SaveHttpRequestMiddleware()
        self.new_request = RequestFactory().get(reverse('hello:index'))
        # save request to DB
        self.save_http.process_request(request=self.new_request)
        # test saving request to DB
        self.assertEqual(Requests.objects.all().count(), 3)


class SaveHttpRequestNoDataTests(TestCase):

    def test_request_list(self):
        """
        Testing request list view function
        """
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertEquals(response.status_code, 200)

    def test_request_list_ajax(self):
        """
        Testing request list view function
        """
        # get requests
        response = client.get(reverse('hello:request_list'),
                              {'last_request': 0},
                              content_type='application/json',
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

    def test_request_context(self):
        """
        1 request have to be in response hello:request_list
        """
        # create request
        req = Requests.objects.create(request="request")
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertIn(req, response.context['requests'])

    def test_request_content(self):
        """
        last request have to be in content
        """
        # create request
        Requests.objects.create(request="request")
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertContains(response, 'last_request="1"')
