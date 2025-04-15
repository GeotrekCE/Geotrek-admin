import logging
import os
import traceback
from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.contrib.gis.geos.collections import Polygon
from django.core.files.base import ContentFile
from django.utils.timezone import make_aware
from paperclip.models import attachment_upload

from geotrek.common.models import Attachment, FileType
from geotrek.feedback.models import (
    AttachedMessage,
    Report,
    ReportActivity,
    ReportCategory,
    ReportProblemMagnitude,
    ReportStatus,
    WorkflowManager,
)

from .helpers import SuricateGestionRequestManager

logger = logging.getLogger(__name__)


class SuricateParser(SuricateGestionRequestManager):
    def __init__(self):
        super().__init__()
        self.bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        self.filetype, created = FileType.objects.get_or_create(
            type="Photographie", structure=None
        )
        self.creator, created = get_user_model().objects.get_or_create(
            username="import", defaults={"is_active": False}
        )

    def parse_date(self, date):
        """Parse datetime string from Suricate Rest API"""
        date_no_timezone = datetime.strptime(date, "%B, %d %Y %H:%M:%S")
        date_timezone = make_aware(date_no_timezone)
        return date_timezone

    def get_activities(self):
        """Get activities list from Suricate Rest API"""

        data = self.get_suricate("wsGetActivities")

        # Parse activities and create
        for activity in data["activites"]:
            obj, created = ReportActivity.objects.update_or_create(
                identifier=activity["id"], defaults={"label": activity["libelle"]}
            )
            if created:
                logger.info(
                    "New activity - id: %s, label: %s",
                    activity["id"],
                    activity["libelle"],
                )

    def get_statuses(self):
        """Get statuses list from Suricate Rest API"""

        data = self.get_suricate("wsGetStatusList")

        # Parse statuses and create
        for status in data["statuts"]:
            obj, created = ReportStatus.objects.get_or_create(
                identifier=status["id"], defaults={"label": status["libelle"]}
            )
            if created:
                logger.info(
                    "New status - id: %s, label: %s", status["id"], status["libelle"]
                )

    def send_workflow_manager_new_reports_email(self, reports):
        for manager in WorkflowManager.objects.all():
            manager.notify_new_reports(reports)

    def parse_report(self, report):
        """
        Parse a JSON report from Suricate API
        :return: returns True if and only if this report is imported (it is in bbox) and is new
        """
        # Parse geom
        rep_gps = Point(report["gpslongitude"], report["gpslatitude"], srid=4326)
        rep_srid = rep_gps.transform(settings.SRID, clone=True)
        rep_point = Point(rep_srid.coords)

        # Parse status
        rep_status = ReportStatus.objects.get(identifier=report["statut"])

        # Keep or discard
        should_import = (
            rep_point.within(self.bbox) and rep_status.identifier != "created"
        )
        should_update_status = True
        if settings.SURICATE_WORKFLOW_ENABLED:
            should_import = (
                should_import and bool(report["locked"])
            )  # In Workflow mode, only import locked reports. In Management mode, import locked or unlocked reports.
            should_update_status = (
                rep_status.identifier != "waiting"
                or report["uid"] not in self.existing_uuids
            )  # Do not override internal statuses with Waiting status

        if should_import:
            # Parse dates
            rep_updated = self.parse_date(report["updated"])
            rep_creation = self.parse_date(report["datedepot"])

            # Parse magnitude
            rep_magnitude, created = ReportProblemMagnitude.objects.get_or_create(
                suricate_label=report["ampleur"]
            )
            if created:
                logger.info(
                    "Created new feedback magnitude - label: %s", report["ampleur"]
                )

            # Parse category
            rep_category, created = ReportCategory.objects.get_or_create(
                label=report["type"]
            )
            if created:
                logger.info("Created new feedback category - label: %s", report["type"])

            # Parse activity
            rep_activity = ReportActivity.objects.get(identifier=report["idactivite"])

            # Create report object
            fields = {
                "locked": bool(report["locked"]),
                "email": report["emaildeposant"],
                "comment": report["commentaire"],
                "geom": rep_point,
                "origin": report["origin"],
                "activity": rep_activity,
                "category": rep_category,
                "problem_magnitude": rep_magnitude,
                "created_in_suricate": rep_creation,
                "last_updated_in_suricate": rep_updated,
                "eid": str(report["shortkeylink"]),
                "provider": "Suricate",
            }

            if should_update_status:
                fields["status"] = rep_status

            report_obj, created = Report.objects.update_or_create(
                external_uuid=report["uid"], defaults=fields
            )

            if created:
                logger.info(
                    "New report - id: %s, location: %s", report["uid"], report_obj.geom
                )
            else:
                self.to_delete.discard(report_obj.pk)

            # Parse documents attached to report
            self.create_documents(report["documents"], report_obj)

            # Parse messages attached to report
            self.create_messages(report["messages"], report_obj)

            return report_obj.pk if created else 0

    def before_get_alerts(self, verbosity=1):
        pk_and_uuid = Report.objects.values_list("pk", "external_uuid")
        if pk_and_uuid:
            pks, uuids = zip(*pk_and_uuid)
            self.existing_uuids = list(
                map(lambda x: "".join(str(x).upper().rsplit("-", 1)), uuids)
            )  # Format UUIDs as they are found in Suricate
            self.to_delete = set(pks)
        else:
            self.existing_uuids = []
            self.to_delete = set()
        if verbosity >= 1:
            logger.info("Starting reports parsing from Suricate\n")

    def after_get_alerts(self, reports_created, should_notify):
        Report.objects.filter(pk__in=self.to_delete).delete()
        if reports_created and should_notify:
            self.send_workflow_manager_new_reports_email(reports_created)

    def get_alert(self, verbosity=1, pk=0):
        """
        Get reports list from Suricate Rest API
        :return: returns True if and only if reports was imported (it is in bbox)
        """
        data = self.get_suricate("wsGetAlerts")
        pk = int(pk)
        if pk:
            formatted_external_uuid = Report.objects.get(pk=pk).formatted_external_uuid
            report = next(
                report
                for report in data["alertes"]
                if report["uid"] == formatted_external_uuid
            )
        else:
            report = data["alertes"][0]
        if verbosity >= 2:
            logger.info("Processing report %s\n", report["uid"])
        self.before_get_alerts(verbosity)
        self.to_delete = set()
        report_created = self.parse_report(report)
        if verbosity >= 1:
            logger.info("Created : %s", report_created)

    def get_alerts(self, verbosity=1, should_notify=True):
        """
        Get reports list from Suricate Rest API
        :return: returns True if and only if reports was imported (it is in bbox)
        """
        self.before_get_alerts(verbosity)
        data = self.get_suricate("wsGetAlerts")
        total_reports = len(data["alertes"])
        current_report = 1
        reports_created = set()
        # Parse alerts
        for report in data["alertes"]:
            if verbosity == 2:
                logger.info(
                    "Processing report %s - %s/%s \n",
                    report["uid"],
                    current_report,
                    total_reports,
                )
            report_created = self.parse_report(report)
            if report_created:
                reports_created.add(report_created)
            current_report += 1
        if verbosity >= 1:
            logger.info("Parsed %s reports from Suricate\n", total_reports)
        if settings.SURICATE_WORKFLOW_SETTINGS.get("SKIP_MANAGER_MODERATION"):
            should_notify = False
        self.after_get_alerts(reports_created, should_notify)

    def create_documents(self, documents, parent):
        """Parse documents list from Suricate Rest API"""
        for document in documents:
            file_id = document["id"]
            file_url = document["url"]
            uid, ext = os.path.splitext(os.path.basename(file_url))
            uid = uid + str(file_id)
            parsed_url = urlparse(file_url)

            attachment, created = Attachment.objects.get_or_create(
                object_id=parent.pk,
                title=uid,
                content_type=ContentType.objects.get_for_model(parent),
                defaults={"filetype": self.filetype, "creator": self.creator},
            )
            attachment_final_name = attachment.prepare_file_suffix(basename=uid + ext)
            attachment_final_path = attachment_upload(attachment, attachment_final_name)
            # If attachment is either new or had a failed download last time => download file
            # If attachment isn't new and was downloaded before => skip this file

            if attachment.attachment_file.storage.exists(attachment_final_path):
                continue

            if parsed_url.scheme in ("http", "https"):
                response = self.get_attachment_from_suricate(file_url)
                try:
                    if response.status_code in [200, 201]:
                        f = ContentFile(response.content)
                        attachment.attachment_file.save(
                            attachment_final_name, f, save=False
                        )
                    attachment.save(**{"skip_file_save": True})
                except Exception as e:
                    logger.error(
                        "Could not download image : %s \n%s\n%s",
                        file_url,
                        e,
                        traceback.format_exc(),
                    )

    def create_messages(self, messages, parent):
        """Parse messages list from Suricate Rest API"""
        for message in messages:
            # Parse date
            msg_creation = self.parse_date(message["date"])

            # Parse fields
            fields = {
                "author": message["redacteur"],
                "content": message["texte"],
                "type": message["type"],
            }

            # Create message object
            message_obj, created = AttachedMessage.objects.update_or_create(
                identifier=message["id"],
                date=msg_creation,
                report=parent,
                defaults=fields,
            )
            if created:
                logger.info(
                    "New Message - id: %s, parent: %s",
                    message["id"],
                    parent.external_uuid,
                )

            # Parse documents attached to message
            self.create_documents(message["documents"], parent)
