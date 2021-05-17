import logging
from datetime import datetime

from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils.timezone import make_aware
from geotrek.feedback.models import (
    AttachedMessage,
    MessageAttachedDocument,
    Report,
    ReportActivity,
    ReportAttachedDocument,
    ReportCategory,
    ReportProblemMagnitude,
    ReportStatus,
)

from .helpers import SuricateRequestManager

logger = logging.getLogger(__name__)


class SuricateParser(SuricateRequestManager):
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
            obj, updated = ReportActivity.objects.update_or_create(
                suricate_id=activity["id"], defaults={"label": activity["libelle"]}
            )
            if updated:
                logger.info(
                    f"New or updated activity - id: {activity['id']}, label: {activity['libelle']}"
                )

    def get_statuses(self):
        """Get statuses list from Suricate Rest API"""

        data = self.get_from_suricate("wsGetStatusList")

        # Parse statuses and create
        for status in data["statuts"]:
            obj, updated = ReportStatus.objects.get_or_create(
                suricate_id=status["id"], defaults={"label": status["libelle"]}
            )
            if updated:
                logger.info(
                    f"New or updated status - id: {status['id']}, label: {status['libelle']}"
                )

    def get_alerts(self):
        """Get reports list from Suricate Rest API"""

        data = self.get_from_suricate("wsGetAlerts")
        # i = 0
        # Parse alerts
        for report in data["alertes"]:
            # print("Alert " + str(i))

            # Parse dates
            rep_updated = self.parse_date(report["updated"])
            rep_creation = self.parse_date(report["datedepot"])

            # Parse geom
            rep_gps = Point(report["gpslongitude"], report["gpslatitude"], srid=4326)
            rep_srid = rep_gps.transform(settings.SRID, clone=True)
            rep_point = Point(rep_srid.coords)

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
            if created:
                logger.info(f"Created new feedback category - label: {report['type']}")

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
                "created": rep_creation,
                "last_updated": rep_updated,
            }
            report_obj, updated = Report.objects.update_or_create(
                uid=report["uid"], defaults=fields
            )
            if updated:
                logger.info(
                    f"New or updated report - id: {report['uid']}, location: {report_obj.geom}"
                )

            # Parse documents attached to report
            self.create_documents(report["documents"], report_obj, "Report")

            # Parse messages attached to report
            self.create_messages(report["messages"], report_obj)
            # i += 1

    def create_documents(self, documents, parent, type_parent):
        """Parse documents list from Suricate Rest API"""

        for document in documents:
            # Parse fields
            fields = {"file_name": document["nomfichier"], "url": document["url"]}

            # Attach document to the right object
            if type_parent == "Report":
                # Attach document to a report and create
                fields["report"] = parent
                document_obj, updated = ReportAttachedDocument.objects.update_or_create(
                    suricate_id=document["id"], defaults=fields
                )
                if updated:
                    logger.info(
                        f"New or updated document - id: {document['id']}, parent: {parent.uid}"
                    )
            elif type_parent == "Message":
                # Attach document to a message and create
                fields["message"] = parent
                (
                    document_obj,
                    updated,
                ) = MessageAttachedDocument.objects.update_or_create(
                    suricate_id=document["id"], defaults=fields
                )
                if updated:
                    logger.info(
                        f"New or updated Message document - id: {document['id']}, parent: {parent.suricate_id}"
                    )

    def create_messages(self, messages, parent):
        """Parse messages list from Suricate Rest API"""

        for message in messages:
            # Parse date
            msg_creation = self.parse_date(message["date"])

            # Parse fields
            fields = {
                "date": msg_creation,
                "author": message["redacteur"],
                "content": message["texte"],
                "type": message["type"],
                "suricate_id": message["id"],
                "report": parent,
            }

            # Create message object
            message_obj, updated = AttachedMessage.objects.update_or_create(
                suricate_id=message["id"], defaults=fields
            )
            if updated:
                logger.info(
                    f"New or updated Message - id: {message['id']}, parent: {parent.uid}"
                )

            # Parse documents attached to message
            self.create_documents(message["documents"], message_obj, "Message")

    def initialize_internal_statuses(self):
        """Create extra statuses that Suricate does not have to know about"""
        ReportStatus.objects.create(suricate_id="to_transmit", label="A transmettre")
        ReportStatus.objects.create(
            suricate_id="intervention_late", label="Intervention en retard"
        )
        ReportStatus.objects.create(
            suricate_id="planned_late", label="Programmation en retard"
        )
        ReportStatus.objects.create(suricate_id="programmed", label="Programmé")
        ReportStatus.objects.create(
            suricate_id="intervention_over", label="Intervention terminée"
        )
