import requests

from django.utils.translation import ugettext_lazy as _
from django.test import LiveServerTestCase
from django.contrib.auth.models import Permission
from mapentity.factories import SuperUserFactory, UserFactory
from mapentity.helpers import smart_urljoin

from geotrek.common.tests import CommonTest
from geotrek.feedback import models as feedback_models
from geotrek.feedback import factories as feedback_factories


class ReportViewsTest(CommonTest):
    model = feedback_models.Report
    modelfactory = feedback_factories.ReportFactory
    userfactory = SuperUserFactory

    def get_bad_data(self):
        return {'geom': 'FOO'}, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'geom': '{"type": "Point", "coordinates": [0, 0]}',
            'name': 'You Yeah',
            'email': 'yeah@you.com',
        }


class CreateReportsAPITest(LiveServerTestCase):
    def setUp(self):
        self.user = UserFactory(password='booh')
        perm = Permission.objects.get_by_natural_key('add_report', 'feedback', 'report')
        self.user.user_permissions.add(perm)

        self.login_url = smart_urljoin(self.live_server_url, '/login/')
        self.add_url = smart_urljoin(self.live_server_url, '/report/add/')

        self.session = requests.Session()
        self.login()

        self.data = {
            'geom': '{"type": "Point", "coordinates": [0, 0]}',
            'name': 'You Yeah',
            'email': 'yeah@you.com'
        }

    def login(self):
        response = self.session.get(self.login_url)
        csrftoken = response.cookies.get('csrftoken', '')
        response = self.session.post(self.login_url,
                                     {'username': self.user.username,
                                      'password': 'booh',
                                      'csrfmiddlewaretoken': csrftoken},
                                     allow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def post_report_data(self, data):
        response = self.session.get(self.add_url,
                                    allow_redirects=False)
        self.assertEqual(response.status_code, 200)
        csrf = response.cookies['csrftoken']
        data['csrfmiddlewaretoken'] = csrf
        response = self.session.post(self.add_url, data=data,
                                     allow_redirects=False)
        self.assertEqual(response.status_code, 302)
        return response

    def test_reports_can_be_created_using_post(self):
        self.post_report_data(self.data)
        self.assertTrue(feedback_models.Report.objects.filter(name='You Yeah').exists())

    def test_reports_can_be_created_without_geom(self):
        self.data.pop('geom')
        self.post_report_data(self.data)
        self.assertTrue(feedback_models.Report.objects.filter(name='You Yeah').exists())
