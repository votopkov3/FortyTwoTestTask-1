# -*- coding: utf-8 -* -
import datetime
from models import Requests


class SaveHttpRequestMiddleware(object):

    def process_request(self, request):
        if request.is_ajax():
            return None
        save_request = Requests(request=request,
                                pub_date=datetime.datetime.now(

                                ) + datetime.timedelta(hours=2),
                                path=request.build_absolute_uri())
        return save_request.save()
