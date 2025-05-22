import factory
from django.conf import settings
from django.contrib.auth.models import Group
from mapentity.tests.factories import UserFactory

from .. import models as core_models


class PathManagerFactory(UserFactory):
    is_staff = True

    @factory.post_generation
    def create_path_manager(obj, create, extracted, **kwargs):
        GROUP_PATH_MANAGER_ID = settings.AUTHENT_GROUPS_MAPPING["PATH_MANAGER"]
        pathmanager = Group.objects.get(pk=GROUP_PATH_MANAGER_ID)
        obj.groups.add(pathmanager)


class TrekkingManagerFactory(UserFactory):
    is_staff = True

    @factory.post_generation
    def create_trekking_manager(obj, create, extracted, **kwargs):
        GROUP_TREKKING_MANAGER_ID = settings.AUTHENT_GROUPS_MAPPING["TREKKING_MANAGER"]
        pathmanager = Group.objects.get(pk=GROUP_TREKKING_MANAGER_ID)
        obj.groups.add(pathmanager)


class StructureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = core_models.Structure

    name = factory.Sequence("structure {0}".format)


# Abstract
class StructureRelatedRandomFactory(factory.django.DjangoModelFactory):
    """Create a new structure each time"""

    class Meta:
        model = core_models.StructureRelated

    # Return the default structure
    structure = factory.SubFactory(StructureFactory)


# Abstract
class StructureRelatedDefaultFactory(factory.django.DjangoModelFactory):
    """Use the default structure"""

    class Meta:
        model = core_models.StructureRelated

    structure = factory.LazyAttribute(lambda _: core_models.default_structure())


class UserProfileFactory(StructureRelatedDefaultFactory):
    """
    Create a normal user (language=fr and structure=default)
    """

    class Meta:
        model = core_models.UserProfile

    user = factory.SubFactory(UserFactory)
