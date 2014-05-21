from django.template.loader import render_to_string
from django.core.mail import mail_managers
from django.utils.translation import ugettext_lazy as _


def send_report_managers(report, template_name='feedback/report_email.html'):
    subject = _(u'Feedback from {name} ({email})').format(name=report.name,
                                                          email=report.email)
    message = render_to_string(template_name, {'report': report})
    mail_managers(subject, message, fail_silently=False)
