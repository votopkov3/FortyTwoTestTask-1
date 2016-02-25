# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.utils.encoding import smart_unicode
from apps.hello.models import Profile

client = Client()


class ProfileMethodTests(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        user = User.objects.get(id=1)
        Profile.objects.create(name=u"Василий",
                               last_name=u"Петров",
                               user=user)
        # get main page
        self.response = self.client.get(reverse('hello:index'))

    def test_profile_context(self):
        """
        Test profile context
        """
        profile = Profile.objects.first()
        self.assertEqual(self.response.context['profile'],
                         profile)

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

    def test_index_template(self):
        """
        Testing valid html on the page
        """
        response = self.client.get(reverse('hello:index'))
        self.assertTemplateUsed(response, 'hello/index.html')

    def test_request_list_template(self):
        """
        Testing valid html on the page
        """
        response = self.client.get(reverse('hello:request_list'))
        self.assertTemplateUsed(response, 'hello/request_list.html')

    def test_edit_profile_template(self):
        """
        Testing valid html on the page
        """
        # login required
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('hello:edit_profile'))
        self.assertTemplateUsed(response, 'hello/edit_profile.html')


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
