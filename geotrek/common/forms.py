import logging
from copy import deepcopy

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Div, Layout, Submit
from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.checks.messages import Error
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.core.files.images import get_image_dimensions
from django.db.models import Q
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models.query import QuerySet
from django.forms.widgets import HiddenInput
from django.urls import reverse
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from mapentity.forms import MapEntityForm, SubmitButton
from modeltranslation.utils import build_localized_fieldname

from geotrek.authent.models import (StructureOrNoneRelated, StructureRelated,
                                    default_structure)
from geotrek.common.mixins.models import PublishableMixin
from geotrek.common.models import AccessibilityAttachment, AnnotationCategory, HDViewPoint
from geotrek.common.utils.translation import get_translated_fields

from .mixins.models import NoDeleteMixin

logger = logging.getLogger(__name__)


class CommonForm(MapEntityForm):

    not_hideable_fields = []

    class Meta:
        fields = []

    MAP_SETTINGS = {
        'PathForm': 'path',
        'TrekForm': 'trek',
        'TrailForm': 'trail',
        'LandEdgeForm': 'landedge',
        'PhysicalEdgeForm': 'physicaledge',
        'CompetenceEdgeForm': 'competenceedge',
        'WorkManagementEdgeForm': 'workmanagement',
        'SignageManagementEdgeForm': 'signagemanagementedge',
        'InfrastructureForm': 'infrastructure',
        'InterventionForm': 'intervention',
        'SignageForm': 'signage',
        'ProjectForm': 'project',
        'SiteForm': 'site',
        'CourseForm': 'course',
        'TouristicContentForm': 'touristic_content',
        'TouristicEventForm': 'touristic_event',
        'POIForm': 'poi',
        'ServiceForm': 'service',
        'DiveForm': 'dive',
        'SensitiveAreaForm': 'sensitivity_species',
        'RegulatorySensitiveAreaForm': 'sensitivity_regulatory',
        'BladeForm': 'blade',
        'ReportForm': 'report',
    }

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
        super().replace_orig_fields()

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

        # Get settings key for this Form
        settings_key = self.MAP_SETTINGS.get(self.__class__.__name__, None)
        if settings_key is None:
            logger.warning("No value set in MAP_SETTINGS dictonary for form class " + self.__class__.__name__)
        self.hidden_fields = settings.HIDDEN_FORM_FIELDS.get(settings_key, [])

        self.fieldslayout = deepcopy(self.fieldslayout)
        super().__init__(*args, **kwargs)
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

        # For each field listed in 'to hide' list for this Form
        for field_to_hide in self.hidden_fields:
            # Ignore if field was translated (handled in TranslatedModelForm)
            if field_to_hide not in self._translated:
                # Hide only if optional
                if self.fields[field_to_hide].required:
                    logger.warning(
                        f"Ignoring entry in HIDDEN_FORM_FIELDS: field '{field_to_hide}' is required on form {self.__class__.__name__}."
                    )
                elif field_to_hide in self.not_hideable_fields:
                    logger.warning(
                        f"Ignoring entry in HIDDEN_FORM_FIELDS: field '{field_to_hide}' cannot be hidden on form {self.__class__.__name__}."
                    )
                else:
                    self.fields[field_to_hide].widget = HiddenInput()

    def clean(self):
        """Check field data with structure and completeness fields if relevant"""
        structure = self.cleaned_data.get('structure')

        # if structure in form, check each field same structure
        if structure:
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

        # If model is publishable or reviewable,
        # check if completeness fields are required, and raise error if some fields are missing
        if self.completeness_fields_are_required():
            missing_fields = []
            completeness_fields = settings.COMPLETENESS_FIELDS.get(self._meta.model._meta.model_name, [])
            if settings.COMPLETENESS_LEVEL == 'error_on_publication':
                missing_fields = self._get_missing_completeness_fields(completeness_fields,
                                                                       _('This field is required to publish object.'))
            elif settings.COMPLETENESS_LEVEL == 'error_on_review':
                missing_fields = self._get_missing_completeness_fields(completeness_fields,
                                                                       _('This field is required to review object.'))

            if missing_fields:
                raise ValidationError(
                    _('Fields are missing to publish or review object: %(fields)s'),
                    params={
                        'fields': ', '.join(missing_fields)
                    },
                )

        return self.cleaned_data

    def check_structure(self, obj, structure, name):
        if hasattr(obj, 'structure'):
            if obj.structure and structure != obj.structure:
                self.add_error(name, format_lazy(_("Please select a choice related to all structures (without brackets) "
                                                   "or related to the structure {struc} (in brackets)"), struc=structure))

    @property
    def any_published(self):
        """Check if form has published in at least one of the language"""
        return any([self.cleaned_data.get(build_localized_fieldname('published', language[0]), False)
                    for language in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']])

    @property
    def published_languages(self):
        """Returns languages in which the form has published data.
        """
        languages = [language[0] for language in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']]
        if settings.PUBLISHED_BY_LANG:
            return [language for language in languages if self.cleaned_data.get(build_localized_fieldname('published', language), None)]
        else:
            if self.any_published:
                return languages

    def completeness_fields_are_required(self):
        """Return True if the completeness fields are required"""
        if not issubclass(self._meta.model, PublishableMixin):
            return False

        if not self.instance.is_complete():
            if settings.COMPLETENESS_LEVEL == 'error_on_publication':
                if self.any_published:
                    return True
            elif settings.COMPLETENESS_LEVEL == 'error_on_review':
                # Error on review implies error on publication
                if self.cleaned_data['review'] or self.any_published:
                    return True

        return False

    def _get_missing_completeness_fields(self, completeness_fields, msg):
        """Check fields completeness and add error message if field is empty"""

        missing_fields = []
        translated_fields = get_translated_fields(self._meta.model)

        # Add error on each field if it is empty
        for field_required in completeness_fields:
            if field_required in translated_fields:
                if self.cleaned_data.get('review') and settings.COMPLETENESS_LEVEL == 'error_on_review':
                    # get field for first language only
                    field_required_lang = build_localized_fieldname(field_required, settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES'][0][0])
                    missing_fields.append(field_required_lang)
                    self.add_error(field_required_lang, msg)
                else:
                    for language in self.published_languages:
                        field_required_lang = build_localized_fieldname(field_required, language)
                        if not self.cleaned_data.get(field_required_lang):
                            missing_fields.append(field_required_lang)
                            self.add_error(field_required_lang, msg)
            else:
                if not self.cleaned_data.get(field_required):
                    missing_fields.append(field_required)
                    self.add_error(field_required, msg)
        return missing_fields

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
        return super().save(commit)

    @classmethod
    def check_fields_to_hide(cls):
        errors = []
        for field_to_hide in settings.HIDDEN_FORM_FIELDS.get(cls.MAP_SETTINGS[cls.__name__], []):
            if field_to_hide not in cls._meta.fields:
                errors.append(
                    Error(
                        f"Cannot hide field '{field_to_hide}'",
                        hint="Field not included in form",
                        # Diplay dotted path only
                        obj=str(cls).split(" ")[1].strip(">").strip("'"),
                    )
                )
        return errors


class ImportDatasetForm(forms.Form):
    parser = forms.TypedChoiceField(
        label=_('Data to import from network'),
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, choices=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


class ImportSuricateForm(forms.Form):
    parser = forms.TypedChoiceField(
        label=_('Data to import from Suricate'),
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, choices=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['parser'].choices = choices

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'parser',
                ),
                FormActions(
                    Submit('import-suricate', _("Import"), css_class='button white')
                ),
                css_class='file-attachment-form',
            )
        )


class ImportDatasetFormWithFile(ImportDatasetForm):
    file = forms.FileField(
        label=_('File'),
        required=True,
        widget=forms.FileInput
    )
    encoding = forms.ChoiceField(
        label=_('Encoding'),
        choices=(('Windows-1252', 'Windows-1252'), ('UTF-8', 'UTF-8'))
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['parser'].label = _('Data to import from local file')
        self.helper.layout = Layout(
            Div(
                Div(
                    'parser',
                    'file',
                    'encoding',
                ),
                FormActions(
                    Submit('upload-file', _("Import"), css_class='button white')
                ),
                css_class='file-attachment-form',
            )
        )


class AttachmentAccessibilityForm(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, request, *args, **kwargs):
        self._object = kwargs.pop('object', None)

        super().__init__(*args, **kwargs)
        self.fields['legend'].widget.attrs['placeholder'] = _('Overview of the tricky passage')

        self.redirect_on_error = True
        # Detect fields errors without uploading (using HTML5)
        self.fields['author'].widget.attrs['pattern'] = r'^\S.*'
        self.fields['legend'].widget.attrs['pattern'] = r'^\S.*'
        self.fields['attachment_accessibility_file'].required = True
        self.fields['attachment_accessibility_file'].widget = forms.FileInput()

        self.helper = FormHelper(form=self)
        self.helper.form_tag = True
        self.helper.form_class = 'attachments-accessibility form-horizontal'
        self.helper.help_text_inline = True
        self.helper.form_style = "default"
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.fields['next'].initial = f"{self._object.get_detail_url()}?tab=attachments-accessibility"

        if not self.instance.pk:
            form_actions = [
                Submit('submit_attachment',
                       _('Submit attachment'),
                       css_class="btn-primary")
            ]
            self.form_url = reverse('common:add_attachment_accessibility', kwargs={
                'app_label': self._object._meta.app_label,
                'model_name': self._object._meta.model_name,
                'pk': self._object.pk
            })
        else:
            form_actions = [
                Button('cancel', _('Cancel'), css_class=""),
                Submit('submit_attachment',
                       _('Update attachment'),
                       css_class="btn-primary")
            ]
            self.fields['title'].widget.attrs['readonly'] = True
            self.form_url = reverse('common:update_attachment_accessibility', kwargs={
                'attachment_pk': self.instance.pk
            })

        self.helper.form_action = self.form_url
        self.helper.layout.fields.append(
            FormActions(*form_actions, css_class="form-actions"))

    class Meta:
        model = AccessibilityAttachment
        fields = ('attachment_accessibility_file', 'info_accessibility', 'author', 'title', 'legend')

    def success_url(self):
        obj = self._object
        return f"{obj.get_detail_url()}?tab=attachments-accessibility"

    def clean_attachment_accessibility_file(self):
        uploaded_image = self.cleaned_data.get("attachment_accessibility_file", False)
        if self.instance.pk:
            try:
                uploaded_image.file.readline()
            except FileNotFoundError:
                return uploaded_image
        if settings.PAPERCLIP_MAX_BYTES_SIZE_IMAGE and settings.PAPERCLIP_MAX_BYTES_SIZE_IMAGE < uploaded_image.size:
            raise forms.ValidationError(_('The uploaded file is too large'))
        width, height = get_image_dimensions(uploaded_image)
        if settings.PAPERCLIP_MIN_IMAGE_UPLOAD_WIDTH and settings.PAPERCLIP_MIN_IMAGE_UPLOAD_WIDTH > width:
            raise forms.ValidationError(_('The uploaded file is not wide enough'))
        if settings.PAPERCLIP_MIN_IMAGE_UPLOAD_HEIGHT and settings.PAPERCLIP_MIN_IMAGE_UPLOAD_HEIGHT > height:
            raise forms.ValidationError(_('The uploaded file is not tall enough'))
        return uploaded_image

    def save(self, request, *args, **kwargs):
        obj = self._object
        self.instance.creator = request.user
        self.instance.content_object = obj
        if "attachment_accessibility_file" in self.changed_data:
            # New file : regenerate new random name for this attachment
            instance = super().save(commit=False)
            instance.save(**{'force_refresh_suffix': True})
            return instance
        return super().save(*args, **kwargs)


class HDViewPointForm(MapEntityForm):
    geomfields = ['geom']

    def __init__(self, *args, content_type=None, object_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if content_type and object_id:
            self.instance.content_type_id = content_type
            self.instance.object_id = object_id
            self.helper.form_action += f"?object_id={object_id}&content_type={content_type}"

    class Meta:
        model = HDViewPoint
        fields = ('picture', 'geom', 'author', 'title', 'license', 'legend')


class HDViewPointAnnotationForm(forms.ModelForm):
    annotations = forms.JSONField(label=False)
    annotations_categories = forms.JSONField(label=False)
    annotation_category = forms.ModelChoiceField(
        required=False,
        queryset=AnnotationCategory.objects.all()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['annotations'].required = False
        self.fields['annotations'].widget = forms.Textarea(
            attrs={
                'name': 'annotations',
                'rows': '15',
                'type': 'textarea',
                'autocomplete': 'off',
                'autocorrect': 'off',
                'autocapitalize': 'off',
                'spellcheck': 'false',
                # Do not show GEOJson textarea to users
                'style': 'display: none;'
            }
        )
        self.fields['annotations_categories'].required = False
        self.fields['annotations_categories'].widget = forms.Textarea(
            attrs={
                'name': 'annotations_categories',
                'rows': '15',
                'type': 'textarea',
                'autocomplete': 'off',
                'autocorrect': 'off',
                'autocapitalize': 'off',
                'spellcheck': 'false',
                # Do not show GEOJson textarea to users
                'style': 'display: none;'
            }
        )
        self._init_layout()

    def _init_layout(self):
        """ Setup form buttons, submit URL, layout """

        actions = [
            Button('cancel', _('Cancel'), css_class="btn btn-light ml-auto mr-2"),
            SubmitButton('save_changes', _('Save changes')),
        ]

        leftpanel = Div(
            'annotations',
            'annotations_categories',
            'annotation_category',
            css_id="modelfields",
        )
        formactions = FormActions(
            *actions,
            css_class="form-actions",
            template='mapentity/crispy_bootstrap4/bootstrap4/layout/formactions.html'
        )

        # # Main form layout
        self.helper.help_text_inline = True
        self.helper.form_class = 'form-horizontal'
        self.helper.form_style = "default"
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'controls col-md-9'
        self.helper.layout = Layout(
            Div(
                Div(
                    leftpanel,
                    css_class="row"
                ),
                css_class="container-fluid"
            ),
            formactions,
        )

    def clean_annotations_categories(self):
        data = self.cleaned_data["annotations_categories"]
        if data is None:
            return {}
        return data

    def clean_annotations(self):
        data = self.cleaned_data["annotations"]
        if data is None:
            return {}
        return data

    class Meta:
        model = HDViewPoint
        fields = ('annotations', 'annotations_categories')
