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


GROUP_PATH_MANAGER = u'Référents sentiers'
GROUP_COMM_MANAGER = u'Référents communication'
GROUP_EDITOR = u'Rédacteurs'
GROUP_ADMINISTRATOR = u'Administrateurs'


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

    def same_structure(self, user):
        """ Returns True if the user is in the same structure, False otherwise. """
        return user.profile.structure == self.structure

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
        """ Returns True if the user belongs to path managers group. """
        g = Group.objects.get(name=GROUP_PATH_MANAGER)
        return self.has_group(g) or self.user.is_staff

    def is_comm_manager(self):
        """ Returns True if the user belongs to comm managers group. """
        g = Group.objects.get(name=GROUP_COMM_MANAGER)
        return self.has_group(g) or self.user.is_staff

    def is_editor(self):
        """ Returns True if the user belongs to editors group. """
        g = Group.objects.get(name=GROUP_EDITOR)
        return self.has_group(g) or self.user.is_staff

    def is_administrator(self):
        """ Returns True if the user belongs to administrators group. """
        g = Group.objects.get(name=GROUP_ADMINISTRATOR)
        return self.has_group(g) or self.user.is_staff

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


@receiver(user_logged_in)
def lang(sender, **kwargs):
    """ Set user's language in session when he logs in. """
    lang_code = kwargs['user'].profile.language
    kwargs['request'].session['django_language'] = lang_code
