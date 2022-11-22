from django.test import TestCase
from freezegun import freeze_time

from geotrek.common.tests.factories import OrganismFactory, AttachmentFactory, AttachmentAccessibilityFactory


class CommonSignalsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.object = OrganismFactory()

    def test_date_update_when_attachment_added(self):
        """ Object date_update updated when attachment added """
        with freeze_time("2022-07-04T14:00:00+00:00"):
            # add attachment
            AttachmentFactory(content_object=self.object)
        self.object.refresh_from_db()
        # object date_update has been updated with current datetime
        self.assertEqual(self.object.date_update.isoformat(), "2022-07-04T14:00:00+00:00")

    def test_date_update_when_attachment_updated(self):
        """ Object date_update updated when attachment updated """
        attachment = AttachmentFactory(content_object=self.object)
        with freeze_time("2022-07-04T15:00:00+00:00"):
            attachment.save()
        self.object.refresh_from_db()
        # object date_update has been updated with current datetime
        self.assertEqual(self.object.date_update.isoformat(), "2022-07-04T15:00:00+00:00")

    def test_date_update_when_attachment_deleted(self):
        """ Object date_update updated when attachment deleted """
        attachment = AttachmentFactory(content_object=self.object)
        with freeze_time("2022-07-04T15:00:00+00:00"):
            attachment.delete()
        self.object.refresh_from_db()
        # object date_update has been updated with current datetime
        self.assertEqual(self.object.date_update.isoformat(), "2022-07-04T15:00:00+00:00")

    def test_date_update_when_attachment_accessibility_added(self):
        """ Object date_update updated when attachment accessibility added """
        with freeze_time("2022-07-04T14:00:00+00:00"):
            # add attachment
            AttachmentAccessibilityFactory(content_object=self.object)
        self.object.refresh_from_db()
        # object date_update has been updated with current datetime
        self.assertEqual(self.object.date_update.isoformat(), "2022-07-04T14:00:00+00:00")

    def test_date_update_when_attachment_accessibility_updated(self):
        """ Object date_update updated when attachment accessibility updated """
        # add attachment
        attachment = AttachmentAccessibilityFactory(content_object=self.object)
        with freeze_time("2022-07-04T15:00:00+00:00"):
            attachment.save()
        self.object.refresh_from_db()
        # object date_update has been updated with current datetime
        self.assertEqual(self.object.date_update.isoformat(), "2022-07-04T15:00:00+00:00")

    def test_date_update_when_attachment_accessibility_deleted(self):
        """ Object date_update updated when attachment accessibility deleted """
        attachment = AttachmentAccessibilityFactory(content_object=self.object)
        with freeze_time("2022-07-04T15:00:00+00:00"):
            attachment.delete()
        self.object.refresh_from_db()
        # object date_update has been updated with current datetime
        self.assertEqual(self.object.date_update.isoformat(), "2022-07-04T15:00:00+00:00")
