from django.test import TestCase

from geotrek.flatpages.tests.factories import FlatPageFactory, MenuItemFactory


class FlatPageModelTest(TestCase):
    def test_publication_date_is_filled_if_published(self):
        fp = FlatPageFactory()
        fp.save()
        self.assertIsNone(fp.publication_date)
        fp.published = True
        fp.save()
        self.assertIsNotNone(fp.publication_date)

    def test_move_child_with_modeltranslation_compat(self):
        parent = FlatPageFactory()
        child = FlatPageFactory()

        FlatPageFactory._meta.model.objects.get(pk=child.pk).move(
            FlatPageFactory._meta.model.objects.get(pk=parent.pk), pos="last-child"
        )

        self.assertEqual(
            FlatPageFactory._meta.model.objects.get(pk=child.pk).get_parent().pk, parent.pk
        )


class MenuItemModelTest(TestCase):
    def test_move_child_with_modeltranslation_compat(self):
        parent = MenuItemFactory()
        child = MenuItemFactory()

        MenuItemFactory._meta.model.objects.get(pk=child.pk).move(
            MenuItemFactory._meta.model.objects.get(pk=parent.pk), pos="last-child"
        )

        self.assertEqual(
            MenuItemFactory._meta.model.objects.get(pk=child.pk).get_parent().pk, parent.pk
        )
