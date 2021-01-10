from geotrek.outdoor.factories import SiteFactory, RatingScaleFactory
from django.test import TestCase, override_settings


class SiteTest(TestCase):
    @override_settings(PUBLISHED_BY_LANG=False)
    def test_published_children(self):
        parent = SiteFactory(name='parent')
        SiteFactory(name='child1', parent=parent, published=False)
        SiteFactory(name='child2', parent=parent, published=True)
        self.assertQuerysetEqual(parent.published_children, ['<Site: child2>'])

    def test_published_children_by_lang(self):
        parent = SiteFactory(name='parent')
        SiteFactory(name='child1', parent=parent, published=False)
        SiteFactory(name='child2', parent=parent, published_en=True)
        SiteFactory(name='child3', parent=parent, published_fr=True)
        self.assertQuerysetEqual(parent.published_children, ['<Site: child2>', '<Site: child3>'])


class RatingScaleTest(TestCase):
    def test_ratingscale_str(self):
        scale = RatingScaleFactory.create(name='Bar', practice__name='Foo')
        self.assertEqual(str(scale), 'Bar (Foo)')
