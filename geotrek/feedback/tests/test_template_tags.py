from datetime import datetime

from django.test import TestCase

from geotrek.authent.tests.factories import UserFactory, UserProfileFactory
from geotrek.feedback.templatetags.feedback_tags import (
    predefined_emails, resolved_intervention_info, status_ids_and_colors)
from geotrek.feedback.tests.factories import (PredefinedEmailFactory,
                                              ReportStatusFactory)
from geotrek.maintenance.tests.factories import ReportInterventionFactory


class TestFeedbackTemplateTags(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = UserFactory(username="CCCC")
        UserProfileFactory.create(user=cls.user1, extended_username="Communauté des Communes des Communautés Communataires")
        cls.user2 = UserFactory(username="Kurt")
        UserProfileFactory.create(user=cls.user2)
        solved_status = ReportStatusFactory(identifier='solved_intervention', color="#448654")
        cls.intervention_solved_1 = ReportInterventionFactory(date=datetime(year=1997, month=4, day=4).date())
        cls.report_1 = cls.intervention_solved_1.target
        cls.report_1.status = solved_status
        cls.report_1.assigned_user = cls.user1
        cls.report_1.save()
        cls.intervention_solved_2 = ReportInterventionFactory(date=datetime(year=1997, month=5, day=4).date())
        cls.report_2 = cls.intervention_solved_2.target
        cls.report_2.status = solved_status
        cls.report_2.assigned_user = cls.user2
        cls.report_2.save()
        cls.email1 = PredefinedEmailFactory()
        cls.email2 = PredefinedEmailFactory()

    def test_resolved_intervention_username(self):
        self.assertEqual(
            "{\"date\": \"04/04/1997\", \"username\": \"Communaut\\u00e9 des Communes des Communaut\\u00e9s Communataires\"}",
            resolved_intervention_info(self.report_1)
        )
        self.assertEqual(
            "{\"date\": \"04/05/1997\", \"username\": \"Kurt\"}",
            resolved_intervention_info(self.report_2)
        )

    def test_status_ids_and_colors(self):
        self.assertEqual(
            "{\"1\": {\"id\": \"solved_intervention\", \"color\": \"#448654\"}, \"2\": {\"id\": \"ID 1\", \"color\": \"#444444\"}, \"3\": {\"id\": \"ID 2\", \"color\": \"#444444\"}}",
            status_ids_and_colors()
        )

    def test_predefined_emails(self):
        self.assertEqual(
            "{\"1\": {\"label\": \"Predefined Email 0\", \"text\": \"Some email body content 0\"}, \"2\": {\"label\": \"Predefined Email 1\", \"text\": \"Some email body content 1\"}}",
            predefined_emails()
        )
