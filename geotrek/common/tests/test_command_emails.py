import tempfile

from django.core.management import call_command
from django.test import TestCase
from django.core import mail
from django.conf import settings


class CommandTests(TestCase):
    def test_command_emails_manager(self):
        call_command('test_managers_emails')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, u'[%s] Test email for managers' % settings.TITLE)
