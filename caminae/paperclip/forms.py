# from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

import floppyforms as forms
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper

from .models import Attachment


class AttachmentForm(forms.ModelForm):
    attachment_file = forms.FileField(label=_('Upload attachment'))

    class Meta:
        model = Attachment
        exclude = ('creator', 'date_insert', 'date_update',
                   'content_type', 'object_id', 'content_object' )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(
                Submit('submit_attachment', _('Add attachment'),
                    css_class="btn-primary offset1")
        )
        super(AttachmentForm, self).__init__(*args, **kwargs)

    def save(self, request, obj, *args, **kwargs):
        self.instance.creator = request.user
        self.instance.content_type = ContentType.objects.get_for_model(obj)
        self.instance.object_id = obj.id
        super(AttachmentForm, self).save(*args, **kwargs)

