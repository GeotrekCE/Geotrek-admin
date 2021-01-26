from django.contrib.gis.geos import Point

import factory

from geotrek.authent.factories import StructureRelatedDefaultFactory
from geotrek.common.factories import ReservationSystemFactory, TargetPortalFactory, ThemeFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image

from . import models


class InformationDeskTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InformationDeskType

    label = "Type"
    pictogram = get_dummy_uploaded_image()


class InformationDeskFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InformationDesk

    name = "Information desk"
    type = factory.SubFactory(InformationDeskTypeFactory)
    description = "<p>Description</p>"
    phone = "01 02 03 04 05"
    email = "email@makina-corpus.com"
    website = "https://makina-corpus.com"
    photo = get_dummy_uploaded_image('photo')
    street = "42 Baker street"
    postal_code = '28300'
    municipality = "Bailleau L'évêque"
    geom = Point(3.14, 42)


class TouristicContentCategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicContentCategory

    label = "Category"
    type1_label = "Type1 label"
    # Keep type2_label with default value
    pictogram = get_dummy_uploaded_image('touristiccontent-category.png')


class TouristicContentType1Factory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicContentType1

    label = "Type1"
    category = factory.SubFactory(TouristicContentCategoryFactory)
    pictogram = get_dummy_uploaded_image('touristiccontent-type1.png')


class TouristicContentType2Factory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicContentType2

    label = "Type2"
    category = factory.SubFactory(TouristicContentCategoryFactory)
    pictogram = get_dummy_uploaded_image('touristiccontent-type2.png')


class TouristicContentFactory(StructureRelatedDefaultFactory):
    class Meta:
        model = models.TouristicContent

    name = "Touristic content"
    category = factory.SubFactory(TouristicContentCategoryFactory)
    geom = 'POINT(0 0)'
    published = True
    reservation_system = factory.SubFactory(ReservationSystemFactory)
    reservation_id = 'XXXXXXXXX'
    description = '<p>Blah CT</p>'

    @factory.post_generation
    def sources(obj, create, extracted=None, **kwargs):
        if create:
            if extracted:
                for source in extracted:
                    obj.source.add(source)

    @factory.post_generation
    def portals(obj, create, extracted=None, **kwargs):
        if create:
            if extracted:
                for portal in extracted:
                    obj.portal.add(portal)
            else:
                obj.portal.add(TargetPortalFactory.create())

    @factory.post_generation
    def themes(obj, create, extracted=None, **kwargs):
        if create:
            if extracted:
                for theme in extracted:
                    obj.themes.add(theme)
            else:
                obj.themes.add(ThemeFactory.create())

    @factory.post_generation
    def type1(obj, create, extracted=None, **kwargs):
        if create:
            assert not extracted, "Not implemented"
            obj.type1.add(TouristicContentType1Factory.create())


class TouristicEventTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicEventType

    type = "Type"
    pictogram = get_dummy_uploaded_image('touristicevent-type.png')


class TouristicEventFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicEvent

    name = "Touristic event"
    geom = 'POINT(0 0)'
    published = True
    begin_date = '2002-02-20'
    end_date = '2202-02-22'

    type = factory.SubFactory(TouristicEventTypeFactory)

    @factory.post_generation
    def sources(obj, create, extracted=None, **kwargs):
        if create:
            if extracted:
                for source in extracted:
                    obj.source.add(source)

    @factory.post_generation
    def portals(obj, create, extracted=None, **kwargs):
        if create:
            if extracted:
                for portal in extracted:
                    obj.portal.add(portal)

    @factory.post_generation
    def themes(obj, create, extracted=None, **kwargs):
        if create:
            if extracted:
                for theme in extracted:
                    obj.themes.add(theme)
            else:
                obj.themes.add(ThemeFactory.create())
