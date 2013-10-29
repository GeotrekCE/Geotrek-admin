import factory
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import Group

from . import models as core_models


class UserFactory(factory.Factory):
    FACTORY_FOR = auth_models.User

    username = factory.Sequence('mary_poppins{0}'.format)
    first_name = factory.Sequence('Mary {0}'.format)
    last_name = factory.Sequence('Poppins {0}'.format)
    email = factory.LazyAttribute(lambda a: '{0}@example.com'.format(a.username))

    is_staff = False
    is_active = True
    is_superuser = False

    # last_login/date_joined

    @classmethod
    def _prepare(cls, create, **kwargs):
        """
        A topology mixin should be linked to at least one Path (through
        PathAggregation).
        """
        # groups/user_permissions
        groups = kwargs.pop('groups', [])
        permissions = kwargs.pop('permissions', [])

        user = super(UserFactory, cls)._prepare(create, **kwargs)

        for group in groups:
            user.groups.add(group)

        for perm in permissions:
            user.user_permissions.add(perm)

        if create:
            # Save ManyToMany group and perm relations
            user.save()

        return user


def create_user_with_password(cls, **kwargs):
    pwd = kwargs.pop('password', None)
    user = cls(**kwargs)
    user.set_password(pwd)
    user.save()
    return user

UserFactory.set_creation_function(create_user_with_password)


class SuperUserFactory(UserFactory):
    is_superuser = True
    is_staff = True


class PathManagerFactory(UserFactory):
    is_staff = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        pathmanager, exist = Group.objects.get_or_create(name=core_models.GROUP_PATH_MANAGER)
        kwargs.setdefault('groups', []).append(pathmanager)
        return super(PathManagerFactory, cls)._prepare(create, **kwargs)


class TrekkingManagerFactory(UserFactory):
    is_staff = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        pathmanager, exist = Group.objects.get_or_create(name=core_models.GROUP_TREKKING_MANAGER)
        kwargs.setdefault('groups', []).append(pathmanager)
        return super(TrekkingManagerFactory, cls)._prepare(create, **kwargs)


class EditorFactory(UserFactory):
    is_staff = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        editor, exist = Group.objects.get_or_create(name=core_models.GROUP_EDITOR)
        kwargs.setdefault('groups', []).append(editor)
        return super(EditorFactory, cls)._prepare(create, **kwargs)


## geotrek.core models ##

class StructureFactory(factory.Factory):
    FACTORY_FOR = core_models.Structure

    name = factory.Sequence('structure {0}'.format)


# Abstract
class StructureRelatedRandomFactory(factory.Factory):
    """Create a new structure each time"""
    FACTORY_FOR = core_models.StructureRelated

    # Return the default structure
    structure = factory.SubFactory(StructureFactory)


# Abstract
class StructureRelatedDefaultFactory(factory.Factory):
    """Use the default structure"""
    FACTORY_FOR = core_models.StructureRelated

    structure = factory.LazyAttribute(lambda _: core_models.default_structure())


class UserProfileFactory(StructureRelatedDefaultFactory):
    """
    Create a normal user (language=fr and structure=default)
    """
    FACTORY_FOR = core_models.UserProfile

    user = factory.SubFactory(UserFactory)
    language = 'fr'
