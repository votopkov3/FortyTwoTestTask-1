import json
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from apps.hello.models import Requests

client = Client()


class RequestPriorityFieldTest(TestCase):

    def test_request_priority_field(self):
        """
        Test priority ordering
        at first order by -pub_date, then priority
        They all have default priority - 0
        """
        # I will make it the last by adding to it priority 1
        #  Create four requests
        Requests.objects.create(request='request')
        Requests.objects.create(request='request')
        Requests.objects.create(request='request')
        Requests.objects.create(request='request')
        # get request with id - 3

        req = Requests.objects.get(id=3)
        # get first request
        req_first = Requests.objects.first()
        # test if they are not equal
        self.assertNotEqual(req.id, req_first.id)
        # add to request with id-7 priority 1
        req.priority = 1
        # save it
        req.save()
        # get first request after
        # adding priority to request with id - 3
        new_req_first = Requests.objects.first()
        self.assertEqual(req.id, new_req_first.id)

    def test_priority_on_request_list_page(self):
        """
        Test ordering by priority on the page
        """
        # add 10 new quests to get valid json response
        Requests.objects.all().delete()
        i = 1
        while i <= 10:
            if i == 10:
                Requests.objects.create(request='test_request',
                                        priority=1)
            else:
                Requests.objects.create(request='test_request')
            i += 1
        response = client.get(reverse('hello:request_list'),
                              {'last_request': 0},
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                              content_type='application/json')
        response_list = json.loads(response.content)
        # set the last request priority 1
        self.assertEqual(
            response_list['requests_data'][0]['fields']['priority'], 1)
        # Test if other priority has default values
        self.assertEqual(
            response_list['requests_data'][1]['fields']['priority'], 0)
        self.assertEqual(
            response_list['requests_data'][2]['fields']['priority'], 0)
