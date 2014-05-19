from django.core.mail import mail_managers
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test if email settings are OK by sending mail to site managers"

    def execute(self, *args, **options):

        subject = u'Test email for managers'
        message = u'If you receive this email, it seems that conf is OK !'

        mail_managers(subject, message, fail_silently=False)
