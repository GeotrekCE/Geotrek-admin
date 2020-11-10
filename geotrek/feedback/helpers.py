import logging
from hashlib import md5
import requests

from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import mail_managers
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def send_report_managers(report, template_name='feedback/report_email.html'):
    subject = _('Feedback from {email}').format(email=report.email)
    message = render_to_string(template_name, {'report': report})
    mail_managers(subject, message, fail_silently=False)


def post_report_to_suricate(report):
    """Send report to Suricate Rest API"""

    URL = settings.SURICATE_REPORT_SETTINGS['URL']
    ID_ORIGIN = settings.SURICATE_REPORT_SETTINGS['ID_ORIGIN']
    PRIVATE_KEY_CLIENT_SERVER = settings.SURICATE_REPORT_SETTINGS['PRIVATE_KEY_CLIENT_SERVER']
    CHECK = md5((PRIVATE_KEY_CLIENT_SERVER + report.email).encode()).hexdigest()

    params = {
        'id_origin': ID_ORIGIN,
        'id_user': report.email,
        'lat': report.geom.y,
        'long': report.geom.x,
        'report': report.comment,
        'activite': report.activity.suricate_id,
        'nature_prb': report.category.suricate_id,
        'ampleur_prb': report.problem_magnitude.suricate_id,
        'check': CHECK,
        'os': 'linux',
        'version': settings.VERSION,
    }

    # If HTTP Auth required, add to request
    if 'AUTH' in settings.SURICATE_REPORT_SETTINGS.keys():
        response = requests.post(URL + 'wsSendReport', params, auth=settings.SURICATE_REPORT_SETTINGS['AUTH'])
    else:
        response = requests.post(URL + 'wsSendReport', params)

    if response.status_code not in [200, 201]:
        raise Exception("Failed to post on Suricate API")
