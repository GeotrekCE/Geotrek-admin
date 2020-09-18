import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from django.utils import translation

from geotrek.common.models import TargetPortal


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Post migration : update elements which was from translation before migrate (.po => models)"

    def execute(self, *args, **options):
        self.stdout.write("Update objects translation after migration from .po files")
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            self.stdout.write("Lang : {lang}".format(lang=lang))
            with translation.override(lang, deactivate=True):
                self.stdout.write("TargetPortal")
                # 'Geotrek Rando' => TargetPortal title
                TargetPortal.objects.filter(
                    **{'title_{}'.format(lang): ''}
                ).update(**{'title_{}'.format(lang): _('Geotrek Rando')})
                # 'Geotrek is a web app ...' => TargetPortal description
                TargetPortal.objects.filter(
                    **{'description_{}'.format(lang): ''}
                ).update(**{'description_{}'.format(lang): _('Geotrek is a web app allowing you to prepare your '
                                                             'next trekking trip !')})

        self.stdout.write("Done.")
