from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, NoReverseMatch
from django.test import TestCase
from apps.hello.models import Profile, Requests
from apps.hello.templatetags.hello_tags import edit_link
from django.template import Template, Context
from django.utils import timezone as t


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
        self.assertIn(u'/admin/hello/profile/',
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
        self.assertIn(u'/admin/hello/requests/',
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
