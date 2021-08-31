import logging
import os
import sys
from datetime import datetime
from time import sleep
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.contrib.gis.geos.collections import Polygon
from django.core.files.base import ContentFile
from django.utils.timezone import make_aware
from django.utils.translation import gettext as _

from geotrek.common.models import Attachment, FileType
from geotrek.common.parsers import (AttachmentParserMixin, DownloadImportError,
                                    GlobalImportError, ValueImportError)
from geotrek.feedback.models import (AttachedMessage, Report, ReportActivity,
                                     ReportCategory, ReportProblemMagnitude,
                                     ReportStatus)

from .helpers import SuricateGestionRequestManager, send_reports_to_managers

logger = logging.getLogger(__name__)


class SuricateParser(AttachmentParserMixin, SuricateGestionRequestManager):

    def __init__(self):
        super().__init__()
        self.bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        # Replicated Attachment parser start
        if settings.PAPERCLIP_ENABLE_LINK is False:
            raise Exception('You need to enable PAPERCLIP_ENABLE_LINK to use this function')
        try:
            self.filetype = FileType.objects.get_or_create(type="Photographie", structure=None)
        except FileType.DoesNotExist:
            raise GlobalImportError("FileType Photographie does not exists in "
                                    "Geotrek-Admin. Please add it")
        self.creator, created = get_user_model().objects.get_or_create(username='import', defaults={'is_active': False})

    def parse_date(self, date):
        """Parse datetime string from Suricate Rest API"""
        date_no_timezone = datetime.strptime(date, "%B, %d %Y %H:%M:%S")
        date_timezone = make_aware(date_no_timezone)
        return date_timezone

    def get_activities(self):
        """Get activities list from Suricate Rest API"""

        data = self.get_from_suricate("wsGetActivities")

        # Parse activities and create
        for activity in data["activites"]:
            obj, created = ReportActivity.objects.update_or_create(
                suricate_id=activity["id"], defaults={"label": activity["libelle"]}
            )
            if created:
                logger.info(
                    f"New activity - id: {activity['id']}, label: {activity['libelle']}"
                )

    def get_statuses(self):
        """Get statuses list from Suricate Rest API"""

        data = self.get_from_suricate("wsGetStatusList")

        # Parse statuses and create
        for status in data["statuts"]:
            obj, created = ReportStatus.objects.get_or_create(
                suricate_id=status["id"], defaults={"label": status["libelle"]}
            )
            if created:
                logger.info(
                    f"New status - id: {status['id']}, label: {status['libelle']}"
                )

    def send_managers_new_reports(self):
        try:
            send_reports_to_managers()
        except Exception as e:
            logger.error("Email could not be sent to managers.")
            logger.exception(e)  # This sends an email to admins :)

    def parse_report(self, report):
        """
        Parse a JSON report from Suricate API
        :return: returns True if and only if this report is imported (it is in bbox) and is new
        """
        # Parse geom
        rep_gps = Point(report["gpslongitude"], report["gpslatitude"], srid=4326)
        rep_srid = rep_gps.transform(settings.SRID, clone=True)
        rep_point = Point(rep_srid.coords)
        should_import = rep_point.within(self.bbox)

        if should_import:
            # Parse dates
            rep_updated = self.parse_date(report["updated"])
            rep_creation = self.parse_date(report["datedepot"])

            # Parse magnitude
            rep_magnitude, created = ReportProblemMagnitude.objects.get_or_create(
                label=report["ampleur"]
            )
            if created:
                logger.info(
                    f"Created new feedback magnitude - label: {report['ampleur']}"
                )

            # Parse category
            rep_category, created = ReportCategory.objects.get_or_create(
                label=report["type"]
            )
            if created:
                logger.info(f"Created new feedback category - label: {report['type']}")
            # Parse status
            rep_status = ReportStatus.objects.get(suricate_id=report["statut"])
            # Parse activity
            rep_activity = ReportActivity.objects.get(suricate_id=report["idactivite"])

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
                "status": rep_status,
                "created_in_suricate": rep_creation,
                "last_updated_in_suricate": rep_updated,
            }
            # TODO When implementing workflow :
            # if report.locked then suricate_status != geotrek_status
            # suricate_status must not override geotrek_status until we solve and unlock (see slides)
            report_obj, created = Report.objects.update_or_create(
                uid=report["uid"], defaults=fields
            )
            if created:
                logger.info(
                    f"New report - id: {report['uid']}, location: {report_obj.geom}"
                )

            # Parse documents attached to report
            self.create_documents(report["documents"], report_obj)

            # Parse messages attached to report
            self.create_messages(report["messages"], report_obj)

            return created

    def get_alerts(self, verbosity=1):
        """
        Get reports list from Suricate Rest API
        :return: returns True if and only if reports was imported (it is in bbox)
        """
        if verbosity >= 1:
            sys.stdout.write("Starting reports parsing from Suricate\n")
        data = self.get_from_suricate("wsGetAlerts")
        total_reports = len(data["alertes"])
        current_report = 1
        reports_created = False
        # Parse alerts
        for report in data["alertes"]:
            if verbosity == 2:
                sys.stdout.write(f"Processing report {report['uid']} - {current_report}/{total_reports} \n")
            report_created = self.parse_report(report)
            reports_created = reports_created or report_created
            current_report += 1
        if verbosity >= 1:
            sys.stdout.write(f"Parsed {total_reports} reports from Suricate\n")
        if reports_created:
            self.send_managers_new_reports()

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
                defaults={
                    'filetype': self.filetype,
                    'creator': self.creator
                }
            )

            if not created:
                # Don't download if it isn't new
                continue

            if parsed_url.scheme in ('http', 'https'):
                response = self.get_attachment_from_suricate(file_url)
                if response.status_code in [200, 201]:
                    f = ContentFile(response.content)
                    attachment.attachment_file.save(file_url, f, save=False)
            else:
                attachment.attachment_link = file_url
            attachment.save()

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
                suricate_id=message["id"], date=msg_creation, report=parent, defaults=fields
            )
            if created:
                logger.info(
                    f"New Message - id: {message['id']}, parent: {parent.uid}"
                )

            # Parse documents attached to message
            # self.create_documents(message["documents"], message_obj, "AttachedMessage")
