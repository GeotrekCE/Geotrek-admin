import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.translation import gettext as _
from django.utils import translation

from geotrek.common.models import TargetPortal

if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from geotrek.trekking.models import LabelTrek

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
                if 'geotrek.trekking' in settings.INSTALLED_APPS:
                    self.stdout.write("LabelTrek")
                    LabelTrek.objects.filter(
                        Q(**{'name_{}'.format(lang): ''}) | Q(**{'name_{}'.format(lang): None})
                    ).update(**{'name_{}'.format(lang): _('Is in the midst of the park')})
                    LabelTrek.objects.filter(
                        Q(**{'advice_{}'.format(lang): ''}) | Q(**{'advice_{}'.format(lang): None})
                    ).update(**{'advice_{}'.format(lang): _('The national park is an unrestricted natural area but '
                                                            'subjected to regulations which must be known '
                                                            'by all visitors.')})
        self.stdout.write("Done.")
