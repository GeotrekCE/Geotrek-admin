# -*- coding: utf-8 -*-

import factory

from geotrek.authent.factories import StructureRelatedDefaultFactory
from geotrek.common.utils.testdata import dummy_filefield_as_sequence

from . import models


class SportPracticeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SportPractice

    name = factory.Sequence(lambda n: u"Practice %s" % n)


class SpeciesFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Species

    name = factory.Sequence(lambda n: u"Species %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')
    url = factory.Sequence(lambda n: u"http://url%s.com" % n)
    period06 = True
    period07 = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        practices = kwargs.pop('practices', None)

        species = super(SpeciesFactory, cls)._prepare(create, **kwargs)

        if create:
            if practices is None:
                practices = [SportPracticeFactory.create(), SportPracticeFactory.create()]
            for practice in practices:
                species.practices.add(practice)

        return species


class SensitiveAreaFactory(StructureRelatedDefaultFactory):
    class Meta:
        model = models.SensitiveArea

    species = factory.SubFactory(SpeciesFactory)
    geom = 'POLYGON((700000 6600000, 700000 6600003, 700003 6600003, 700003 6600000, 700000 6600000))'
    published = True
