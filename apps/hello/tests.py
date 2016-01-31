# -*- coding: utf-8 -*-
import json
from django.core.urlresolvers import reverse
from django.test import Client, RequestFactory
from django.test import TestCase
from apps.hello.middleware import SaveHttpRequestMiddleware
from models import Profile, Requests
from django.utils.encoding import smart_unicode

client = Client()


class ProfileMethodTests(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        Profile.objects.create(name=u"Василий", last_name=u"Петров")
        # get main page
        self.response = self.client.get(reverse('hello:index'))

    def test_enter_main_page(self):
        """
        Test entering main page
        """
        # if index page exists
        self.assertEqual(self.response.status_code, 200)

    def test_profile(self):
        """
        Testing profile shown in the page
        """
        # get profile
        profile = Profile.objects.first()
        # test context main view
        self.assertEqual(self.response.context['profile'], profile)
        # test profile data exist on the main page
        self.assertContains(self.response, u'Отопков')
        self.assertContains(self.response, u'Владимир')

    def test_non_another_profile(self):
        """
        Test if exist another profile in the page
        """
        # test if not another profile on index
        self.assertNotEqual(self.response.context['profile'],
                            Profile.objects.get(id=2))
        self.assertNotIn('Василий', self.response.content)

    def test_unicode(self):
        """
        Test unicode data on the page
        """
        profile = Profile.objects.first()
        self.assertEqual(smart_unicode(profile), u'Отопков')

    def test_db_entries_count(self):
        """
        Test db entries
        """
        profile = Profile.objects.all().count()
        # one profile in fixtures and one in setUp
        self.assertEqual(profile, 2)

    def test_admin(self):
        """
        Test getting admin page
        """
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

    def test_admin_login(self):
        """
        Testing admin login
        """
        admin = {'name': 'admin',
                 'password': 'admin'}
        response = self.client.post(reverse('admin:index'), admin)
        self.assertEqual(response.status_code, 200)

    def test_index_html(self):
        """
        Testing valid html on the page
        """
        response = self.client.get(reverse('hello:index'))
        self.assertTemplateUsed(response, 'hello/index.html')
        self.assertTrue('<h1>42 Coffee Cups Test Assignment</h1>'
                        in response.content)


class ProfileNoDataMethodTests(TestCase):

    def setUp(self):
        Profile.objects.all().delete()
        # get main page
        self.response = self.client.get(reverse('hello:index'))

    def test_enter_main_page(self):
        """
        Test entering main page
        """
        # if index page exists
        self.assertEqual(self.response.status_code, 200)

    def test_profile(self):
        """
        Testing profile shown in the page
        """
        # get profile
        profile = Profile.objects.all().count()
        self.assertEqual(profile, 0)
        # test profile data exist on the main page
        self.assertNotContains(self.response, u'Отопков')
        self.assertNotContains(self.response, u'Владимир')

    def test_db_entries_count(self):
        """
        Test db entries
        """
        profile = Profile.objects.all().count()
        self.assertEqual(profile, 0)


class SaveHttpRequestTests(TestCase):

    def setUp(self):
        Requests.objects.create(
            request='request_1',
            path='/'
        )
        Requests.objects.create(
            request='request_2',
            path='/'
        )

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
        # create new 10 requests will be 12 requests in db
        i = 0
        while i < 10:
            Requests.objects.create(
                request='request_1',
                path='/'
            )
            i += 1
        # get requests
        response = client.get(reverse('hello:request_list_ajax'),
                              content_type='application/json',
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # get first request
        request = Requests.objects.get(id=1)
        # get second request
        request_2 = Requests.objects.get(id=2)
        # test getting request list
        self.assertEquals(response.status_code, 200)
        # test first request in response content
        self.assertContains(response, request)
        # test second request in response content
        self.assertContains(response, request_2)
        # get json response and loads it
        response_list = json.loads(response.content)
        # test if 10 requests in response
        resp_list_count = sum(1 for x in response_list)
        self.assertEqual(resp_list_count, 10)

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
        self.new_request = RequestFactory().get(reverse(
            'hello:index'))
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

    def test_request_context(self):
        """
        1 request have to be in response hello:request_list
        """
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertEquals(str(response.context['requests']),
                          '[<Requests: Http_request>]')

    def test_request_content(self):
        """
        last request have to be in content
        """
        i = 1
        while i < 10:
            Requests.objects.create(
                request='request_1',
                path='/'
            )
            i += 1
        # get request_list
        response = client.get(reverse('hello:request_list'))
        print(response.content)
        # test entering the page
        self.assertContains(response, 'last_request=10')

    def test_no_data_on_the_page(self):
        """
        Test shop tip that to requests in db
        """
        # delete all requests
        Requests.objects.all().delete()
        # get request_list (make ajax to not create request by middleware)
        response = client.get(reverse('hello:request_list'),
                              content_type='application/json',
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, 'No requests in DB')

    def test_request_list_ajax(self):
        """
        Testing request list view function
        """
        # get requests
        response = client.get(reverse('hello:request_list_ajax'),
                              content_type='application/json',
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

