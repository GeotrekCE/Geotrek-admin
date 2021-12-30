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

    URL = None
    ID_ORIGIN = None
    PRIVATE_KEY_CLIENT_SERVER = None
    PRIVATE_KEY_SERVER_CLIENT = None
    CHECK_CLIENT = None
    CHECK_SERVER = None

    USE_AUTH = None
    AUTH = None

    def check_response_integrity(self, response, id_alert=""):
        if response.status_code not in [200, 201]:
            raise Exception(
                f"Failed to access Suricate API - Status code: {response.status_code}"
            )
        else:
            data = json.loads(response.content.decode())
            if ("code_ok" in data) and (data["code_ok"] == 'false'):
                raise Exception(
                    f"Unsuccesful request on Suricate API:   [{data['error']['code']} - {data['error']['message']} - {data['message']}]"
                )
            return data
        #  THIS SHOULD BE A THING but the documentation is at war with the API
        #         else:
        #         if id_alert:
        #             check = self.PRIVATE_KEY_SERVER_CLIENT
        #         else:
        #             check = md5((self.PRIVATE_KEY_CLIENT_SERVER + id_alert + self.ID_ORIGIN).encode()).hexdigest()
        #         if check != data["check"]:
        #             raise Exception(f"Integrity of Suricate response compromised: expected checksum {check}, got checksum {data['check']}")

    def get_from_suricate_no_integrity_check(self, endpoint, url_params={}):
        # Build ever-present URL parameter
        origin_param = f"?id_origin={self.ID_ORIGIN}"
        # Add specific URL parameters
        extra_url_params = urllib.parse.urlencode(url_params)
        # Include alert ID in check when needed
        if "uid_alerte" in url_params:
            id_alert = str(url_params["uid_alerte"])
            check = f"&check={md5((self.PRIVATE_KEY_CLIENT_SERVER + self.ID_ORIGIN + id_alert).encode()).hexdigest()}"
        else:
            check = self.CHECK_CLIENT
        # If HTTP Auth required, add to request
        if self.USE_AUTH:
            response = requests.get(
                f"{self.URL}{endpoint}{origin_param}&{extra_url_params}{check}",
                auth=self.AUTH,
            )
        else:
            response = requests.get(
                f"{self.URL}{endpoint}{origin_param}&{extra_url_params}{check}",
            )
        return response

    def get_from_suricate(self, endpoint, url_params={}):
        response = self.get_from_suricate_no_integrity_check(endpoint, url_params)
        return self.check_response_integrity(response)

    def post_to_suricate(self, endpoint, params=None):
        # If HTTP Auth required, add to request
        if self.USE_AUTH:
            response = requests.post(
                f"{self.URL}{endpoint}",
                params,
                auth=self.AUTH,
            )
        else:
            response = requests.post(f"{self.URL}{endpoint}", params)
        self.check_response_integrity(response)

    def get_attachment_from_suricate(self, url):
        if self.USE_AUTH:
            response = requests.get(
                url,
                auth=self.AUTH,
            )
        else:
            response = requests.get(
                url,
            )
        if response.status_code not in [200, 201]:
            logger.warning(
                f"Failed to access Suricate attachment - Status code: {response.status_code}"
            )
        return response

    def print_response_OK_or_KO(self, response):
        if response.status_code not in [200, 201]:
            print(f"KO - Status code: {response.status_code}")
        else:
            data = json.loads(response.content.decode())
            if "code_ok" in data and not bool(data["code_ok"]):
                print(f"KO:   [{data['error']['code']} - {data['error']['message']}]")
            elif "code_ok" in data and bool(data["code_ok"]):
                print("OK")

    def test_suricate_connection(self):
        response = self.get_from_suricate_no_integrity_check(endpoint="wsGetActivities")
        self.print_response_OK_or_KO(response)


class SuricateStandardRequestManager(SuricateRequestManager):

    def __init__(self):
        self.URL = settings.SURICATE_REPORT_SETTINGS["URL"]
        self.ID_ORIGIN = settings.SURICATE_REPORT_SETTINGS["ID_ORIGIN"]
        self.PRIVATE_KEY_CLIENT_SERVER = settings.SURICATE_REPORT_SETTINGS[
            "PRIVATE_KEY_CLIENT_SERVER"
        ]
        self.PRIVATE_KEY_SERVER_CLIENT = settings.SURICATE_REPORT_SETTINGS[
            "PRIVATE_KEY_SERVER_CLIENT"
        ]
        self.CHECK_CLIENT = (
            f"&check={md5((self.PRIVATE_KEY_CLIENT_SERVER + self.ID_ORIGIN).encode()).hexdigest()}"
        )
        self.CHECK_SERVER = md5((self.PRIVATE_KEY_SERVER_CLIENT + self.ID_ORIGIN).encode()).hexdigest()

        self.USE_AUTH = "AUTH" in settings.SURICATE_REPORT_SETTINGS.keys()
        self.AUTH = settings.SURICATE_REPORT_SETTINGS["AUTH"] if self.USE_AUTH else None


class SuricateGestionRequestManager(SuricateRequestManager):

    def __init__(self):
        self.URL = settings.SURICATE_MANAGEMENT_SETTINGS["URL"]
        self.ID_ORIGIN = settings.SURICATE_MANAGEMENT_SETTINGS["ID_ORIGIN"]
        self.PRIVATE_KEY_CLIENT_SERVER = settings.SURICATE_MANAGEMENT_SETTINGS[
            "PRIVATE_KEY_CLIENT_SERVER"
        ]
        self.PRIVATE_KEY_SERVER_CLIENT = settings.SURICATE_MANAGEMENT_SETTINGS[
            "PRIVATE_KEY_SERVER_CLIENT"
        ]
        self.CHECK_CLIENT = (
            f"&check={md5((self.PRIVATE_KEY_CLIENT_SERVER + self.ID_ORIGIN).encode()).hexdigest()}"
        )
        self.CHECK_SERVER = md5((self.PRIVATE_KEY_SERVER_CLIENT + self.ID_ORIGIN).encode()).hexdigest()

        self.USE_AUTH = "AUTH" in settings.SURICATE_MANAGEMENT_SETTINGS.keys()
        self.AUTH = settings.SURICATE_MANAGEMENT_SETTINGS["AUTH"] if self.USE_AUTH else None


def test_suricate_connection():
    print("API Standard :")
    SuricateStandardRequestManager().test_suricate_connection()
    print("API Gestion :")
    SuricateGestionRequestManager().test_suricate_connection()


def send_report_to_managers(report, template_name="feedback/report_email.html"):
    subject = _("Feedback from {email}").format(email=report.email)
    message = render_to_string(template_name, {"report": report})
    mail_managers(subject, message, fail_silently=False)


def send_reports_to_managers(template_name="feedback/reports_email.html"):
    subject = _("New reports from Suricate")
    message = render_to_string(template_name)
    mail_managers(subject, message, fail_silently=False)


class SuricateMessenger:

    def __init__(self):
        self.standard_manager = SuricateStandardRequestManager()
        self.gestion_manager = SuricateGestionRequestManager()

    def post_report(self, report):
        manager = self.standard_manager
        check = md5(
            (manager.PRIVATE_KEY_CLIENT_SERVER + report.email).encode()
        ).hexdigest()
        """Send report to Suricate Rest API"""
        activity_id = report.activity.suricate_id if report.activity is not None else None
        category_id = report.category.suricate_id if report.category is not None else None
        magnitude_id = report.problem_magnitude.suricate_id if report.problem_magnitude is not None else None
        gps_geom = report.geom.transform(4326, clone=True)
        params = {
            "id_origin": manager.ID_ORIGIN,
            "id_user": report.email,
            "lat": gps_geom.y,
            "long": gps_geom.x,
            "report": report.comment,
            "activite": activity_id,
            "nature_prb": category_id,
            "ampleur_prb": magnitude_id,
            "check": check,
            "os": "linux",
            "version": settings.VERSION,
        }
        manager.post_to_suricate("wsSendReport", params)

    # TODO use in workflow
    # def lock_alert(self, id_alert):
    #     """Lock report on Suricate Rest API"""
    #     return self.gestion_manager.get_from_suricate(
    #         "wsLockAlert", extra_url_params={"uid_alerte": id_alert}
    #     )

    # def unlock_alert(self, id_alert):
    #     """Unlock report on Suricate Rest API"""
    #     return self.gestion_manager.get_from_suricate(
    #         "wsUnlockAlert", url_params={"uid_alerte": id_alert}
    #     )

    def update_status(self, id_alert, new_status, message):
        """Update status for given report on Suricate Rest API"""
        check = md5(
            (self.gestion_manager.PRIVATE_KEY_CLIENT_SERVER + self.gestion_manager.ID_ORIGIN + str(id_alert)).encode()
        ).hexdigest()

        params = {
            "id_origin": self.gestion_manager.ID_ORIGIN,
            "uid_alerte": id_alert,
            "statut": new_status,
            "txt_changestatut": message,
            "check": check,
        }
        self.gestion_manager.post_to_suricate("wsUpdateStatus", params)

    # def update_gps(self, id_alert, gps_lat, gps_long):
    #     """Update report GPS coordinates on Suricate Rest API"""
    #     self.gestion_manager.get_from_suricate(
    #         "wsUpdateStatus",
    #         url_params={
    #             "uid_alerte": id_alert,
    #             "gpslatitude": gps_lat,
    #             "gpslongitude": gps_long,
    #         },
    #     )

    def message_sentinel(self, id_alert, message):
        check = md5(
            (self.gestion_manager.PRIVATE_KEY_CLIENT_SERVER + self.gestion_manager.ID_ORIGIN + str(id_alert)).encode()
        ).hexdigest()
        """Send report to Suricate Rest API"""
        params = {
            "id_origin": self.gestion_manager.ID_ORIGIN,
            "uid_alerte": id_alert,
            "message": message,
            "check": check,
        }

        self.gestion_manager.post_to_suricate("wsSendMessageSentinelle", params)
