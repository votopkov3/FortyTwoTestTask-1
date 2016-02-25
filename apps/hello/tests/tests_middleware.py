from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from apps.hello.middleware import SaveHttpRequestMiddleware
from apps.hello.models import Requests


class MiddleWareTests(TestCase):

    def test_save_request(self):
        """
        Test SaveHttpRequestMiddleware()
        """
        # create client and savehttpr... instance
        # test if 10 requests in db
        self.assertEqual(Requests.objects.count(),
                         10)
        self.save_http = SaveHttpRequestMiddleware()
        self.new_request = RequestFactory().get(reverse('hello:index'))
        # save request to DB
        self.save_http.process_request(request=self.new_request)
        # test saving request to DB
        self.assertEqual(Requests.objects.count(), 11)
