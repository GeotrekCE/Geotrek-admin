from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from django.db.models.signals import post_migrate


def create_default_structure(sender, **kwargs):
    from geotrek.authent.models import Structure
    structure, created = Structure.objects.get_or_create(name=_('My structure'))
    if created and not Structure.objects.filter(pk=settings.DEFAULT_STRUCTURE_PK).exists():
        structure.pk = settings.DEFAULT_STRUCTURE_PK
        structure.save()


class AuthentConfig(AppConfig):
    name = 'geotrek.authent'
    verbose_name = _("Authent")

    def ready(self):
        post_migrate.connect(create_default_structure, sender=self)
