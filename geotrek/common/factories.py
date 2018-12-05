import factory

from geotrek.authent.factories import UserFactory
from geotrek.common.models import Attachment
from geotrek.common.utils.testdata import (dummy_filefield_as_sequence,
                                           get_dummy_uploaded_file)

from . import models


class OrganismFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Organism

    organism = factory.Sequence(lambda n: u"Organism %s" % n)


class FileTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FileType

    type = factory.Sequence(lambda n: u"FileType %s" % n)


class AttachmentFactory(factory.DjangoModelFactory):
    """
    Create an attachment. You must provide an 'obj' keywords,
    the object (saved in db) to which the attachment will be bound.
    """

    class Meta:
        model = Attachment

    attachment_file = get_dummy_uploaded_file()
    filetype = factory.SubFactory(FileTypeFactory)

    creator = factory.SubFactory(UserFactory)
    title = factory.Sequence(u"Title {0}".format)
    legend = factory.Sequence(u"Legend {0}".format)


class ThemeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Theme

    label = factory.Sequence(lambda n: u"Theme %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class RecordSourceFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.RecordSource

    name = factory.Sequence(lambda n: u"Record source %s" % n)
    website = 'http://geotrek.fr'
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class TargetPortalFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TargetPortal

    name = factory.Sequence(lambda n: u"Target Portal %s" % n)
    website = factory.Sequence(lambda n: u"http://geotrek-rando-{}.fr".format(n))
