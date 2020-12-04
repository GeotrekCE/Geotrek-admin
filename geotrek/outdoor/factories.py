import factory
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from geotrek.authent.factories import StructureRelatedDefaultFactory
from geotrek.outdoor.models import Site
from mapentity.factories import UserFactory


class SiteFactory(StructureRelatedDefaultFactory):
    class Meta:
        model = Site

    name = "Site"
    description = "Blah"
    geom = 'POINT(0 0)'


class OutdoorManagerFactory(UserFactory):
    is_staff = True

    @factory.post_generation
    def create_Outdoor_manager(obj, create, extracted, **kwargs):
        for model in (Site, ):
            content_type = ContentType.objects.get_for_model(model)
            for action in ('add', 'change', 'delete', 'read', 'export'):
                codename = '{}_{}'.format(action, model.__name__.lower())
                permission = Permission.objects.get(content_type=content_type, codename=codename)
                obj.user_permissions.add(permission)
