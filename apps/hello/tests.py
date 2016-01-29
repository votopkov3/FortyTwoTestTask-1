# -*- coding: utf-8 -*-
import json
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, RequestFactory
from django.test import TestCase
from apps.hello.forms import ProfileForm
from apps.hello.middleware import SaveHttpRequestMiddleware
from models import Profile, Requests, SavedSignals
from django.utils.encoding import smart_unicode
from apps.hello.templatetags.hello_tags import edit_link
from django.core.management import call_command
from django.utils.six import StringIO
import subprocess
from django.template import Template, Context
from django.utils import timezone as t


client = Client()


class ProfileMethodTests(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        Profile.objects.create(name=u"Василий", last_name=u"Петров")
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


class SaveHttpRequestTests(TestCase):

    def setUp(self):
        Requests.objects.create(request='request_1')
        Requests.objects.create(request='request_2')

    def test_request_list(self):
        """
        Testing request list view function
        """
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertEquals(response.status_code, 200)

    def test_request_list_ajax(self):
        """
        Testing request list view function
        """
        # create new 10 requests will be 12 requests in db
        i = 0
        while i < 10:
            Requests.objects.create(request='test_request')
            i += 1
        # get requests
        response = client.get(reverse('hello:request_list_ajax'),
                              content_type='application/json',
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # get first request
        request = Requests.objects.get(request='request_1')
        # get second request
        request_2 = Requests.objects.get(request='request_2')
        # test getting request list
        self.assertEquals(response.status_code, 200)
        # test first request in response content
        self.assertContains(response, request)
        # test second request in response content
        self.assertContains(response, request_2)
        # get json response and loads it
        response_list = json.loads(response.content)
        # test if 10 requests in response
        resp_list_count = sum(1 for x in response_list)
        self.assertEqual(resp_list_count, 10)

    def test_last_requests(self):
        """
        Testing the requests in the right order
        """
        # test count of requests in db
        self.assertEqual(Requests.objects.all().count(), 2)
        # test if new request is the first
        self.assertEqual(Requests.objects.first().id, 2)

    def test_save_request(self):
        """
        Test SaveHttpRequestMiddleware()
        """
        # create client and savehttpr... instance
        self.save_http = SaveHttpRequestMiddleware()
        self.new_request = RequestFactory().get(reverse('hello:index'))
        # save request to DB
        self.save_http.process_request(request=self.new_request)
        # test saving request to DB
        self.assertEqual(Requests.objects.all().count(), 3)


class SaveHttpRequestNoDataTests(TestCase):

    def test_request_list(self):
        """
        Testing request list view function
        """
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertEquals(response.status_code, 200)

    def test_request_list_ajax(self):
        """
        Testing request list view function
        """
        # get requests
        response = client.get(reverse('hello:request_list_ajax'),
                              content_type='application/json',
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

    def test_request_context(self):
        """
        1 request have to be in response hello:request_list
        """
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertEquals(str(response.context['requests']),
                          '[<Requests: Http_request>]')

    def test_request_content(self):
        """
        last request have to be in content
        """
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertContains(response, 'last_request=')

    def test_no_data_on_the_page(self):
        """
        Test shop tip that to requests in db
        """
        # delete all requests
        Requests.objects.all().delete()

        # get request_list (make ajax to not create request by middleware)
        response = client.get(reverse('hello:request_list'),
                              content_type='application/json',
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, 'No requests in DB')


class EditProfileTests(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        Profile.objects.create(
            name=u"Василий",
            last_name=u"Петров",
            user=User.objects.get(id=1))

    def test_edit_profile_html(self):
        """
        Test html on the edit profile page
        """
        # login
        self.client.login(username='admin', password='admin')
        # get edit profile page
        response = self.client.get(reverse('hello:edit_profile'))
        # test title on the page
        self.assertTrue('<h1>42 Coffee Cups Test Assignment</h1>'
                        in response.content)
        # test form on the page
        self.assertTrue('<form action="/update_profile/" method="post"'
                        ' id="update-profile-form" '
                        'enctype="multipart/form-data">'
                        in response.content)

    def test_entering_edit_profile(self):
        """
        Test enter page to edit data
        """
        # test login required
        test_login_req_response = client.get(
            reverse('hello:edit_profile')
        )
        self.assertEqual(test_login_req_response.status_code, 302)
        # login
        self.client.login(username='admin', password='admin')
        # get edit page with login user
        response = self.client.get(reverse('hello:edit_profile'))
        self.assertEqual(response.status_code, 200)
        # test if form is on the page (Save - submit button)
        self.assertContains(response, 'Save')

    def test_send_post_data_update_profile(self):
        """
        Testing update profile
        """
        form_data = {
            'id': 2,
            'name': 'admin',
            'last_name': 'admin',
            'date_of_birth': '1993-11-29',
            'email': 'mail@mail.ua',
            'jabber': 'jabber@jabber.ua',
            'skype': 'skype',
        }
        # test login required
        test_login_req_response = self.client.post(
            reverse('hello:update_profile'), form_data
        )
        self.assertEqual(test_login_req_response.status_code, 302)
        # login
        self.client.login(username='admin', password='admin')
        # test method (get not allowed)
        test_method_response = self.client.get(
            reverse('hello:update_profile')
        )
        self.assertEqual(test_method_response.status_code, 405)
        # update Vasiliy Petrov
        self.client.post(reverse('hello:update_profile'), form_data)
        # get Vasiliy Petrov profile
        profile = Profile.objects.get(id=2)
        # test if it is updated
        self.assertEqual(profile.name, 'admin')
        self.assertEqual(profile.email, 'mail@mail.ua')

    def test_send_unvalid_post_data_update_profile(self):
        """
        Testing not update profile unvalid data
        """
        form_data = {
            'id': 2,
            'name': 'ad',
            'last_name': 'admin' * 21,
            'date_of_birth': '1993-1121',
            'email': '123',
            'jabber': '123',
            'skype': '12',
        }
        form = ProfileForm(data=form_data)
        # test if form is not valid
        self.assertFalse(form.is_valid())
        self.assertIn(u'Ensure this value has at least 3 characters',
                      str(form['name'].errors))
        self.assertIn(u'Ensure this value has at most 100 characters',
                      str(form['last_name'].errors))
        self.assertIn(u'Enter a valid date',
                      str(form['date_of_birth'].errors))
        self.assertIn(u'Enter a valid email address',
                      str(form['email'].errors))
        self.assertIn(u'Enter a valid email address',
                      str(form['jabber'].errors))
        self.assertIn(u'Ensure this value has at least 3 characters',
                      str(form['skype'].errors))

    def test_send_no_post_data_update_profile(self):
        """
        Testing not update profile unvalid data
        """
        form = ProfileForm(data={})
        self.assertIn(u'This field is required',
                      str(form['id'].errors))
        self.assertIn(u'This field is required',
                      str(form['name'].errors))
        self.assertIn(u'This field is required',
                      str(form['last_name'].errors))
        self.assertIn(u'This field is required',
                      str(form['date_of_birth'].errors))
        self.assertIn(u'This field is required',
                      str(form['email'].errors))
        self.assertIn(u'This field is required',
                      str(form['jabber'].errors))
        self.assertIn(u'This field is required',
                      str(form['skype'].errors))


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


class SignalsTests(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        User.objects.create_user('signal', ' ', 'signal')

    def test_count_SavedSignals(self):
        """
        Must be 61 entries
        """
        self.assertEqual(SavedSignals.objects.all().count(), 61)

    def test_signals_create_entry(self):
        """
        Test entry about user create
        """
        # test status about user
        self.assertEqual(SavedSignals.objects.last().status, 'Create')

    def test_signals_update_entry(self):
        """
        Test entry about user update
        """
        # get user
        user = User.objects.get(username='signal')
        # update username
        user.username = 'update_signal'
        # save
        user.save()
        # test status of entry about user
        self.assertEqual(SavedSignals.objects.last().status, 'Update')

    def test_signals_delete_entry(self):
        """
        Test entry about user delete
        """
        user = User.objects.get(username='signal')
        # delete user
        user.delete()
        # test if user is deleted
        self.assertEqual(SavedSignals.objects.last().status, 'Delete')

    def test_signals_not_work_on_not_allowed_model(self):
        """
        Test signal not work on not allowed model
        """
        SavedSignals.objects.create(title='Title', status="Status")
        # signal not working if SavedSignals created/updated/deleted
        # get entry about creating SavedSignals
        signal = SavedSignals.objects.last()
        # test if SavedSignals entry has not got create/update/delete
        # status
        self.assertEqual(signal.status, "Status")


class TagTests(TestCase):
    fixtures = ['initial_data.json']

    def test_tag(self):
        """
        Testing custom tag
        """
        profile = Profile.objects.first()
        template = Template("{% load hello_tags %}"
                            "{% edit_link profile %}")
        rendered = template.render(Context({'profile': profile}))
        self.assertIn(edit_link(profile),
                      rendered)

    def test_tag_add_another_object(self):
        """
        Give request object to tag
        """
        Requests(request='request',
                 pub_date=t.now() + t.timedelta(hours=3),
                 path='/'
                 ).save()
        req = Requests.objects.first()
        template = Template("{% load hello_tags %}"
                            "{% edit_link request %}")
        rendered = template.render(Context({'request': req}))
        self.assertIn(edit_link(req),
                      rendered)

    def test_tag_on_the_page(self):
        """
        Test tag on the index page
        """
        # login
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('hello:index'))
        self.assertIn('/admin/hello/profile/', response.content)

    def test_tag_on_the_page_not_login_user(self):
        """
        Test tag on the page not login user
        """
        response = self.client.get(reverse('hello:index'))
        self.assertNotIn('/admin/hello/profile/', response.content)
