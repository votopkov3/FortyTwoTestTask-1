# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from apps.hello.models import Profile

client = Client()


class ProfileMethodTests(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        user = User.objects.get(id=1)
        Profile.objects.create(name=u"Василий",
                               last_name=u"Петров",
                               date_of_birth='1993-11-29',
                               bio='biofield',
                               email='mail@mail.ru',
                               jabber='jabber',
                               skype='skype',
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

    def test_profile_static_html(self):
        """
        Testing profile shown on the page
        """
        # test profile data exist on the main page
        self.assertContains(self.response, u'Отопков')
        self.assertContains(self.response, u'Владимир')

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

    def test_non_another_profile(self):
        """
        Test if exist another profile in the page
        """
        an_profile = Profile.objects.get(id=2)
        # test if not another profile on index
        self.assertNotEqual(self.response.context['profile'],
                            an_profile)
        self.assertNotIn(an_profile.name, self.response.content)

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

    def test_profile_unicode(self):
        """
        Testing unicode profile data shown on the page
        """
        # get profile
        self.response = self.client.get(reverse('hello:index'))
        # test profile data exist on the main page
        self.assertNotIn(self.response.content, u'Отопков')
        self.assertNotIn(self.response.content, u'Владимир')
