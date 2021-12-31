from django.conf import settings
from django.forms.fields import CharField
from django.forms.widgets import HiddenInput, Textarea
from django.utils.translation import gettext as _

from geotrek.common.forms import CommonForm
from .models import Report

from .models import Report, ReportStatus, TimerEvent

# This dict stores constraints for status changes in management workflow
# {'current_status': ['allowed_next_status', 'other_allowed_status']}
# Empty status should not be changed from this form
SURICATE_MANAGEMENT_WORKFLOW = {
    'filed': ['classified', 'filed'],
    'classified': ['classified'],
    'waiting': ['waiting'],
    'programmed': ['programmed'],
    'resolution_late': ['resolution_late'],
    'intervention_late': ['intervention_late'],
    'intervention_solved': ['resolved', 'intervention_solved'],
    'resolved': ['resolved']
}


class ReportForm(CommonForm):
    geomfields = ["geom"]

    fieldslayout = [
        Div(
            "email",
            "comment",
            "activity",
            "category",
            "problem_magnitude",
            "related_trek",
            "status",
            "assigned_user",
            "uses_timers"
        )
    ]

    class Meta:
        fields = [
            "geom",
            "email",
            "comment",
            "activity",
            "category",
            "problem_magnitude",
            "related_trek",
            "status",
            "assigned_user",
            "uses_timers"
        ]
        model = Report

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["geom"].required = True
        if settings.SURICATE_MANAGEMENT_ENABLED:
            if self.instance.pk:
                # Store current status
                self.old_status_id = self.instance.status.suricate_id
                # Hide fields that are handled automatically in Management mode
                self.fields["geom"].widget = HiddenInput()
                self.fields["email"].widget = HiddenInput()
                self.fields["comment"].widget = HiddenInput()
                self.fields["activity"].widget = HiddenInput()
                self.fields["category"].widget = HiddenInput()
                self.fields["problem_magnitude"].widget = HiddenInput()
                # Add fields that are used in Management mode
                # status
                next_statuses = SURICATE_MANAGEMENT_WORKFLOW[self.instance.status.suricate_id]
                self.fields["status"].empty_label = None
                self.fields["status"].queryset = ReportStatus.objects.filter(suricate_id__in=next_statuses)
                # assigned_user
                if self.old_status_id != 'filed':
                    self.fields["assigned_user"].widget = HiddenInput()
                # message for sentinel
                self.fields["message_sentinel"] = CharField(required=False)
                self.fields["message_sentinel"].widget = Textarea()
                self.fields["message_sentinel"].label = _("Message for sentinel")
                right_after_status_index = self.fieldslayout[0].fields.index('status') + 1
                self.fieldslayout[0].insert(right_after_status_index, 'message_sentinel')
                # message for supervisor
                self.fields["message_supervisor"] = CharField(required=False)
                self.fields["message_supervisor"].widget = Textarea()
                self.fields["message_supervisor"].label = _("Message for supervisor")
                right_after_user_index = self.fieldslayout[0].fields.index('assigned_user') + 1
                self.fieldslayout[0].insert(right_after_user_index, 'message_supervisor')
            else:
                self.old_status_id = None
                self.fields["status"].widget = HiddenInput()
                self.fields["assigned_user"].widget = HiddenInput()
                self.fields["uses_timers"].widget = HiddenInput()
        else:
            self.fields["assigned_user"].widget = HiddenInput()
            self.fields["uses_timers"].widget = HiddenInput()

    def save(self, *args, **kwargs):
        report = super().save(self, *args, **kwargs)
        if self.instance.pk and settings.SURICATE_MANAGEMENT_ENABLED:
            if self.old_status_id == 'filed' and 'assigned_user' in self.changed_data:
                msg = self.cleaned_data.get('message_supervisor', "")
                report.notify_assigned_user(msg)
                waiting_status = ReportStatus.objects.get(suricate_id='waiting')
                report.status = waiting_status
                report.save()
                report.lock_in_suricate()
                TimerEvent.objects.create(step=waiting_status, report=report)
            if 'status' in self.changed_data or 'assigned_user' in self.changed_data:
                msg = self.cleaned_data.get('message_sentinel', "")
                report.send_notifications_on_status_change(self.old_status_id, msg)
            if 'status' in self.changed_data and self.old_status_id == 'intervention_solved':
                report.unlock_in_suricate()
        return report
