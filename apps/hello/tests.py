# -*- coding: utf-8 -*-
import json
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse, NoReverseMatch
from django.test import Client, RequestFactory
from django.test import TestCase
from apps.hello.forms import ProfileForm
from apps.hello.middleware import SaveHttpRequestMiddleware
from models import Profile, Requests, LogEntrry
from django.utils.encoding import smart_unicode
from apps.hello.templatetags.hello_tags import edit_link
from django.core.management import call_command
from django.utils.six import StringIO
import subprocess
from django.template import Template, Context, TemplateSyntaxError
from django.utils import timezone as t
from PIL import Image, ImageOps
from django.conf import settings

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
        # create request
        req = Requests.objects.create(request="request")
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertIn(req, response.context['requests'])

    def test_request_content(self):
        """
        last request have to be in content
        """
        # create request
        req = Requests.objects.create(request="request")
        # get request_list
        response = client.get(reverse('hello:request_list'))
        # test entering the page
        self.assertContains(response, 'last_request="1"')

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

    def test_send_bad_image_format_cant_open(self):
        """
        Testing bad image fortmat
        Save Profile method open image and scale it
        """
        bad_file_path = settings.BASE_DIR + \
            settings.MEDIA_URL + 'test_file.doc'
        bad_file = open(bad_file_path, 'w+')
        form_data = {
            'id': 1,
            'name': 'ad2s',
            'last_name': 'admin',
            'date_of_birth': '1993-11-21',
            'email': 'smith@mail.ru',
            'jabber': 'smith@jabber.ru',
            'skype': 'sgsfdf',
            'photo': bad_file  # only this bad field
        }
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('hello:update_profile'), form_data)
        self.assertIn("error", response.content)

        # delete file from app
        default_storage.delete(bad_file_path)

    def test_send_valid_image_update_profile(self):
        """
        Testing valid image in profile form
        """

        profile = Profile.objects.get(id=1)

        # create test image
        test_image = Image.new('RGB', (1200, 1200))

        test_image_path = settings.BASE_DIR + \
            settings.MEDIA_URL + \
            'image_for_test.jpg'

        test_image.save(test_image_path)

        # get it
        valid_file = open(test_image_path)

        # test image width before put it in form
        image_width = Image.open(test_image_path).width
        self.assertEqual(image_width, 1200)

        form_data = {
            'id': 1,
            'name': 'ad2s',
            'last_name': 'admin',
            'date_of_birth': '1993-11-21',
            'email': 'smith@mail.ru',
            'jabber': 'smith@jabber.ru',
            'skype': 'sgsfdf',
        }

        valid_file_name = valid_file.name

        # upload file
        photo_file = {
            'photo': SimpleUploadedFile(
                valid_file_name, valid_file.read())}

        valid_file.close()

        # put data in form
        form = ProfileForm(
            data=form_data,
            files=photo_file,
            instance=profile
        )
        form.save()

        # test if form is valid
        self.assertEqual(form.is_valid(), True)

        # saved image path
        new_image = settings.BASE_DIR + \
            settings.MEDIA_URL + 'images/' + \
            'image_for_test.jpg'

        # open saved image
        profile_image = Image.open(new_image)

        # test image width
        self.assertEqual(profile_image.width, 200)

        # test image height
        self.assertEqual(profile_image.height, 200)

        # delete image
        default_storage.delete(new_image)
        default_storage.delete(test_image_path)


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

    def test_count_LogEntrry(self):
        """
        Must be 113 entries
        """
        self.assertEqual(LogEntrry.objects.all().count(), 93)

    def test_signals_create_entry(self):
        """
        Test entry about user create
        """
        # test status about user
        self.assertEqual(LogEntrry.objects.last().status, 'Create')

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
        self.assertEqual(LogEntrry.objects.last().status, 'Update')

    def test_signals_delete_entry(self):
        """
        Test entry about user delete
        """
        user = User.objects.get(username='signal')
        # delete user
        user.delete()
        # test if user is deleted
        self.assertEqual(LogEntrry.objects.last().status, 'Delete')

    def test_signals_not_work_on_not_allowed_model(self):
        """
        Test signal not work on not allowed model
        """
        LogEntrry.objects.create(title='Title', status="Status")
        # signal not working if LogEntrry created/updated/deleted
        # get entry about creating LogEntrry
        signal = LogEntrry.objects.last()
        # test if LogEntrry entry has not got create/update/delete
        # status
        self.assertEqual(signal.status, "Status")

    def test_signals_count_change(self):
        """
        Test signals count change
        """
        self.assertEqual(LogEntrry.objects.all().count(), 93)
        # create user to add new signal
        User.objects.create_user('create', ' ', 'create')
        self.assertEqual(LogEntrry.objects.all().count(), 94)
        # delete Saved Signals to add new signal
        LogEntrry.objects.last().delete()
        # one Saved signal delete and one added 94 -1 + 1
        self.assertEqual(LogEntrry.objects.all().count(), 94)
        # update Saved signals instance
        signal = LogEntrry.objects.last()
        signal.status = "asd"
        signal.save()
        self.assertEqual(LogEntrry.objects.all().count(), 95)

    def test_signals_create_for_its_own(self):
        """
        Create signal and test that signal create for
        its own
        """
        # create User instance to create new Saved Signals
        User.objects.create_user('create', ' ', 'create')
        # get the last saved instance(User[create, create])
        user_instance = LogEntrry.objects.last()
        # test status and name of the saved signals
        self.assertEqual(user_instance.status, 'Create')
        self.assertEqual(user_instance.title, 'User')

    def test_signals_update_for_its_own(self):
        """
        Create signal and test that signal create for
        its own
        """
        last_signal = LogEntrry.objects.last()
        last_signal.title = "asdsa"
        last_signal.save()
        # test status and name of the saved signals
        signal = LogEntrry.objects.last()
        self.assertEqual(signal.status, 'Update')
        self.assertEqual(signal.title, 'LogEntrry')

    def test_signals_delete_for_its_own(self):
        """
        Create signal and test that signal create for
        its own
        """
        LogEntrry.objects.last().delete()
        # test status and name of the saved signals
        signal = LogEntrry.objects.last()
        self.assertEqual(signal.status, 'Delete')
        self.assertEqual(signal.title, 'LogEntrry')


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

    def test_tag_with_blank_data(self):
        """
        Testing custom tag
        """
        self.assertRaises(ObjectDoesNotExist, lambda: edit_link(''))

    def test_tag_with_wrong_data(self):
        """
        Testing custom tag
        """
        self.assertRaises(ObjectDoesNotExist, lambda: edit_link(123))

    def test_tag_with_not_edit_model(self):
        """
        Testing custom tag
        """
        content_type = ContentType.objects.first()
        self.assertRaises(NoReverseMatch, lambda: edit_link(content_type))
