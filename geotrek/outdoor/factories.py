import factory
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from geotrek.authent.factories import StructureRelatedDefaultFactory
from geotrek.outdoor.models import Site, Practice, SiteType, RatingScale, Rating
from mapentity.factories import UserFactory


class PracticeFactory(factory.DjangoModelFactory):
    class Meta:
        model = Practice

    name = "Practice"


class RatingScaleFactory(factory.DjangoModelFactory):
    class Meta:
        model = RatingScale

    name = "RatingScale"
    practice = factory.SubFactory(PracticeFactory)


class RatingFactory(factory.DjangoModelFactory):
    class Meta:
        model = Rating

    name = "Rating"
    scale = factory.SubFactory(RatingScaleFactory)


class SiteTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = SiteType

    name = "Site type"
    practice = factory.SubFactory(PracticeFactory)


class SiteFactory(StructureRelatedDefaultFactory):
    class Meta:
        model = Site

    name = "Site"
    practice = factory.SubFactory(PracticeFactory)
    description = "Blah"
    description_teaser = "More blah"
    ambiance = "Party time!"
    advice = "Warning!"
    period = "Summer"
    orientation = ['S', 'SW']
    wind = ['N']
    published = True
    type = factory.SubFactory(SiteTypeFactory)
    eid = "42"
    geom = 'GEOMETRYCOLLECTION(POINT(0 0))'


class OutdoorManagerFactory(UserFactory):
    is_staff = True

    @factory.post_generation
    def create_outdoor_manager(obj, create, extracted, **kwargs):
        for model in (Site, ):
            content_type = ContentType.objects.get_for_model(model)
            for action in ('add', 'change', 'delete', 'read', 'export'):
                codename = '{}_{}'.format(action, model.__name__.lower())
                permission = Permission.objects.get(content_type=content_type, codename=codename)
                obj.user_permissions.add(permission)
