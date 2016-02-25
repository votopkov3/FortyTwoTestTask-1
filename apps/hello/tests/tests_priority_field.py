import json
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from apps.hello.models import Requests

client = Client()


class RequestPriorityFieldTest(TestCase):
    fixtures = ['initial_data.json']

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
        i = 1
        while i < 10:
            if i == 2:
                Requests.objects.create(request='test_request', priority=1)
            else:
                Requests.objects.create(request='test_request')
            i += 1
        # get list of requests
        response = client.get(reverse('hello:request_list'),
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                              content_type='application/json',)
        response_list = json.loads(response.content)
        # Test if the first entry is entry with priority 1
        self.assertEqual(response_list[0]['fields']['priority'], 1)
        # Test if the second entry has  priority 2
        self.assertEqual(response_list[1]['fields']['priority'], 0)
        # Test if the 6th request has priority 3
        self.assertEqual(response_list[2]['fields']['priority'], 0)
