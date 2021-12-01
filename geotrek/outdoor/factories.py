import factory
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from geotrek.authent.factories import StructureRelatedDefaultFactory
from geotrek.outdoor.models import Site, Practice, SiteType, CourseType, RatingScale, Rating, Sector, Course
from mapentity.factories import UserFactory


class SectorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Sector

    name = "Sector"


class PracticeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Practice

    name = "Practice"
    sector = factory.SubFactory(SectorFactory)


class RatingScaleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RatingScale

    name = "RatingScale"
    practice = factory.SubFactory(PracticeFactory)


class RatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rating

    name = "Rating"
    scale = factory.SubFactory(RatingScaleFactory)


class SiteTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SiteType

    name = "Site type"
    practice = factory.SubFactory(PracticeFactory)


class CourseTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseType

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

    @factory.post_generation
    def managers(obj, create, extracted=None, **kwargs):
        if create and extracted:
            obj.managers.set(extracted)


class OutdoorManagerFactory(UserFactory):
    is_staff = True

    @factory.post_generation
    def create_outdoor_manager(obj, create, extracted, **kwargs):
        for model in (Site, Course):
            content_type = ContentType.objects.get_for_model(model)
            for action in ('add', 'change', 'delete', 'read', 'export'):
                codename = '{}_{}'.format(action, model.__name__.lower())
                permission = Permission.objects.get(content_type=content_type, codename=codename)
                obj.user_permissions.add(permission)


class CourseFactory(StructureRelatedDefaultFactory):
    class Meta:
        model = Course

    name = "Course"
    description = "Blah"
    advice = "Warning!"
    equipment = "Rope"
    height = 42
    published = True
    duration = 55
    eid = "43"
    geom = 'GEOMETRYCOLLECTION(POINT(0 0))'
    type = factory.SubFactory(CourseTypeFactory)
    ratings_description = 'Ths rating is ratable'
    gear = 'Shoes mandatory'

    @factory.post_generation
    def parent_sites(obj, create, extracted=None, **kwargs):
        if create:
            if extracted:
                obj.parent_sites.set(extracted)
            else:
                obj.parent_sites.add(SiteFactory.create().pk)
