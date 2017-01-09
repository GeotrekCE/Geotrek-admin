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

    label = factory.Sequence(lambda n: u"Type %s" % n)
    pictogram = get_dummy_uploaded_image()


class InformationDeskFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InformationDesk

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


class TouristicContentCategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicContentCategory

    label = factory.Sequence(lambda n: u"Category %s" % n)
    type1_label = factory.Sequence(lambda n: u"Type1_label %s" % n)
    # Keep type2_label with default value
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class TouristicContentTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicContentType

    label = factory.Sequence(lambda n: u"Type %s" % n)
    category = factory.SubFactory(TouristicContentCategoryFactory)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')
    in_list = 1


class ReservationSystemFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ReservationSystem

    name = factory.Sequence(lambda n: u"ReservationSystem %s" % n)


class TouristicContentFactory(StructureRelatedDefaultFactory):
    class Meta:
        model = models.TouristicContent

    name = factory.Sequence(lambda n: u"TouristicContent %s" % n)
    category = factory.SubFactory(TouristicContentCategoryFactory)
    geom = 'POINT(0 0)'
    published = True
    reservation_system = factory.SubFactory(ReservationSystemFactory)
    reservation_id = 'XXXXXXXXX'

    @classmethod
    def _prepare(cls, create, **kwargs):
        sources = kwargs.pop('sources', None)
        portals = kwargs.pop('portals', None)

        content = super(TouristicContentFactory, cls)._prepare(create, **kwargs)

        if create:
            if sources:
                for source in sources:
                    content.source.add(source)

            if portals:
                for portal in portals:
                    content.portal.add(portal)
        return content


class TouristicEventTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicEventType

    type = factory.Sequence(lambda n: u"Type %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class TouristicEventFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TouristicEvent

    name = factory.Sequence(lambda n: u"TouristicEvent %s" % n)
    geom = 'POINT(0 0)'
    published = True
    begin_date = timezone.now()
    end_date = timezone.now()

    type = factory.SubFactory(TouristicEventTypeFactory)

    @classmethod
    def _prepare(cls, create, **kwargs):
        sources = kwargs.pop('sources', None)
        portals = kwargs.pop('portals', None)

        event = super(TouristicEventFactory, cls)._prepare(create, **kwargs)

        if create:
            if sources:
                for source in sources:
                    event.source.add(source)

            if portals:
                for portal in portals:
                    event.portal.add(portal)
        return event


class TrekWithTouristicEventFactory(TrekFactory):
    @classmethod
    def _prepare(cls, create, **kwargs):
        trek = super(TrekWithTouristicEventFactory, cls)._prepare(create, **kwargs)
        TouristicEventFactory.create(geom='POINT(700000 6600000)')
        TouristicEventFactory.create(geom='POINT(700100 6600100)')

        if create:
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                setattr(trek, 'published_{}'.format(lang), True)
            trek.save()

        return trek


class TrekWithTouristicContentFactory(TrekFactory):
    @classmethod
    def _prepare(cls, create, **kwargs):
        trek = super(TrekWithTouristicContentFactory, cls)._prepare(create, **kwargs)
        TouristicContentFactory.create(category=TouristicContentCategoryFactory(label=u"Restaurant"),
                                       geom='POINT(700000 6600000)')
        TouristicContentFactory.create(category=TouristicContentCategoryFactory(label=u"Musée"),
                                       geom='POINT(700100 6600100)')

        if create:
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                setattr(trek, 'published_{}'.format(lang), True)
            trek.save()

        return trek
