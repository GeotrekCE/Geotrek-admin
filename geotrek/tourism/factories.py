# -*- coding: utf-8 -*-

from django.contrib.gis.geos import Point
from django.utils import timezone

import factory

from geotrek.authent.factories import StructureRelatedDefaultFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image, dummy_filefield_as_sequence

from . import models
from geotrek.trekking.factories import TrekFactory
from django.conf import settings


class InformationDeskTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InformationDeskType

    label = factory.Sequence(lambda n: "Type %s" % n)
    pictogram = get_dummy_uploaded_image()


class InformationDeskFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InformationDesk

    name = factory.Sequence(lambda n: "information desk name %s" % n)
    type = factory.SubFactory(InformationDeskTypeFactory)
    description = factory.Sequence(lambda n: "<p>description %s</p>" % n)
    phone = factory.Sequence(lambda n: "01 02 03 %s" % n)
    email = factory.Sequence(lambda n: "email-%s@makina-corpus.com" % n)
    website = factory.Sequence(lambda n: "http://makina-corpus.com/%s" % n)
    photo = dummy_filefield_as_sequence('photo %s')
    street = factory.Sequence(lambda n: "%s baker street" % n)
    postal_code = '28300'
    municipality = factory.Sequence(lambda n: "Bailleau L'évêque-%s" % n)
    geom = Point(3.14, 42)


class TouristicContentCategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicContentCategory

    label = factory.Sequence(lambda n: "Category %s" % n)
    type1_label = factory.Sequence(lambda n: "Type1_label %s" % n)
    # Keep type2_label with default value
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class TouristicContentTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicContentType

    label = factory.Sequence(lambda n: "Type %s" % n)
    category = factory.SubFactory(TouristicContentCategoryFactory)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class ReservationSystemFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ReservationSystem

    name = factory.Sequence(lambda n: "ReservationSystem %s" % n)


class TouristicContentFactory(StructureRelatedDefaultFactory):
    class Meta:
        model = models.TouristicContent

    name = factory.Sequence(lambda n: "TouristicContent %s" % n)
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

    type = factory.Sequence(lambda n: "Type %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class TouristicEventFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicEvent

    name = factory.Sequence(lambda n: "TouristicEvent %s" % n)
    geom = 'POINT(0 0)'
    published = True
    begin_date = timezone.now()
    end_date = timezone.now()

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
