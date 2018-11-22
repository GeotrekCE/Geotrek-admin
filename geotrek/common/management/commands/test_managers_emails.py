from django.core.mail import mail_managers
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test if email settings are OK by sending mail to site managers"

    def handle(self, *args, **options):

        subject = 'Test email for managers'
        message = 'If you receive this email, configuration is OK !'

        mail_managers(subject, message, fail_silently=False)
