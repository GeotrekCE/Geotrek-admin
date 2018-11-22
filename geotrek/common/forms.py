# -*- coding: utf-8 -*-
from copy import deepcopy
from zipfile import is_zipfile

from django import forms
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.core.exceptions import FieldDoesNotExist
from django.utils.translation import ugettext_lazy as _

from mapentity.forms import MapEntityForm

from geotrek.authent.models import (default_structure, StructureRelated, StructureOrNoneRelated,
                                    StructureRelatedQuerySet)

from .mixins import NoDeleteMixin

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from crispy_forms.bootstrap import FormActions


class CommonForm(MapEntityForm):

    class Meta:
        fields = []

    def deep_remove(self, fieldslayout, name):
        if isinstance(fieldslayout, list):
            for field in fieldslayout:
                self.deep_remove(field, name)
        elif hasattr(fieldslayout, 'fields'):
            if name in fieldslayout.fields:
                fieldslayout.fields.remove(name)
            for field in fieldslayout.fields:
                self.deep_remove(field, name)

    def replace_orig_fields(self):
        model = self._meta.model
        codeperm = '%s.publish_%s' % (
            model._meta.app_label, model._meta.model_name)
        if 'published' in self.fields and self.user and not self.user.has_perm(codeperm):
            del self.fields['published']
        if 'review' in self.fields and self.instance and self.instance.any_published:
            del self.fields['review']
        super(CommonForm, self).replace_orig_fields()

    def filter_related_field(self, name, field):
        if not isinstance(field, forms.models.ModelChoiceField):
            return
        try:
            modelfield = self.instance._meta.get_field(name)
        except FieldDoesNotExist:
            # be careful but custom form fields, not in model
            modelfield = None
        if not isinstance(modelfield, (ForeignKey, ManyToManyField)):
            return
        model = modelfield.remote_field.to
        # Filter structured choice fields according to user's structure
        if issubclass(model, StructureRelated) or issubclass(model, StructureOrNoneRelated):
            field.queryset = StructureRelatedQuerySet.queryset_for_user(
                field.queryset, self.user)
        if issubclass(model, NoDeleteMixin):
            field.queryset = field.queryset.filter(deleted=False)

    def __init__(self, *args, **kwargs):
        super(CommonForm, self).__init__(*args, **kwargs)

        self.update = kwargs.get("instance") is not None

        for name, field in list(self.fields.items()):
            self.filter_related_field(name, field)

        # allow to modify layout per instance
        self.helper.fieldlayout = deepcopy(self.fieldslayout)
        model = self._meta.model
        codeperm = '%s.publish_%s' % (model._meta.app_label, model._meta.model_name)
        if 'published' in self.fields and self.user and not self.user.has_perm(codeperm):
            self.deep_remove(self.helper.fieldslayout, 'published')
        if 'review' in self.fields and self.instance and self.instance.any_published:
            self.deep_remove(self.helper.fieldslayout, 'review')

    def save(self, commit=True):
        """Set structure field before saving if need be"""
        if self.update:  # Structure is already set on object.
            pass
        elif not hasattr(self.instance, 'structure'):
            pass
        elif 'structure' in self.fields:
            pass  # The form contains the structure field. Let django use its value.
        elif self.user:
            self.instance.structure = self.user.profile.structure
        else:
            self.instance.structure = default_structure()
        return super(CommonForm, self).save(commit)


class ImportDatasetForm(forms.Form):
    parser = forms.TypedChoiceField(
        label=_('Data to import from network'),
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, choices=None, *args, **kwargs):
        super(ImportDatasetForm, self).__init__(*args, **kwargs)

        self.fields['parser'].choices = choices

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'parser',
                ),
                FormActions(
                    Submit('import-web', _("Import"), css_class='button white')
                ),
                css_class='file-attachment-form',
            )
        )


class ImportDatasetFormWithFile(ImportDatasetForm):
    zipfile = forms.FileField(
        label=_('File'),
        required=True,
        widget=forms.FileInput
    )
    encoding = forms.ChoiceField(
        label=_('Encoding'),
        choices=(('Windows-1252', 'Windows-1252'), ('UTF-8', 'UTF-8'))
    )

    def __init__(self, *args, **kwargs):
        super(ImportDatasetFormWithFile, self).__init__(*args, **kwargs)

        self.fields['parser'].label = _('Data to import from local file')
        self.helper.layout = Layout(
            Div(
                Div(
                    'parser',
                    'zipfile',
                    'encoding',
                ),
                FormActions(
                    Submit('upload-file', _("Import"), css_class='button white')
                ),
                css_class='file-attachment-form',
            )
        )

    def clean_zipfile(self):
        z = self.cleaned_data['zipfile']
        if not is_zipfile(z):
            raise forms.ValidationError(
                _("File must be of ZIP type."), code='invalid')
        # Reset position for further use.
        z.seek(0)
