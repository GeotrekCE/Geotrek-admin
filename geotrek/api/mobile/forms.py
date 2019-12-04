from django.utils.translation import ugettext as _
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django.core.urlresolvers import reverse


class SyncMobileForm(forms.Form):
    """
    Sync Mobile View Form
    """

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_id = 'form-sync'
        helper.form_action = reverse('apimobile:sync_mobiles')
        helper.form_class = 'search'
        # submit button with boostrap attributes, disabled by default
        helper.add_input(Submit('sync-web', _("Launch Sync Mobile"),
                                **{'data-toggle': "modal",
                                   'data-target': "#confirm-submit",
                                   'disabled': 'disabled'}))

        return helper
