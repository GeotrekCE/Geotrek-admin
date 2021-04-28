import logging

from geotrek.feedback.models import ReportActivity, ReportStatus

from .helpers import SuricateRequestManager

logger = logging.getLogger(__name__)


class SuricateParser(SuricateRequestManager):
    def get_activities(self):
        """Get activities list from Suricate Rest API"""
        data = self.get_from_suricate("wsGetActivities")
        for activity in data["activites"]:
            obj, created = ReportActivity.objects.get_or_create(
                suricate_id=activity["id"], defaults={"label": activity["libelle"]}
            )
            if created:
                logger.info(
                    f"Created new activity - id: {activity['id']}, label: {activity['libelle']}"
                )

    def get_statuses(self):
        """Get statuses list from Suricate Rest API"""
        data = self.get_from_suricate("wsGetStatusList")
        for status in data["statuts"]:
            obj, created = ReportStatus.objects.get_or_create(
                id=status["id"], defaults={"label": status["libelle"]}
            )
            if created:
                logger.info(
                    f"Created new status - id: {status['id']}, label: {status['libelle']}"
                )

    def get_alerts(self):
        """Get reports list from Suricate Rest API"""
        return self.get_from_suricate("wsGetAlerts")
