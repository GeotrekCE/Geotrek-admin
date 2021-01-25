from geotrek.outdoor.factories import SiteFactory, RatingScaleFactory, SectorFactory
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


class SiteSuperTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = SiteFactory(
            practice__name='Bbb',
            practice__sector__name='Bxx',
            orientation=['N', 'S'],
            wind=['N', 'S']
        )
        cls.child = SiteFactory(
            parent=cls.parent,
            practice__name='Aaa',
            practice__sector__name='Axx',
            orientation=['E', 'S'],
            wind=['E', 'S']
        )
        cls.grandchild1 = SiteFactory(
            parent=cls.child,
            practice=cls.parent.practice,
            orientation=cls.parent.orientation,
            wind=cls.parent.wind
        )
        cls.grandchild2 = SiteFactory(
            parent=cls.child,
            practice=None,
            orientation=[],
            wind=[]
        )

    def test_super_practices_descendants(self):
        self.assertQuerysetEqual(self.parent.super_practices, ['<Practice: Aaa>', '<Practice: Bbb>'])

    def test_super_practices_ascendants(self):
        self.assertQuerysetEqual(self.grandchild2.super_practices, ['<Practice: Aaa>'])

    def test_super_sectors_descendants(self):
        self.assertQuerysetEqual(self.parent.super_sectors, ['<Sector: Axx>', '<Sector: Bxx>'])

    def test_super_sectors_ascendants(self):
        self.assertQuerysetEqual(self.grandchild2.super_sectors, ['<Sector: Axx>'])

    def test_super_orientation_descendants(self):
        self.assertEqual(self.parent.super_orientation, ['N', 'E', 'S'])

    def test_super_orientation_ascendants(self):
        self.assertEqual(self.grandchild2.super_orientation, ['E', 'S'])

    def test_super_wind_descendants(self):
        self.assertEqual(self.parent.super_wind, ['N', 'E', 'S'])

    def test_super_wind_ascendants(self):
        self.assertEqual(self.grandchild2.super_wind, ['E', 'S'])


class SectorTest(TestCase):
    def test_sector_str(self):
        sector = SectorFactory.create(name='Baz')
        self.assertEqual(str(sector), 'Baz')


class RatingScaleTest(TestCase):
    def test_ratingscale_str(self):
        scale = RatingScaleFactory.create(name='Bar', practice__name='Foo')
        self.assertEqual(str(scale), 'Bar (Foo)')
