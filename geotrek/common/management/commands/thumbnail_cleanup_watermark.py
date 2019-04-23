from django.core.management.base import BaseCommand

from geotrek.common.models import BaseAttachment


class Command(BaseCommand):
    help = "Unset structure in lists of choices and group choices with the same name."

    def handle(self, *args, **options):
        attachments = BaseAttachment.objects.all()
        for attachment in attachments:
            attachment.update()
        if options['verbosity'] > 1:
            self.stdout.write('{attachments} updated'.format(attachments=attachments.count()))
