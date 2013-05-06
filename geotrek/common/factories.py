import factory

from . import models


class OrganismFactory(factory.Factory):
    FACTORY_FOR = models.Organism

    organism = factory.Sequence(lambda n: u"Organism %s" % n)


class FileTypeFactory(factory.Factory):
    FACTORY_FOR = models.FileType

    type = factory.Sequence(lambda n: u"FileType %s" % n)

