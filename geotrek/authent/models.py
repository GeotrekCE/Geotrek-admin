"""
    Models to manage users and profiles
"""
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils.translation import LANGUAGE_SESSION_KEY


class Structure(models.Model):
    """
    Represents an organisational structure, to which users are related.
    """
    name = models.CharField(max_length=256, verbose_name=_("Nom"))

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
    return default_structure().pk


class StructureRelated(models.Model):
    """
    A mixin used for any entities that belong to a structure
    """
    structure = models.ForeignKey(Structure, default=default_structure_pk, on_delete=models.CASCADE,
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
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE,
                                  verbose_name=_("Related structure"), blank=True, null=True)

    objects = models.Manager()
    check_structure_in_forms = True

    class Meta:
        abstract = True
        verbose_name = _("Related structures")
        verbose_name_plural = _("Related structure")


class UserProfile(StructureRelated):
    """
    A custom user profile
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True, related_name="profile",
                                on_delete=models.DO_NOTHING)
    language = models.CharField(_("Language"), max_length=10,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)

    class Meta:
        verbose_name = _("User's profile")
        verbose_name_plural = _("User's profiles")

    def __str__(self):
        return _("Profile for %s") % self.user


@receiver(user_logged_in)
def lang(sender, **kwargs):
    """ Set user's language in session when he logs in. """
    lang_code = kwargs['user'].profile.language
    kwargs['request'].session[LANGUAGE_SESSION_KEY] = lang_code
