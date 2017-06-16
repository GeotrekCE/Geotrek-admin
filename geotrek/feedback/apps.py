from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.core.appconfig import GeotrekConfig


class FeedbackConfig(GeotrekConfig):
    name = 'geotrek.feedback'
    verbose_name = _("Feedback")
