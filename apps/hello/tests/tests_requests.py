import json
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
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
        Requests.objects.all().delete()
        # create new 10 requests will be 12 requests in db
        i = 0
        while i <= 10:
            Requests.objects.create(
                request='request_1',
                path='/'
            )
            i += 1
        # get requests
        response = client.get(reverse('hello:request_list'),
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
        self.assertEqual(len(response_list), 10)

        # test queryset
        requests = serializers.serialize(
            "json",
            Requests.objects.filter(id__gt=0).reverse()[:10]
        )
        self.assertEqual(response.content, requests)

    def test_last_requests(self):
        """
        Testing the requests in the right order
        """
        # test count of requests in db
        self.assertEqual(Requests.objects.count(), 12)
        # test if new request is the first
        self.assertEqual(Requests.objects.first().id, 12)


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
                              content_type='application/json',
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

    def test_request_context(self):
        """
        1 request have to be in response hello:request_list
        """
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        req = Requests.objects.first()
        self.assertIn(req, response.context['requests'])

    def test_request_content(self):
        """
        last request have to be in content
        """
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertContains(response, 'last_request="10"')
