from django.core.urlresolvers import reverse
from django.test import RequestFactory
from apps.hello.middleware import SaveHttpRequestMiddleware
from apps.hello.models import Requests


def test_save_request(self):
        """
        Test SaveHttpRequestMiddleware()
        """
        # test if 12 request in db
        self.assertEqual(Requests.objects.count(), 12)
        # create client and savehttpr... instance
        self.save_http = SaveHttpRequestMiddleware()
        self.new_request = RequestFactory().get(reverse(
            'hello:index'))
        # save request to DB
        self.save_http.process_request(request=self.new_request)
        # test saving request to DB
        self.assertEqual(Requests.objects.count(), 13)
