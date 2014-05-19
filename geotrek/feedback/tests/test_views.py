from mapentity.factories import SuperUserFactory
from django.utils.translation import ugettext_lazy as _
from django.test import LiveServerTestCase

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
    pass