# -*- coding: utf-8 -*-
from django.contrib.gis.geos import Point

import factory

from geotrek.common.utils.testdata import get_dummy_uploaded_image, dummy_filefield_as_sequence

from . import models


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


class TouristicContentFactory(factory.Factory):
    FACTORY_FOR = models.TouristicContent

    name = factory.Sequence(lambda n: u"TouristicContent %s" % n)
    geom = 'POINT(0 0)'
