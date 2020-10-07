from django.test import TestCase

from geotrek.flatpages.factories import FlatPageFactory
from geotrek.flatpages.models import FlatPage


class FlatPageModelTest(TestCase):
    def test_slug_is_taken_from_title(self):
        fp = FlatPageFactory(title="C'est pour toi")
        self.assertEqual(fp.slug, 'cest-pour-toi')

    def test_target_is_all_by_default(self):
        fp = FlatPageFactory()
        self.assertEqual(fp.target, 'all')

    def test_publication_date_is_filled_if_published(self):
        fp = FlatPageFactory()
        fp.save()
        self.assertIsNone(fp.publication_date)
        fp.published = True
        fp.save()
        self.assertIsNotNone(fp.publication_date)

    def test_validation_does_not_fail_if_url_and_content_are_falsy(self):
        fp = FlatPageFactory(external_url="  ",
                             content="<p></p>")
        fp.clean()

    def test_validation_does_not_fail_if_url_is_none(self):
        fp = FlatPageFactory(external_url=None,
                             content="<p></p>")
        fp.clean()

    def test_retrieve_by_order(self):
        try:
            fp = FlatPageFactory.create_batch(5)
            for index, flatpage in enumerate(FlatPage.objects.all()):
                if index == 0:
                    continue
                self.assertGreater(flatpage.order, int(fp[index - 1].order))
        finally:
            for f in fp:
                f.clean()

    def test_retrieve_by_id_if_order_is_the_same(self):
        try:
            fp = FlatPageFactory.create_batch(5, order=0)
            for index, flatpage in enumerate(FlatPage.objects.all()):
                if index == 0:
                    continue
                self.assertGreater(flatpage.id, fp[index - 1].id)
        finally:
            for f in fp:
                f.clean()
