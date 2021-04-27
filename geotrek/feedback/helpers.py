import json
import logging
import urllib.parse
from hashlib import md5

import requests
from django.conf import settings
from django.core.mail import mail_managers
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class SuricateRequestManager:
  
    URL = settings.SURICATE_REPORT_SETTINGS["URL"]
    ID_ORIGIN = settings.SURICATE_REPORT_SETTINGS["ID_ORIGIN"]
    PRIVATE_KEY_CLIENT_SERVER = settings.SURICATE_REPORT_SETTINGS[
        "PRIVATE_KEY_CLIENT_SERVER"
    ]
    CHECK_ORIGIN = (
        f"&check={md5((PRIVATE_KEY_CLIENT_SERVER + ID_ORIGIN).encode()).hexdigest()}"
    )
    USE_AUTH = "AUTH" in settings.SURICATE_REPORT_SETTINGS.keys()
    AUTH = (None, settings.SURICATE_REPORT_SETTINGS["AUTH"])[USE_AUTH]

    def get_from_suricate(self, endpoint, web_service="wsgestion/", url_params={}):
        # Build ever-present URL parameter
        origin_param = f"?id_origin={self.ID_ORIGIN}"
        # Add specific URL parameters
        extra_url_params = urllib.parse.urlencode(url_params)
        # Include alert ID in check when needed
        if "uid_alerte" in url_params:
            id_alert = url_params["uid_alerte"]
            check = f"&check={md5((self.PRIVATE_KEY_CLIENT_SERVER + id_alert + self.ID_ORIGIN).encode()).hexdigest()}"
        else:
            check = self.CHECK_ORIGIN
        # If HTTP Auth required, add to request
        if self.USE_AUTH:
            response = requests.get(
                f"{self.URL}{web_service}{endpoint}{origin_param}{extra_url_params}{check}",
                auth=self.AUTH,
            )
        else:
            response = requests.get(
                f"{self.URL}{web_service}{endpoint}{origin_param}{extra_url_params}{check}",
            )

        # Handle response
        # todo
        if response.status_code not in [200, 201]:
            print(response.status_code)
            raise Exception("Failed to get Suricate API")

        print(json.loads(response.content.decode()))
        return json.loads(response.content.decode())

    def post_to_suricate(self, endpoint, params, web_service="wsgestion/"):
        # If HTTP Auth required, add to request
        if self.USE_AUTH:
            response = requests.post(
                f"{self.URL}{web_service}{endpoint}",
                params,
                auth=self.AUTH,
            )
        else:
            response = requests.post(f"{self.URL}{web_service}{endpoint}", params)
        # Handle response
        # todo
        if response.status_code not in [200, 201]:
            raise Exception("Failed to post on Suricate API")
        return response


def send_report_managers(report, template_name="feedback/report_email.html"):
    subject = _("Feedback from {email}").format(email=report.email)
    message = render_to_string(template_name, {"report": report})
    mail_managers(subject, message, fail_silently=False)


class SuricateMessenger(SuricateRequestManager):
    def post_report(self, report):
        CHECK = md5(
            (self.PRIVATE_KEY_CLIENT_SERVER + report.email).encode()
        ).hexdigest()
        """Send report to Suricate Rest API"""
        params = {
            "id_origin": self.ID_ORIGIN,
            "id_user": report.email,
            "lat": report.geom.y,
            "long": report.geom.x,
            "report": report.comment,
            "activite": report.activity.suricate_id,
            "nature_prb": report.category.suricate_id,
            "ampleur_prb": report.problem_magnitude.suricate_id,
            "check": CHECK,
            "os": "linux",
            "version": settings.VERSION,
        }

        self.post_to_suricate("wsSendReport", params, "wsstandard")

    def lock_alert(self, id_alert):
        """Lock report on Suricate Rest API"""
        return self.get_from_suricate(
            "wsLockAlert", extra_url_params={"uid_alerte": id_alert}
        )

    def unlock_alert(self, id_alert):
        """Unlock report on Suricate Rest API"""
        return self.get_from_suricate(
            "wsUnlockAlert", url_params={"uid_alerte": id_alert}
        )

    def post_message(self, message, id_alert):
        """Send message to sentinel through Suricate Rest API"""
        check = md5(
            (self.PRIVATE_KEY_CLIENT_SERVER + self.ID_ORIGIN + id_alert).encode()
        ).hexdigest()
        params = {
            "id_origin": self.ID_ORIGIN,
            "uid_alerte": id_alert,
            "message": message,
            "check": check,
        }

        self.post_to_suricate("wsSendMessageSentinelle", params)

    def update_status(self, id_alert, new_status, message):
        """Update status for given report on Suricate Rest API"""
        check = md5(
            (self.PRIVATE_KEY_CLIENT_SERVER + self.ID_ORIGIN + id_alert).encode()
        ).hexdigest()

        params = {
            "id_origin": self.ID_ORIGIN,
            "uid_alerte": id_alert,
            "statut": new_status,
            "txt_changestatut": message,
            "check": check,
        }
        self.post_to_suricate("wsUpdateStatus", params)

    def update_gps(self, id_alert, gps_lat, gps_long):
        """Update report GPS coordinates on Suricate Rest API"""
        self.get_from_suricate(
            "wsUpdateStatus",
            url_params={
                "uid_alerte": id_alert,
                "gpslatitude": gps_lat,
                "gpslongitude": gps_long,
            },
        )
