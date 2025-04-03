from unittest import mock

from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from mapentity.tests.factories import SuperUserFactory

from geotrek.outdoor import views as course_views
from geotrek.outdoor.models import Site
from geotrek.outdoor.tests.factories import CourseFactory, SiteFactory
from geotrek.tourism.tests.test_views import PNG_BLACK_PIXEL
from geotrek.trekking.tests.factories import POIFactory


class SiteCustomViewTests(TestCase):
    @mock.patch("mapentity.helpers.requests.get")
    def test_public_document_pdf(self, mocked):
        site = SiteFactory.create(published=True)
        url = "/api/en/sites/{pk}/slug.pdf".format(pk=site.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(TREK_EXPORT_POI_LIST_LIMIT=1)
    @mock.patch("mapentity.models.MapEntityMixin.prepare_map_image")
    @mock.patch("mapentity.models.MapEntityMixin.get_attributes_html")
    def test_site_export_poi_list_limit(self, mocked_prepare, mocked_attributes):
        site = SiteFactory.create(
            geom="SRID=2154;GEOMETRYCOLLECTION (POINT (700000 6600000))"
        )
        POIFactory.create(published=True)
        self.assertEqual(len(site.pois), 1)
        view = course_views.SiteDocumentPublic()
        view.object = site
        view.request = RequestFactory().get("/")
        view.kwargs = {}
        view.kwargs[view.pk_url_kwarg] = site.pk
        context = view.get_context_data()
        self.assertEqual(len(context["pois"]), 1)

    def test_init_form_with_parent_site(self):
        user = SuperUserFactory()
        self.client.force_login(user)
        parent = SiteFactory(name="Parent name")
        response = self.client.get(
            reverse("outdoor:site_add"), {"parent_sites": parent.pk}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        selected = f'<option value="{parent.pk}" selected> {parent.name}</option>'
        self.assertContains(response, selected)


class CourseCustomViewTests(TestCase):
    @mock.patch("mapentity.helpers.requests.get")
    def test_public_document_pdf(self, mocked):
        course = CourseFactory.create(published=True)
        url = "/api/en/courses/{pk}/slug.pdf".format(pk=course.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(TREK_EXPORT_POI_LIST_LIMIT=1)
    @mock.patch("mapentity.models.MapEntityMixin.prepare_map_image")
    @mock.patch("mapentity.models.MapEntityMixin.get_attributes_html")
    def test_course_export_poi_list_limit(self, mocked_prepare, mocked_attributes):
        course = CourseFactory.create(
            geom="SRID=2154;GEOMETRYCOLLECTION (POINT (700000 6600000))"
        )
        POIFactory.create(published=True)
        self.assertEqual(len(course.pois), 1)
        view = course_views.CourseDocumentPublic()
        view.object = course
        view.request = RequestFactory().get("/")
        view.kwargs = {}
        view.kwargs[view.pk_url_kwarg] = course.pk
        context = view.get_context_data()
        self.assertEqual(len(context["pois"]), 1)


class SiteDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_view_delete_site(self):
        self.site_1 = SiteFactory.create(name="site_1")
        response = self.client.get(
            reverse("outdoor:site_delete", args=["%s" % self.site_1.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Do you really wish to delete <strong>%s</strong> ?" % (self.site_1.name),
        )

        self.site_2 = SiteFactory.create(name="site_2")
        self.site_3 = SiteFactory.create(name="site_3", parent=self.site_2)
        response = self.client.get(
            reverse("outdoor:site_delete", args=["%s" % self.site_2.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "You can't delete <strong>%s</strong> because it has child outdoor sites associated with it. Modify or delete these child outdoor sites before proceeding."
            % (self.site_2.name),
        )

    def test_delete_site(self):
        site_1 = SiteFactory.create(name="site_1")
        site_2 = SiteFactory.create(name="site_2")
        self.assertEqual(Site.objects.count(), 2)
        response = self.client.post(
            reverse("outdoor:site_delete", args=["%s" % site_2.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Site.objects.count(), 1)
        self.assertEqual(Site.objects.filter(pk=site_1.pk).exists(), True)
