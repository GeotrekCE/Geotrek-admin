"""
    Models to manage users and profiles
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _

from geotrek.common.mixins.models import TimeStampedModelMixin
from geotrek.common.utils import reify


class Structure(TimeStampedModelMixin, models.Model):
    """
    Represents an organisational structure, to which users are related.
    """
    name = models.CharField(max_length=256, verbose_name=_("Nom"), db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Structure")
        verbose_name_plural = _("Structures")
        ordering = ['name']
        permissions = (("can_bypass_structure", _("Can bypass structure")),)


def default_structure():
    """ Create default structure if necessary """
    return Structure.objects.get_or_create(name=settings.DEFAULT_STRUCTURE_NAME)[0]


def default_structure_pk():
    if settings.TEST:
        # test env can create multiple default structure and keep in cache already deleted
        return default_structure().pk
    structure_pk = cache.get("default_structure")
    if structure_pk:
        return int(structure_pk)
    else:
        pk = default_structure().pk
        cache.set("default_structure", str(pk))
        return pk


class StructureRelated(models.Model):
    """
    A mixin used for any entities that belong to a structure
    """
    structure = models.ForeignKey(Structure, default=default_structure_pk, on_delete=models.PROTECT,
                                  verbose_name=_("Related structure"))

    check_structure_in_forms = True

    def same_structure(self, user):
        """ Returns True if the user is in the same structure or has
            bypass_structure permission, False otherwise. """
        return (user.profile.structure == self.structure
                or user.is_superuser
                or user.has_perm('authent.can_bypass_structure'))

    class Meta:
        abstract = True
        verbose_name = _("Related structures")
        verbose_name_plural = _("Related structure")


class StructureOrNoneRelated(models.Model):
    """
    A mixin used for any entities that belong to a structure or None entity
    """
    structure = models.ForeignKey(Structure, on_delete=models.SET_NULL,
                                  verbose_name=_("Related structure"), blank=True, null=True)

    check_structure_in_forms = True

    class Meta:
        abstract = True
        verbose_name = _("Related structures")
        verbose_name_plural = _("Related structure")


class UserProfile(StructureRelated):
    """
    A custom user profile
    """
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    extended_username = models.CharField(blank=True, max_length=200, default="", verbose_name=_('Extended username'))

    class Meta:
        verbose_name = _("User's profile")
        verbose_name_plural = _("User's profiles")

    def __str__(self):
        return _("Profile for %s") % self.user


User.profile = reify(lambda u: UserProfile.objects.get_or_create(user=u)[0])
