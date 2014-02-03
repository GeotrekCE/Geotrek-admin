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

from geotrek.common.utils import reify


"""
    Groups required for managing permissions.
    This could be managed using initial_data. And permissions could globally be refactored using has_perm()
"""
GROUP_PATH_MANAGER = u'Référents sentiers'
GROUP_TREKKING_MANAGER = u'Référents communication'
GROUP_EDITOR = u'Rédacteurs'


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
        ordering = ['name']


def default_structure():
    """ Create default structure if necessary """
    return Structure.objects.get_or_create(name=settings.DEFAULT_STRUCTURE_NAME)[0]


class StructureRelatedQuerySet(models.query.QuerySet):
    def for_user(self, user):
        return StructureRelatedQuerySet.queryset_for_user(self, user)

    @staticmethod
    def queryset_for_user(queryset, user):
        return queryset.filter(structure=user.profile.structure)


class StructureRelatedManager(models.Manager):
    """ A simple manager to manage structure related objects"""
    def get_queryset(self):
        return StructureRelatedQuerySet(self.model, using=self._db)

    def for_user(self, user):
        """ Filter by user's structure """
        return self.get_queryset().for_user(user)


class StructureRelated(models.Model):
    """
    A mixin used for any entities that belong to a structure
    """
    structure = models.ForeignKey(Structure, default=default_structure,
                                  verbose_name=_(u"Related structure"), db_column='structure')

    objects = models.Manager()
    in_structure = StructureRelatedManager()

    @classmethod
    def for_user(cls, user):
        """ Shortcut to manager's filter by user """
        return cls.in_structure.for_user(user)

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

    @reify
    def is_path_manager(self):
        """ Returns True if the user belongs to path managers group. """
        g = Group.objects.get_or_create(name=GROUP_PATH_MANAGER)[0]
        return self.has_group(g) or self.user.is_superuser

    @reify
    def is_trekking_manager(self):
        """ Returns True if the user belongs to comm managers group. """
        g = Group.objects.get_or_create(name=GROUP_TREKKING_MANAGER)[0]
        return self.has_group(g) or self.user.is_superuser

    @reify
    def is_editor(self):
        """ Returns True if the user belongs to editors group. """
        g = Group.objects.get_or_create(name=GROUP_EDITOR)[0]
        return self.has_group(g) or self.is_path_manager or self.user.is_superuser

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

# Force all apps to appear in Admin
# TODO: this is obviously wrong: using Django perms instead of groups, it can be removed.
User.has_module_perms = lambda u, app_label: True


@receiver(user_logged_in)
def lang(sender, **kwargs):
    """ Set user's language in session when he logs in. """
    lang_code = kwargs['user'].profile.language
    kwargs['request'].session['django_language'] = lang_code
