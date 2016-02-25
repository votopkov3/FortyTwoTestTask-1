# -*- coding: utf-8 -*-
from django.utils.six import StringIO
from django.core.management import call_command
from django.test import TestCase
import subprocess
from apps.hello.models import Requests
from django.utils import timezone as t


class CommandTests(TestCase):
    fixtures = ['initial_data.json']

    def test_command_output(self):
        """
        Testing command
        """
        req = Requests(request='request',
                       pub_date=t.now() + t.timedelta(hours=3),
                       path='/'
                       )
        req.save()
        out = StringIO()  # flake8: noqa
        call_command('model_list', stderr=out)
        self.assertIn('apps.hello.models.Requests',
                      out.getvalue())

    def test_model_list_script(self):
        """
        Testing command by executing models_lish.sh
        """
        out = subprocess.Popen("./model_list.sh",
                               stderr=subprocess.PIPE,
                               shell=True)
