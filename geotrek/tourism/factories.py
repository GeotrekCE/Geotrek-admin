# -*- coding: utf-8 -*-
from django.contrib.gis.geos import Point

import factory

from geotrek.authent.factories import StructureRelatedDefaultFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image, dummy_filefield_as_sequence

from . import models
from geotrek.trekking.factories import TrekFactory


class DataSourceFactory(factory.Factory):
    FACTORY_FOR = models.DataSource

    title = factory.Sequence(lambda n: u"DataSource %s" % n)
    url = factory.Sequence(lambda n: u"http://%s.com" % n)
    type = models.DATA_SOURCE_TYPES.GEOJSON
    pictogram = get_dummy_uploaded_image()


class InformationDeskTypeFactory(factory.Factory):
    FACTORY_FOR = models.InformationDeskType

    label = factory.Sequence(lambda n: u"Type %s" % n)
    pictogram = get_dummy_uploaded_image()


class InformationDeskFactory(factory.Factory):
    FACTORY_FOR = models.InformationDesk

    name = factory.Sequence(lambda n: u"information desk name %s" % n)
    type = factory.SubFactory(InformationDeskTypeFactory)
    description = factory.Sequence(lambda n: u"<p>description %s</p>" % n)
    phone = factory.Sequence(lambda n: u"01 02 03 %s" % n)
    email = factory.Sequence(lambda n: u"email-%s@makina-corpus.com" % n)
    website = factory.Sequence(lambda n: u"http://makina-corpus.com/%s" % n)
    photo = dummy_filefield_as_sequence('photo %s')
    street = factory.Sequence(lambda n: u"%s baker street" % n)
    postal_code = '28300'
    municipality = factory.Sequence(lambda n: u"Bailleau L'évêque-%s" % n)
    geom = Point(3.14, 42)


class TouristicContentCategoryFactory(factory.Factory):
    FACTORY_FOR = models.TouristicContentCategory

    label = factory.Sequence(lambda n: u"Category %s" % n)
    type1_label = factory.Sequence(lambda n: u"Type1_label %s" % n)
    # Keep type2_label with default value
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class TouristicContentTypeFactory(factory.Factory):
    FACTORY_FOR = models.TouristicContentType

    label = factory.Sequence(lambda n: u"Type %s" % n)
    category = factory.SubFactory(TouristicContentCategoryFactory)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')
    in_list = 1


class ReservationSystemFactory(factory.Factory):
    FACTORY_FOR = models.ReservationSystem

    name = factory.Sequence(lambda n: u"ReservationSystem %s" % n)


class TouristicContentFactory(StructureRelatedDefaultFactory):
    FACTORY_FOR = models.TouristicContent

    name = factory.Sequence(lambda n: u"TouristicContent %s" % n)
    category = factory.SubFactory(TouristicContentCategoryFactory)
    geom = 'POINT(0 0)'
    published = True
    reservation_system = factory.SubFactory(ReservationSystemFactory)
    reservation_id = 'XXXXXXXXX'


class TouristicEventTypeFactory(factory.Factory):
    FACTORY_FOR = models.TouristicEventType

    type = factory.Sequence(lambda n: u"Type %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class TouristicEventFactory(factory.Factory):
    FACTORY_FOR = models.TouristicEvent

    name = factory.Sequence(lambda n: u"TouristicEvent %s" % n)
    geom = 'POINT(0 0)'
    published = True

    type = factory.SubFactory(TouristicEventTypeFactory)


class TrekWithTouristicEventFactory(TrekFactory):
    @classmethod
    def _prepare(cls, create, **kwargs):
        trek = super(TrekWithTouristicEventFactory, cls)._prepare(create, **kwargs)
        path = trek.paths.all()[0]
        te1 = TouristicEventFactory.create(no_path=True)
        te1.add_path(path, start=0.5, end=0.5)
        te2 = TouristicEventFactory.create(no_path=True)
        te2.add_path(path, start=0.4, end=0.4)

        if create:
            trek.save()

        return trek


class TrekWithTouristicContentFactory(TrekFactory):
    @classmethod
    def _prepare(cls, create, **kwargs):
        trek = super(TrekWithTouristicContentFactory, cls)._prepare(create, **kwargs)
        path = trek.paths.all()[0]
        tc1 = TouristicContentFactory.create(no_path=True)
        tc1.add_path(path, start=0.5, end=0.5)
        tc2 = TouristicContentFactory.create(no_path=True)
        tc2.add_path(path, start=0.4, end=0.4)

        if create:
            trek.save()

        return trek
