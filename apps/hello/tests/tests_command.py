# -*- coding: utf-8 -*-
import os
from django.test import TestCase
from apps.hello.models import Requests
from django.utils import timezone as t


class CommandTests(TestCase):
    fixtures = ['initial_data.json']

    def test_command_stdout_output(self):
        """
        Testing command
        """
        req = Requests(request='request',
                       pub_date=t.now() + t.timedelta(hours=3),
                       path='/'
                       )
        req.save()
        fin, fout = os.popen4('python manage.py model_list --stdout')
        self.assertIn('apps.hello.models.Requests',
                      fout.read())

    def test_command_stderr_output(self):
        """
        Testing command
        """
        req = Requests(request='request',
                       pub_date=t.now() + t.timedelta(hours=3),
                       path='/'
                       )
        req.save()
        fin, fout = os.popen4('python manage.py model_list --stderr')
        self.assertIn('Error: apps.hello.models.Requests',
                      fout.read())
