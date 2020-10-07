from zipfile import is_zipfile
from copy import deepcopy

from django import forms
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.core.exceptions import FieldDoesNotExist
from django.urls import reverse
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _

from mapentity.forms import MapEntityForm

from geotrek.authent.models import default_structure, StructureRelated, StructureOrNoneRelated

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
                self.fields.pop(name)
            for field in fieldslayout.fields:
                self.deep_remove(field, name)

    def replace_orig_fields(self):
        model = self._meta.model
        codeperm = '%s.publish_%s' % (
            model._meta.app_label, model._meta.model_name)
        if 'published' in self.fields and self.user and not self.user.has_perm(codeperm):
            self.deep_remove(self.fieldslayout, 'published')
        if 'review' in self.fields and self.instance and self.instance.any_published:
            self.deep_remove(self.fieldslayout, 'review')
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
        model = modelfield.remote_field.model
        # Filter structured choice fields according to user's structure
        if issubclass(model, StructureRelated) and model.check_structure_in_forms:
            field.queryset = field.queryset.filter(structure=self.user.profile.structure)
        if issubclass(model, StructureOrNoneRelated) and model.check_structure_in_forms:
            field.queryset = field.queryset.filter(Q(structure=self.user.profile.structure) | Q(structure=None))
        if issubclass(model, NoDeleteMixin):
            field.queryset = field.queryset.filter(deleted=False)

    def __init__(self, *args, **kwargs):
        self.fieldslayout = deepcopy(self.fieldslayout)
        super(CommonForm, self).__init__(*args, **kwargs)
        self.fields = self.fields.copy()
        self.update = kwargs.get("instance") is not None
        if 'structure' in self.fields:
            if self.user.has_perm('authent.can_bypass_structure'):
                if not self.instance.pk:
                    self.fields['structure'].initial = self.user.profile.structure
            else:
                for name, field in self.fields.items():
                    self.filter_related_field(name, field)
                del self.fields['structure']

    def clean(self):
        structure = self.cleaned_data.get('structure')
        if not structure:
            return self.cleaned_data

        # Copy cleaned_data because self.add_error may remove an item
        for name, field in self.cleaned_data.copy().items():
            try:
                modelfield = self.instance._meta.get_field(name)
            except FieldDoesNotExist:
                continue
            if not isinstance(modelfield, (ForeignKey, ManyToManyField)):
                continue
            model = modelfield.remote_field.model
            if not issubclass(model, (StructureRelated, StructureOrNoneRelated)):
                continue
            if not model.check_structure_in_forms:
                continue
            if isinstance(field, QuerySet):
                for value in field:
                    self.check_structure(value, structure, name)
            else:
                self.check_structure(field, structure, name)
        return self.cleaned_data

    def check_structure(self, obj, structure, name):
        if hasattr(obj, 'structure'):
            if obj.structure and structure != obj.structure:
                self.add_error(name, format_lazy(_("Please select a choice related to all structures (without brackets) "
                                                   "or related to the structure {struc} (in brackets)"), struc=structure))

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


class SyncRandoForm(forms.Form):
    """
    Sync Rando View Form
    """

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_id = 'form-sync'
        helper.form_action = reverse('common:sync_randos')
        helper.form_class = 'search'
        # submit button with boostrap attributes, disabled by default
        helper.add_input(Submit('sync-web', _("Launch Sync"),
                                **{'data-toggle': "modal",
                                   'data-target': "#confirm-submit",
                                   'disabled': 'disabled'}))

        return helper
