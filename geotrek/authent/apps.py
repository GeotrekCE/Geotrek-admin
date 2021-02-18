from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from django.db.models.signals import post_migrate


def create_default_structure(sender, **kwargs):
    from geotrek.authent.models import Structure
    structure, created = Structure.objects.get_or_create(name=_('My structure'))
    if created and not Structure.objects.filter(pk=1).exists():
        structure.pk = 1
        structure.save()


class AuthentConfig(AppConfig):
    name = 'geotrek.authent'
    verbose_name = _("Authent")

    def ready(self):
        post_migrate.connect(create_default_structure, sender=self)
