from geotrek.feedback.models import ReportStatus
from .helpers import SuricateRequestManager
import logging

logger = logging.getLogger(__name__)


class SuricateParser(SuricateRequestManager):
    def get_activities(self):
        """Get activities list from Suricate Rest API"""
        return self.get_from_suricate("wsGetActivities")

    def get_statuses(self):
        """Get statuses list from Suricate Rest API"""
        data = self.get_from_suricate("wsGetStatusList")
        for status in data['statuts']:
            print(status)
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
