from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in


class Structure(models.Model):
    """
    Represents an organisational structure, to which users are related.
    """
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


def default_structure():
    return Structure.objects.get_or_create(name=settings.DEFAULT_STRUCTURE_NAME)[0]


class StructureRelated(models.Model):
    """
    A mixin used for any entities that belong to a structure
    """
    structure = models.ForeignKey(Structure, default=default_structure)

    @classmethod
    def forUser(cls, user):
        qs = cls.objects.get_query_set()
        return qs.filter(structure=user.profile.structure)

    class Meta:
        abstract = True


class UserProfile(StructureRelated):
    user = models.OneToOneField(User, unique=True)

    language = models.CharField(_('Language'), max_length=10,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


@receiver(user_logged_in)
def lang(sender, **kwargs):
    """ Set user's language in session when he logs in. """
    lang_code = kwargs['user'].profile.language
    kwargs['request'].session['django_language'] = lang_code
