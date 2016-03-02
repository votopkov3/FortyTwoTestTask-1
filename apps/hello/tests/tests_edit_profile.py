# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase
from apps.hello.forms import ProfileForm
from apps.hello.models import Profile
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from io import BytesIO


client = Client()


class EditProfileTests(TestCase):
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
        # test if form is on the page (Save - submit button)
        self.assertContains(response, 'Save')

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

    def test_send_post_data_update_profile(self):
        """
        Testing update profile
        """
        form_data = {
            'id': 2,
            'name': 'admin',
            'last_name': 'admin',
            'date_of_birth': '1993-11-29',
            'bio': 'my bio',
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
            'bio': 's',
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
        self.assertIn(u'Ensure this value has at least 3 characters',
                      str(form['bio'].errors))

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
        self.assertIn(u'This field is required',
                      str(form['bio'].errors))

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


class EditProfileImageFieldTests(TestCase):
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

    def tearDown(self):
        # delete image
        self.profile_obj.photo.delete()

    def test_send_valid_image_update_profile(self):
        """
        Testing valid image in profile form
        """

        # create test image
        file_obj = BytesIO()
        test_image = Image.new('RGB', size=(1200, 1200))

        test_image.save(file_obj, 'JPEG')
        file_obj.name = 'test.jpg'
        file_obj.seek(0)
        # test image width before put it in form
        image_width = Image.open(file_obj).width
        self.assertEqual(image_width, 1200)

        photo_file = SimpleUploadedFile(
                name='test.jpg', content=file_obj.getvalue())

        form_data = {
            'id': 1,
            'name': 'ad2s',
            'last_name': 'admin',
            'date_of_birth': '1993-11-21',
            'bio': 'my bio',
            'email': 'smith@mail.ru',
            'jabber': 'smith@jabber.ru',
            'skype': 'sgsfdf',
            'photo': photo_file
        }

        # login
        self.client.login(username='admin', password='admin')

        self.client.post(
            reverse('hello:update_profile'),
            form_data,
        )

        self.profile_obj = Profile.objects.first()

        # open saved image
        profile_image = Image.open(self.profile_obj.photo)

        # test image width
        self.assertEqual(profile_image.width, 200)

        # test image height
        self.assertEqual(profile_image.height, 200)

    def test_aspect_ratio_update_profile(self):
        """
        Testing valid image in profile form
        """
        # login
        self.client.login(username='admin', password='admin')

        # create test image
        file_obj = BytesIO()
        test_image = Image.new('RGB', size=(1200, 200))

        test_image.save(file_obj, 'JPEG')
        file_obj.name = 'test.jpg'
        file_obj.seek(0)
        # test image width before put it in form
        image_height = Image.open(file_obj).height
        self.assertEqual(image_height, 200)

        photo_file = SimpleUploadedFile(
                name='test.jpg', content=file_obj.getvalue())

        form_data = {
            'id': 1,
            'name': 'ad2s',
            'last_name': 'admin',
            'date_of_birth': '1993-11-21',
            'bio': 'my bio',
            'email': 'smith@mail.ru',
            'jabber': 'smith@jabber.ru',
            'skype': 'sgsfdf',
            'photo': photo_file
        }

        # login
        self.client.login(username='admin', password='admin')

        self.client.post(
            reverse('hello:update_profile'),
            form_data,
        )

        self.profile_obj = Profile.objects.first()

        # open saved image
        profile_image = Image.open(self.profile_obj.photo)

        # test image width
        self.assertEqual(profile_image.width, 200)

        # test image height
        self.assertEqual(profile_image.height, 33)
