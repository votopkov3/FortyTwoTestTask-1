# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase
from models import Profile

client = Client()


class ProfileMethodTests(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        Profile.objects.create(name=u"Василий",
                               last_name=u"Петров",
                               date_of_birth='1993-11-29',
                               bio='biofield',
                               email='mail@mail.ru',
                               jabber='jabber',
                               skype='skype')
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
        self.assertContains(self.response, profile.last_name)
        self.assertContains(self.response, profile.name)
        self.assertContains(self.response,
                            profile.date_of_birth.strftime("%b. %d, %Y"))
        self.assertContains(self.response, profile.bio)
        self.assertContains(self.response, profile.jabber)
        self.assertContains(self.response, profile.skype)
        self.assertContains(self.response, profile.email)

    def test_profile_static_html(self):
        """
        Testing profile shown on the page
        """
        # test profile data exist on the main page
        self.assertContains(self.response, u'Отопков')
        self.assertContains(self.response, u'Владимир')
        self.assertContains(self.response,
                            'Nov. 29, 1993')
        self.assertContains(self.response,
                            u'Меня зовут Владимир')
        self.assertContains(self.response,
                            '_smith_@khavr.com')
        self.assertContains(self.response, 'gashik_3')
        self.assertContains(self.response,
                            'votopkov.webmaster@gmail.com')

    def test_profile_static_enter_html(self):
        """
        Testing profile shown on the page
        """
        # test profile data exist on the main page
        self.assertNotContains(self.response, 'Георгий')
        self.assertNotContains(self.response, 'Петров')
        self.assertNotContains(self.response,
                               'Меня зовут Георгий')
        self.assertNotContains(self.response,
                               'votopkov@gmail.com')
        self.assertNotContains(self.response,
                               'smith@khavr.com')

    def test_non_another_profile(self):
        """
        Test if exist another profile in the page
        """
        # test if not another profile on index
        self.assertNotEqual(self.response.context['profile'],
                            Profile.objects.get(id=2))
        self.assertNotIn('Василий', self.response.content)

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
