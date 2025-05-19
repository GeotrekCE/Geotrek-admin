from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button
from django import forms
from django.urls import reverse
from django.utils.translation import gettext as _


class SyncMobileForm(forms.Form):
    """
    Sync Mobile View Form
    """

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_id = "form-sync"
        helper.form_action = reverse("apimobile:sync_mobiles")
        helper.form_class = "search"
        # submit button with boostrap attributes, disabled by default
        helper.add_input(
            Button(
                "sync-web",
                _("Launch Sync Mobile"),
                css_class="btn-primary",
                **{
                    "data-toggle": "modal",
                    "data-target": "#confirm-submit",
                    "disabled": "disabled",
                },
            )
        )

        return helper
