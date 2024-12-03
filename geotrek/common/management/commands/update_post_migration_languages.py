import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.translation import gettext as _
from django.utils import translation
from modeltranslation.utils import build_localized_fieldname

from geotrek.common.models import TargetPortal, Label

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
                    **{build_localized_fieldname('title', lang): ''}
                ).update(**{build_localized_fieldname('title', lang): _('Geotrek Rando')})
                # 'Geotrek is a web app ...' => TargetPortal description
                TargetPortal.objects.filter(
                    **{build_localized_fieldname('description', lang): ''}
                ).update(
                    **{build_localized_fieldname('description', lang): _('Geotrek is a web app allowing you to prepare your '
                                                                         'next trekking trip !')})
                self.stdout.write("Label is park centered")
                Label.objects.filter(pk=1).filter(
                    Q(**{build_localized_fieldname('name', lang): ''}) | Q(**{build_localized_fieldname('name', lang): None})
                ).update(**{build_localized_fieldname('name', lang): _('Is in the midst of the park')})
                Label.objects.filter(pk=1).filter(
                    Q(**{build_localized_fieldname('advice', lang): ''}) | Q(**{build_localized_fieldname('advice', lang): None})
                ).update(**{build_localized_fieldname('advice', lang): _('The national park is an unrestricted natural area but '
                                                                         'subjected to regulations which must be known '
                                                                         'by all visitors.')})
        self.stdout.write("Done.")
