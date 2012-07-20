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
    name = models.CharField(max_length=256, verbose_name=_(u"Nom"))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Structure")
        verbose_name_plural = _(u"Structures")


def default_structure():
    return Structure.objects.get_or_create(name=settings.DEFAULT_STRUCTURE_NAME)[0]


class StructureRelatedManager(models.Manager):
    def byUser(self, user):
        qs = super(StructureRelatedManager, self).get_query_set()
        return qs.filter(structure=user.profile.structure)


class StructureRelated(models.Model):
    """
    A mixin used for any entities that belong to a structure
    """
    structure = models.ForeignKey(Structure, default=default_structure, verbose_name=_(u"Related structure")

    objects = models.Manager()
    in_structure = StructureRelatedManager()

    @classmethod
    def forUser(cls, user):
        return cls.in_structure.byUser(user)

    class Meta:
        abstract = True
        verbose_name = _(u"Related structures")
        verbose_name_plural = _(u"Related structure")


class UserProfile(StructureRelated):
    user = models.OneToOneField(User, unique=True)

    language = models.CharField(_(u"Language"), max_length=10,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)
    class Meta:
        verbose_name = _(u"User's profile")
        verbose_name_plural = _(u"User's profiles")

    def __unicode__(self):
        return _("Profile for %s") % self.user

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


@receiver(user_logged_in)
def lang(sender, **kwargs):
    """ Set user's language in session when he logs in. """
    lang_code = kwargs['user'].profile.language
    kwargs['request'].session['django_language'] = lang_code
