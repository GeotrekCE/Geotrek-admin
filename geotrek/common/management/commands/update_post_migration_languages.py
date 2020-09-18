import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from django.utils import translation

from geotrek.common.models import TargetPortal


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create models permissions"

    def execute(self, *args, **options):
        self.stdout.write("Synchronize languages after migration")
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with translation.override(lang, deactivate=True):
                TargetPortal.objects.filter(
                    **{'title_{}'.format(lang): '', 'title_{}'.format(lang): None}
                ).update(**{'title_{}'.format(lang): _('Geotrek Rando')})
                TargetPortal.objects.filter(
                    **{'description_{}'.format(lang): ''}
                ).update(**{'description_{}'.format(lang): _('Geotrek is a web app allowing you to prepare your '
                                                             'next trekking trip !')})
        self.stdout.write("Done.")
