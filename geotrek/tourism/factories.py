from django.contrib.gis.geos import Point

import factory

from geotrek.authent.factories import StructureRelatedDefaultFactory
from geotrek.common.factories import ReservationSystemFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image

from . import models
from geotrek.trekking.factories import TrekFactory
from django.conf import settings


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


class TrekWithTouristicEventFactory(TrekFactory):
    @factory.post_generation
    def create_trek_with_touristic_event(obj, create, extracted, **kwargs):
        TouristicEventFactory.create(geom='POINT(700000 6600000)')
        TouristicEventFactory.create(geom='POINT(700100 6600100)')

        if create:
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                setattr(obj, 'published_{}'.format(lang), True)
            obj.save()


class TrekWithTouristicContentFactory(TrekFactory):
    @factory.post_generation
    def create_trek_with_touristic_content(obj, create, extracted, **kwargs):
        TouristicContentFactory.create(category=TouristicContentCategoryFactory(label="Restaurant"),
                                       geom='POINT(700000 6600000)')
        TouristicContentFactory.create(category=TouristicContentCategoryFactory(label="Musée"),
                                       geom='POINT(700100 6600100)')

        if create:
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                setattr(obj, 'published_{}'.format(lang), True)
            obj.save()
