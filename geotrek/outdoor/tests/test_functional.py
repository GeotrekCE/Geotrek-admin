from geotrek.common.tests import CommonTest, GeotrekAPITestCase
from geotrek.outdoor.models import Site, Course
from geotrek.outdoor.tests.factories import SiteFactory, CourseFactory, OutdoorManagerFactory
from geotrek.authent.tests.factories import StructureFactory
from django.test.utils import override_settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _


class SiteViewsTests(GeotrekAPITestCase, CommonTest):
    model = Site
    modelfactory = SiteFactory
    userfactory = OutdoorManagerFactory
    expected_json_geom = {
        'type': 'GeometryCollection',
        'geometries': [{'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]}],
    }
    extra_column_list = ['orientation', 'ratings', 'period']

    def get_expected_json_attrs(self):
        return {
            'accessibility': 'Accessible',
            'advice': 'Warning!',
            'ambiance': 'Party time!',
            'areas': [],
            'children': [],
            'cities': [],
            'description': 'Blah',
            'description_teaser': 'More blah',
            'districts': [],
            'eid': '42',
            'filelist_url': '/paperclip/get/outdoor/site/{}/'.format(self.obj.pk),
            'information_desks': [],
            'labels': [],
            'map_image_url': '/image/site-{}.png'.format(self.obj.pk),
            'name': 'Site',
            'orientation': ['S', 'SW'],
            'parent': None,
            'period': 'Summer',
            'portal': [],
            'practice': {
                'id': self.obj.practice.pk,
                'name': 'Practice',
            },
            'printable': '/api/en/sites/{}/site.pdf'.format(self.obj.pk),
            'publication_date': '2020-03-17',
            'published': True,
            'published_status': [
                {'lang': 'en', 'language': 'English', 'status': True},
                {'lang': 'es', 'language': 'Spanish', 'status': False},
                {'lang': 'fr', 'language': 'French', 'status': False},
                {'lang': 'it', 'language': 'Italian', 'status': False},
            ],
            'slug': 'site',
            'source': [],
            'structure': {
                'id': self.obj.structure.pk,
                'name': 'My structure',
            },
            'themes': [],
            'type': {
                'id': self.obj.type.pk,
                'name': 'Site type'
            },
            'web_links': [],
            'ratings': [],
            'wind': ['N'],
        }

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'structure': StructureFactory.create().pk,
            'name_en': 'test en',
            'name_fr': 'test fr',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates":[0, 0]}]}',
        }

    def get_expected_datatables_attrs(self):
        return {
            'date_update': '17/03/2020 00:00:00',
            'id': self.obj.pk,
            'checkbox': self.obj.checkbox_display,
            'name': self.obj.name_display,
            'super_practices': self.obj.super_practices_display
        }

    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={f'outdoor_{self.model._meta.model_name}_view': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List')().columns,
                             ['id', 'checkbox', 'name', 'orientation', 'ratings', 'period'])

    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={f'outdoor_{self.model._meta.model_name}_export': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList')().columns,
                             ['id', 'orientation', 'ratings', 'period'])


class CourseViewsTests(GeotrekAPITestCase, CommonTest):
    model = Course
    modelfactory = CourseFactory
    userfactory = OutdoorManagerFactory
    expected_json_geom = {
        'type': 'GeometryCollection',
        'geometries': [{'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]}],
    }
    extra_column_list = ['equipment', 'ratings', 'eid']

    def get_expected_json_attrs(self):
        return {
            'advice': 'Warning!',
            'areas': [],
            'cities': [],
            'description': 'Blah',
            'districts': [],
            'duration': 55.0,
            'eid': '43',
            'equipment': 'Rope',
            'accessibility': 'Accessible',
            'filelist_url': '/paperclip/get/outdoor/course/{}/'.format(self.obj.pk),
            'gear': 'Shoes mandatory',
            'height': 42,
            'map_image_url': '/image/course-{}.png'.format(self.obj.pk),
            'name': 'Course',
            'parent_sites': [self.obj.parent_sites.first().pk],
            'points_reference': None,
            'printable': '/api/en/courses/{}/course.pdf'.format(self.obj.pk),
            'publication_date': '2020-03-17',
            'published': True,
            'published_status': [
                {'lang': 'en', 'language': 'English', 'status': True},
                {'lang': 'es', 'language': 'Spanish', 'status': False},
                {'lang': 'fr', 'language': 'French', 'status': False},
                {'lang': 'it', 'language': 'Italian', 'status': False},
            ],
            'slug': 'course',
            'structure': {
                'id': self.obj.structure.pk,
                'name': 'My structure',
            },
            'type': self.obj.type.pk,
            'ratings': [],
            'ratings_description': 'Ths rating is ratable',
        }

    def get_expected_datatables_attrs(self):
        return {
            'date_update': '17/03/2020 00:00:00',
            'id': self.obj.pk,
            'checkbox': self.obj.checkbox_display,
            'name': self.obj.name_display,
            'parent_sites': self.obj.parent_sites_display,
        }

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'structure': StructureFactory.create().pk,
            'parent_sites': [SiteFactory.create().pk],
            'name_en': 'test en',
            'name_fr': 'test fr',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates":[0, 0]}]}',
        }

    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={f'outdoor_{self.model._meta.model_name}_view': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List')().columns,
                             ['id', 'checkbox', 'name', 'equipment', 'ratings', 'eid'])

    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(COLUMNS_LISTS={f'outdoor_{self.model._meta.model_name}_export': self.extra_column_list}):
            self.assertEqual(import_string(f'geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList')().columns,
                             ['id', 'equipment', 'ratings', 'eid'])
