import logging
from hashlib import md5
import requests

from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import mail_managers
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


def send_report_managers(report, template_name='feedback/report_email.html'):
    subject = _('Feedback from {email}').format(email=report.email)
    message = render_to_string(template_name, {'report': report})
    mail_managers(subject, message, fail_silently=False)


def post_report_to_suricate(report):
    """Send report to Suricate Rest API"""

    URL = settings.SURICATE_SETTINGS['URL']
    ID_ORIGIN = settings.SURICATE_SETTINGS['ID_ORIGIN']
    PRIVATE_KEY_CLIENT_SERVER = settings.SURICATE_SETTINGS['PRIVATE_KEY_CLIENT_SERVER']
    ID_USER = settings.SURICATE_SETTINGS['ID_USER']
    CHECK = md5((PRIVATE_KEY_CLIENT_SERVER + ID_USER).encode()).hexdigest()

    params = {
        'id_origin': ID_ORIGIN,
        'id_user': ID_USER,
        'lat': report.geom.y,
        'long': report.geom.x,
        'report': report.comment,
        'activite': report.activity.id,
        'nature_prb': report.category.id,
        'ampleur_prb': report.problem_magnitude.id,
        'check': CHECK,
        'os': 'linux',
        'version': '0.1',
    }

    response = requests.post(URL + 'wsSendReport', params)

    logger.debug("Report sent to Suricate API with status {0}".format(response.status_code))

    if response.status_code not in [200, 201]:
        raise Exception("Failed to post on Suricate API")
