import factory
import os
import tempfile
from zipfile import ZipFile

from geotrek.authent.tests.factories import UserFactory
from geotrek.common.models import Attachment
from geotrek.common.utils.testdata import (dummy_filefield_as_sequence,
                                           get_dummy_uploaded_image,
                                           get_dummy_uploaded_file)

from .. import models

from geotrek.common.management.commands.sync_rando import Command

from django.conf import settings
from django.test.client import RequestFactory


class FakeSyncCommand(Command):
    categories = '1'
    verbosity = 2
    host = 'localhost:8000'
    secure = True
    with_infrastructures = True
    with_signages = True
    with_events = True
    rando_url = 'localhost:3000'

    def __init__(self, portal='', source='', skip_dem=False, skip_pdf=False, skip_profile_png=False):
        super().__init__(stdout=None, stderr=None, no_color=False, force_color=False)
        self.dst_root = settings.TMP_DIR
        self.temporary_directory = tempfile.TemporaryDirectory(dir=settings.VAR_DIR)
        self.tmp_root = self.temporary_directory.name
        zipname = os.path.join('zip', 'tiles', 'global.zip')
        global_file = os.path.join(self.tmp_root, zipname)
        dirname = os.path.dirname(global_file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self.zipfile = ZipFile(os.path.join(self.tmp_root, 'zip', 'tiles', 'global.zip'), 'w')
        self.factory = RequestFactory()
        self.source = source
        self.portal = portal
        self.skip_dem = skip_dem
        self.skip_pdf = skip_pdf
        self.skip_profile_png = skip_profile_png


class OrganismFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Organism

    organism = factory.Sequence(lambda n: "Organism %s" % n)


class FileTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FileType

    type = factory.Sequence(lambda n: "FileType %s" % n)


class LicenseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.License

    label = factory.Sequence(lambda n: "License %s" % n)


class AttachmentFactory(factory.django.DjangoModelFactory):
    """
    Create an attachment. You must provide an 'obj' keywords,
    the object (saved in db) to which the attachment will be bound.
    """

    class Meta:
        model = Attachment

    attachment_file = get_dummy_uploaded_file()
    filetype = factory.SubFactory(FileTypeFactory)
    license = factory.SubFactory(LicenseFactory)

    creator = factory.SubFactory(UserFactory)
    title = factory.Sequence("Title {0}".format)
    legend = factory.Sequence("Legend {0}".format)


class ThemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Theme

    label = factory.Sequence(lambda n: "Theme %s" % n)
    pictogram = dummy_filefield_as_sequence('theme-%s.png')


class RecordSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RecordSource

    name = factory.Sequence(lambda n: "Record source %s" % n)
    website = 'http://geotrek.fr'
    pictogram = dummy_filefield_as_sequence('recordsource-%s.png')


class TargetPortalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TargetPortal

    name = factory.Sequence(lambda n: "Target Portal %s" % n)
    website = factory.Sequence(lambda n: "http://geotrek-rando-{}.fr".format(n))


class ReservationSystemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ReservationSystem

    name = factory.Sequence(lambda n: "Reservation system %s" % n)


class LabelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Label

    name = "Label"
    pictogram = get_dummy_uploaded_image('label.png')
    advice = "Advice label"
    filter = True


class AttachmentAccessibilityFactory(factory.django.DjangoModelFactory):
    """
    Create an attachment. You must provide an 'obj' keywords,
    the object (saved in db) to which the attachment will be bound.
    """

    class Meta:
        model = models.AccessibilityAttachment

    attachment_accessibility_file = get_dummy_uploaded_image()

    creator = factory.SubFactory(UserFactory)
    title = factory.Sequence("Title {0}".format)
    legend = factory.Sequence("Legend {0}".format)
