from django.test import TestCase

from geotrek.flatpages.tests.factories import FlatPageFactory


class FlatPageModelTest(TestCase):

    # FIXME: to remove? Slug was used for sync randov2
    def test_slug_is_taken_from_title(self):
        fp = FlatPageFactory(title="C'est pour toi")
        self.assertEqual(fp.slug, 'cest-pour-toi')

    # FIXME: to remove? Should be tested in the mixin
    def test_publication_date_is_filled_if_published(self):
        fp = FlatPageFactory()
        fp.save()
        self.assertIsNone(fp.publication_date)
        fp.published = True
        fp.save()
        self.assertIsNotNone(fp.publication_date)

    # FIXME: to remove?
    def test_is_public(self):
        fp = FlatPageFactory(title="Blabla", published_fr=True)
        self.assertTrue(fp.is_public())
