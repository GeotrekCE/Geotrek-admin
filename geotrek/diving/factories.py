# -*- coding: utf-8 -*-

import factory

from geotrek.authent.factories import StructureRelatedDefaultFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image

from . import models


class PracticeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Practice

    name = factory.Sequence(lambda n: u"Practice %s" % n)
    pictogram = get_dummy_uploaded_image()


class DiveFactory(StructureRelatedDefaultFactory):
    class Meta:
        model = models.Dive

    name = factory.Sequence(lambda n: u"Dive %s" % n)
    practice = factory.SubFactory(PracticeFactory)
    geom = 'POINT(0 0)'
    published = True

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
