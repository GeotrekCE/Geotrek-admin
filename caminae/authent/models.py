# -*- coding: utf-8 -*-

"""
    Models to manage users and profiles
"""
from django.db import models
from django.contrib.auth.models import User, Group
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
    """ Create default structure if necessary """
    return Structure.objects.get_or_create(name=settings.DEFAULT_STRUCTURE_NAME)[0]


class StructureRelatedManager(models.Manager):
    """ A simple manager to manage structure related objects"""
    def byUser(self, user):
        """ Filter by user's structure """
        qs = super(StructureRelatedManager, self).get_query_set()
        return qs.filter(structure=user.profile.structure)


class StructureRelated(models.Model):
    """
    A mixin used for any entities that belong to a structure
    """
    structure = models.ForeignKey(Structure, default=default_structure, verbose_name=_(u"Related structure"))

    objects = models.Manager()
    in_structure = StructureRelatedManager()

    @classmethod
    def forUser(cls, user):
        """ Shortcut to manager's filter by user """
        return cls.in_structure.byUser(user)

    class Meta:
        abstract = True
        verbose_name = _(u"Related structures")
        verbose_name_plural = _(u"Related structure")


class UserProfile(StructureRelated):
    """
    A custom user profile
    """
    user = models.OneToOneField(User, unique=True)

    language = models.CharField(_(u"Language"), max_length=10,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)
    class Meta:
        verbose_name = _(u"User's profile")
        verbose_name_plural = _(u"User's profiles")

    def __unicode__(self):
        return _("Profile for %s") % self.user

    def has_group(self, g):
        return self.user.groups.filter(pk=g.pk).exists()

    def is_path_manager(self):
        g = Group.objects.get(name='Référents sentiers')
        return self.has_group(g)

    def is_comm_manager(self):
        g = Group.objects.get(name='Référents communication')
        return self.has_group(g)

    def is_editor(self):
        g = Group.objects.get(name='Rédacteurs')
        return self.has_group(g)

    def is_administrator(self):
        g = Group.objects.get(name='Administrateurs')
        return self.has_group(g)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


@receiver(user_logged_in)
def lang(sender, **kwargs):
    """ Set user's language in session when he logs in. """
    lang_code = kwargs['user'].profile.language
    kwargs['request'].session['django_language'] = lang_code
