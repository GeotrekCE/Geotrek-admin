import copy
import json
import logging
import urllib.parse
from hashlib import md5

import requests
from django.conf import settings

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

    def check_response_integrity(self, response):
        if response.status_code not in [200, 201]:
            raise Exception(
                f"Failed to access Suricate API - Status code: {response.status_code}"
            )
        else:
            data = json.loads(response.content.decode())
            if ("code_ok" in data) and (data["code_ok"] == "false"):
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
        all_url_params = copy.deepcopy(url_params)
        all_url_params["id_origin"] = self.ID_ORIGIN
        # Include alert ID in check when needed
        if "uid_alerte" in url_params:
            id_alert = str(url_params["uid_alerte"])
            check = md5(
                (self.PRIVATE_KEY_CLIENT_SERVER + self.ID_ORIGIN + id_alert).encode()
            ).hexdigest()
        else:
            check = self.CHECK_CLIENT
        all_url_params["check"] = check
        # Add URL parameters
        encoded_url_params = urllib.parse.urlencode(all_url_params)
        # If HTTP Auth required, add to request
        if self.USE_AUTH:
            response = requests.get(
                f"{self.URL}{endpoint}?{encoded_url_params}",
                auth=self.AUTH,
            )
        else:
            response = requests.get(
                f"{self.URL}{endpoint}?{encoded_url_params}",
            )
        return response

    def save_pending_request(self, request_type, endpoint, params, error_message):
        # Save request to database
        if self.URL == settings.SURICATE_REPORT_SETTINGS["URL"]:
            which_api = "STA"
        else:
            which_api = "MAN"
        # UUID cannot be JSON serialized, turn them into strings before
        if "uid_alerte" in params:
            uuid = params.pop("uid_alerte")
            params["uid_alerte"] = str(uuid)
        self.pending_requests_model.objects.create(
            request_type=request_type,
            api=which_api,
            endpoint=endpoint,
            params=json.dumps(params),
            error_message=error_message,
        )

    def get_suricate(self, endpoint, url_params={}):
        response = self.get_from_suricate_no_integrity_check(endpoint, url_params)
        return self.check_response_integrity(response)

    def get_or_retry_from_suricate(self, endpoint, url_params={}):
        try:
            return self.get_suricate(endpoint, url_params)
        except Exception as e:
            logger.exception(e)  # This sends an email to admins :)
            self.save_pending_request("GET", endpoint, url_params, e.args)

    def post_suricate(self, endpoint, params=None):
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

    def post_or_retry_to_suricate(self, endpoint, params=None):
        try:
            self.post_suricate(endpoint, params)
        except Exception as e:
            logger.exception(e)  # Send alert to admins
            self.save_pending_request("POST", endpoint, params, e.args)

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
                "Failed to access Suricate attachment - Status code: %s",
                response.status_code,
            )
        return response

    def print_response_OK_or_KO(self, response):
        if response.status_code not in [200, 201]:
            return f"KO - Status code: {response.status_code}"
        else:
            data = json.loads(response.content.decode())

            if "code_ok" in data and (data["code_ok"] == "false"):
                return f"KO:   [{data['error']['code']} - {data['error']['message']}]"
            elif "code_ok" in data and (data["code_ok"] == "true"):
                return "OK"

    def test_suricate_connection(self):
        response = self.get_from_suricate_no_integrity_check(endpoint="wsGetActivities")
        return self.print_response_OK_or_KO(response)


class SuricateStandardRequestManager(SuricateRequestManager):
    def __init__(self, pending_requests_model=None):
        self.pending_requests_model = pending_requests_model
        self.URL = settings.SURICATE_REPORT_SETTINGS["URL"]
        self.ID_ORIGIN = settings.SURICATE_REPORT_SETTINGS["ID_ORIGIN"]
        self.PRIVATE_KEY_CLIENT_SERVER = settings.SURICATE_REPORT_SETTINGS[
            "PRIVATE_KEY_CLIENT_SERVER"
        ]
        self.PRIVATE_KEY_SERVER_CLIENT = settings.SURICATE_REPORT_SETTINGS[
            "PRIVATE_KEY_SERVER_CLIENT"
        ]
        self.CHECK_CLIENT = md5((self.PRIVATE_KEY_CLIENT_SERVER).encode()).hexdigest()
        self.CHECK_SERVER = md5(
            (self.PRIVATE_KEY_SERVER_CLIENT + self.ID_ORIGIN).encode()
        ).hexdigest()

        self.USE_AUTH = "AUTH" in settings.SURICATE_REPORT_SETTINGS.keys()
        self.AUTH = settings.SURICATE_REPORT_SETTINGS["AUTH"] if self.USE_AUTH else None


class SuricateGestionRequestManager(SuricateRequestManager):
    def __init__(self, pending_requests_model=None):
        self.pending_requests_model = pending_requests_model
        self.URL = settings.SURICATE_MANAGEMENT_SETTINGS["URL"]
        self.ID_ORIGIN = settings.SURICATE_MANAGEMENT_SETTINGS["ID_ORIGIN"]
        self.PRIVATE_KEY_CLIENT_SERVER = settings.SURICATE_MANAGEMENT_SETTINGS[
            "PRIVATE_KEY_CLIENT_SERVER"
        ]
        self.PRIVATE_KEY_SERVER_CLIENT = settings.SURICATE_MANAGEMENT_SETTINGS[
            "PRIVATE_KEY_SERVER_CLIENT"
        ]
        self.CHECK_CLIENT = md5(
            (self.PRIVATE_KEY_CLIENT_SERVER + self.ID_ORIGIN).encode()
        ).hexdigest()
        self.CHECK_SERVER = md5(
            (self.PRIVATE_KEY_SERVER_CLIENT + self.ID_ORIGIN).encode()
        ).hexdigest()

        self.USE_AUTH = "AUTH" in settings.SURICATE_MANAGEMENT_SETTINGS.keys()
        self.AUTH = (
            settings.SURICATE_MANAGEMENT_SETTINGS["AUTH"] if self.USE_AUTH else None
        )


class SuricateMessenger:
    def __init__(self, pending_requests_model=None):
        self.pending_requests_model = pending_requests_model
        self.standard_manager = SuricateStandardRequestManager(pending_requests_model)
        self.gestion_manager = SuricateGestionRequestManager(pending_requests_model)

    def post_report(self, report):
        manager = self.standard_manager
        check = md5(
            (manager.PRIVATE_KEY_CLIENT_SERVER + report.email).encode()
        ).hexdigest()
        """Send report to Suricate Rest API"""
        activity_id = (
            report.activity.identifier if report.activity is not None else None
        )
        category_id = (
            report.category.identifier if report.category is not None else None
        )
        magnitude_id = (
            report.problem_magnitude.identifier
            if report.problem_magnitude is not None
            else None
        )
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
        manager.post_or_retry_to_suricate("wsSendReport", params)

    def lock_alert(self, id_alert):
        """Lock report on Suricate Rest API"""
        return self.gestion_manager.get_or_retry_from_suricate(
            "wsLockAlert", url_params={"uid_alerte": id_alert}
        )

    def unlock_alert(self, id_alert):
        """Unlock report on Suricate Rest API"""
        return self.gestion_manager.get_or_retry_from_suricate(
            "wsUnlockAlert", url_params={"uid_alerte": id_alert}
        )

    def update_status(
        self,
        id_alert,
        new_status,
        message_sentinel="No message",
        message_admins="No message",
    ):
        """Update status for given report on Suricate Rest API"""
        check = md5(
            (
                self.gestion_manager.PRIVATE_KEY_CLIENT_SERVER
                + self.gestion_manager.ID_ORIGIN
                + str(id_alert)
            ).encode()
        ).hexdigest()

        params = {
            "id_origin": self.gestion_manager.ID_ORIGIN,
            "uid_alerte": id_alert,
            "statut": new_status,
            "txt_changestatut": message_admins,
            "txt_changestatut_sentinelle": message_sentinel,
            "check": check,
        }
        self.gestion_manager.post_or_retry_to_suricate("wsUpdateStatus", params)

    def update_gps(self, id_alert, gps_lat, gps_long, force=False):
        """Update report GPS coordinates on Suricate Rest API"""
        url_params = {
            "uid_alerte": id_alert,
            "gpslatitude": f"{gps_lat:.6f}",
            "gpslongitude": f"{gps_long:.6f}",
        }
        if force:
            url_params["force_update"] = 1
        self.gestion_manager.get_or_retry_from_suricate(
            "wsUpdateGPS", url_params=url_params
        )

    def message_sentinel(self, id_alert, message):
        check = md5(
            (
                self.gestion_manager.PRIVATE_KEY_CLIENT_SERVER
                + self.gestion_manager.ID_ORIGIN
                + str(id_alert)
            ).encode()
        ).hexdigest()
        """Send report to Suricate Rest API"""
        params = {
            "id_origin": self.gestion_manager.ID_ORIGIN,
            "uid_alerte": id_alert,
            "message": message,
            "check": check,
        }

        self.gestion_manager.post_or_retry_to_suricate(
            "wsSendMessageSentinelle", params
        )

    def retry_failed_requests(self):
        for failed_request in self.pending_requests_model.objects.all():
            if failed_request.api == "STA":
                request_manager = self.standard_manager
            else:
                request_manager = self.gestion_manager
            try:
                # Calls either request_manager.get_suricate() or request_manager.post_suricate()
                getattr(
                    request_manager, f"{failed_request.request_type.lower()}_suricate"
                )(failed_request.endpoint, json.loads(failed_request.params))
                # Delete this pending request if it was successful
                failed_request.delete()
            except Exception as e:
                failed_request.retries += 1
                failed_request.error_message = str(
                    e.args
                )  # Keep last exception message
                failed_request.save()

    def flush_failed_requests(self):
        for failed_request in self.pending_requests_model.objects.all():
            failed_request.delete()
