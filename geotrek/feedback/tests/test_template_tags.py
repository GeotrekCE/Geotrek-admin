import json
from datetime import datetime

from django.test import TestCase
from django.utils.encoding import force_str
from mapentity.models import ADDITION, LogEntry

from geotrek.authent.tests.factories import UserFactory, UserProfileFactory
from geotrek.feedback.templatetags.feedback_tags import (
    predefined_emails, resolved_intervention_info, status_ids_and_colors, workflow_manager)
from geotrek.feedback.tests.factories import (PredefinedEmailFactory,
                                              ReportStatusFactory, WorkflowManagerFactory)
from geotrek.maintenance.tests.factories import ReportInterventionFactory


class TestFeedbackTemplateTags(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = UserFactory(username="CCCC")
        UserProfileFactory.create(user=cls.user1, extended_username="Communauté des Communes des Communautés Communataires")
        cls.user2 = UserFactory(username="Kurt")
        UserProfileFactory.create(user=cls.user2)
        cls.solved_status = ReportStatusFactory(identifier='solved_intervention', color="#448654")
        cls.intervention_solved_1 = ReportInterventionFactory(date=datetime(year=1997, month=4, day=4).date())
        # Simulate user created intervention
        LogEntry.objects.log_action(
            user_id=cls.user1.pk,
            content_type_id=cls.intervention_solved_1.get_content_type_id(),
            object_id=cls.intervention_solved_1.pk,
            object_repr=force_str(cls.intervention_solved_1),
            action_flag=ADDITION
        )
        # Intervention is linked to a solved report
        cls.report_1 = cls.intervention_solved_1.target
        cls.status_1 = cls.report_1.status
        cls.report_1.status = cls.solved_status
        cls.report_1.save()
        cls.intervention_solved_2 = ReportInterventionFactory(date=datetime(year=1997, month=5, day=4).date())
        # Simulate user created intervention
        LogEntry.objects.log_action(
            user_id=cls.user2.pk,
            content_type_id=cls.intervention_solved_2.get_content_type_id(),
            object_id=cls.intervention_solved_2.pk,
            object_repr=force_str(cls.intervention_solved_2),
            action_flag=ADDITION
        )
        # Intervention is linked to a solved report
        cls.report_2 = cls.intervention_solved_2.target
        cls.status_2 = cls.report_2.status
        cls.report_2.status = cls.solved_status
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
        expected = json.loads(f"{{\"{self.solved_status.pk}\": {{\"label\": \"{self.solved_status.label}\", \"id\": \"solved_intervention\", \"color\": \"#448654\", \"display_in_legend\": true}}, \"{self.status_1.pk}\": {{\"label\": \"{self.status_1.label}\", \"id\": \"{self.status_1.identifier}\", \"color\": \"#444444\", \"display_in_legend\": true}}, \"{self.status_2.pk}\": {{\"label\": \"{self.status_2.label}\", \"id\": \"{self.status_2.identifier}\", \"color\": \"#444444\", \"display_in_legend\": true}}}}")
        actual = json.loads(status_ids_and_colors())
        self.assertEqual(
            sorted(expected.items()),
            sorted(actual.items())
        )

    def test_predefined_emails(self):
        expected = json.loads(f"{{\"{self.email1.pk}\": {{\"label\": \"{self.email1.label}\", \"text\": \"{self.email1.text}\"}}, \"{self.email2.pk}\": {{\"label\": \"{self.email2.label}\", \"text\": \"{self.email2.text}\"}}}}")
        actual = json.loads(predefined_emails())
        self.assertEqual(
            sorted(expected.items()),
            sorted(actual.items())
        )

    def test_workflow_manager(self):
        self.assertEqual(workflow_manager(), None)
        wm = WorkflowManagerFactory(user=self.user1)
        self.assertEqual(workflow_manager(), wm.user.pk)
