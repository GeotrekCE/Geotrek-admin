from django.test import TestCase

from geotrek.flatpages.tests.factories import FlatPageFactory


class FlatPageModelTest(TestCase):

    def test_publication_date_is_filled_if_published(self):
        fp = FlatPageFactory()
        fp.save()
        self.assertIsNone(fp.publication_date)
        fp.published = True
        fp.save()
        self.assertIsNotNone(fp.publication_date)
