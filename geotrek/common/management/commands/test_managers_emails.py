from django.conf import settings
from django.core.mail import mail_managers
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test if email settings are OK by sending mail to site managers"

    def execute(self, *args, **options):

        subject = u'[%s] Test email for managers' % settings.TITLE
        message = u'If you receive this email, configuration is OK !'

        mail_managers(subject, message, fail_silently=False)
