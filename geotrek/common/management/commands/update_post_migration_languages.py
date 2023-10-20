import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.translation import gettext as _
from django.utils import translation

from geotrek.common.models import TargetPortal, Label

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Post migration : update elements which was from translation before migrate (.po => models)"

    def execute(self, *args, **options):
        self.stdout.write("Update objects translation after migration from .po files")
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            correct_lang = lang.replace('-', '_')
            self.stdout.write("Lang : {lang}".format(lang=lang))
            with translation.override(lang, deactivate=True):
                self.stdout.write("TargetPortal")
                # 'Geotrek Rando' => TargetPortal title
                TargetPortal.objects.filter(
                    **{'title_{}'.format(correct_lang): ''}
                ).update(**{'title_{}'.format(correct_lang): _('Geotrek Rando')})
                # 'Geotrek is a web app ...' => TargetPortal description
                TargetPortal.objects.filter(
                    **{'description_{}'.format(correct_lang): ''}
                ).update(
                    **{'description_{}'.format(correct_lang): _('Geotrek is a web app allowing you to prepare your '
                                                                'next trekking trip !')})
                self.stdout.write("Label is park centered")
                Label.objects.filter(pk=1).filter(
                    Q(**{'name_{}'.format(correct_lang): ''}) | Q(**{'name_{}'.format(correct_lang): None})
                ).update(**{'name_{}'.format(correct_lang): _('Is in the midst of the park')})
                Label.objects.filter(pk=1).filter(
                    Q(**{'advice_{}'.format(correct_lang): ''}) | Q(**{'advice_{}'.format(correct_lang): None})
                ).update(**{'advice_{}'.format(correct_lang): _('The national park is an unrestricted natural area but '
                                                                'subjected to regulations which must be known '
                                                                'by all visitors.')})
        self.stdout.write("Done.")
