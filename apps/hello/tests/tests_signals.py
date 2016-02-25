from django.contrib.auth.models import User
from apps.hello.models import LogEntrry
from django.test import TestCase


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
