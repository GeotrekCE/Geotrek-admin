from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from easy_thumbnails.models import Thumbnail

from geotrek.common.models import Attachment


class Command(BaseCommand):
    help = "Remove files for deleted attachments"

    def handle(self, *args, **options):
        paperclip_dir = Path(settings.MEDIA_ROOT) / "paperclip"
        attachments = set(Attachment.objects.values_list("attachment_file", flat=True))
        thumbnails = set(Thumbnail.objects.values_list("name", flat=True))
        if options["verbosity"] >= 1:
            self.stdout.write(
                f"Attachments: {len(attachments)} / Thumbnails: {len(thumbnails)}"
            )
        total = 0
        deleted = 0
        for path in paperclip_dir.glob("**/*"):
            if not path.is_file():
                continue
            total += 1
            relative = str(path.relative_to(settings.MEDIA_ROOT))
            if relative in attachments:
                if options["verbosity"] >= 2:
                    self.stdout.write(f"{relative}... Found")
                continue
            if relative in thumbnails:
                if options["verbosity"] >= 2:
                    self.stdout.write(f"{relative}... Thumbnail")
                continue
            deleted += 1
            path.unlink()
            if options["verbosity"] >= 1:
                self.stdout.write(f"{relative}... DELETED")
        if options["verbosity"] >= 1:
            self.stdout.write(f"Files: {total} / Deleted: {deleted}")
