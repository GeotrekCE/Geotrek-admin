from geotrek.common.tests import CommonTest
from geotrek.outdoor.models import Site, Course
from geotrek.outdoor.factories import SiteFactory, CourseFactory, OutdoorManagerFactory
from geotrek.authent.factories import StructureFactory
from django.utils.translation import gettext as _


class SiteViewsTests(CommonTest):
    model = Site
    modelfactory = SiteFactory
    userfactory = OutdoorManagerFactory
    expected_json_geom = {
        'type': 'GeometryCollection',
        'geometries': [{'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]}],
    }

    def get_expected_json_attrs(self):
        return {
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
            'ratings_min': [],
            'ratings_max': [],
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


class CourseViewsTests(CommonTest):
    model = Course
    modelfactory = CourseFactory
    userfactory = OutdoorManagerFactory
    expected_json_geom = {
        'type': 'GeometryCollection',
        'geometries': [{'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]}],
    }

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
            'filelist_url': '/paperclip/get/outdoor/course/{}/'.format(self.obj.pk),
            'gear': 'Shoes mandatory',
            'height': 42,
            'map_image_url': '/image/course-{}.png'.format(self.obj.pk),
            'name': 'Course',
            'site': self.obj.site.pk,
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

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'structure': StructureFactory.create().pk,
            'site': SiteFactory.create().pk,
            'name_en': 'test en',
            'name_fr': 'test fr',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates":[0, 0]}]}',
        }
