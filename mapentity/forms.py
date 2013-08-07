import copy

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django import forms as django_forms

import floppyforms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Button, HTML
from crispy_forms.bootstrap import FormActions
from tinymce.widgets import TinyMCE
from modeltranslation.translator import translator, NotRegistered


class TranslatedModelForm(forms.ModelForm):
    """
    Auto-expand translatable fields.
    Expand means replace native (e.g. `name`) by translated (e.g. `name_fr`, `name_en`)
    """

    def __init__(self, *args, **kwargs):
        super(TranslatedModelForm, self).__init__(*args, **kwargs)
        # Track translated fields
        self._translated = {}
        self.replace_orig_fields()
        self.populate_fields()

    def replace_orig_fields(self):
        # Expand i18n fields
        try:
            # Obtain model translation options
            mto = translator.get_options_for_model(self._meta.model)
        except NotRegistered:
            # No translation field on this model, nothing to do
            return
        # For each translated model field
        for modelfield in mto.fields:
            # Remove form native field (e.g. `name`)
            native = self.fields.pop(modelfield)
            # Add translated fields (e.g. `name_fr`, `name_en`...)
            for l in settings.LANGUAGES:
                lang = l[0]
                name = '%s_%s' % (modelfield, lang)
                # Add to form.fields{}
                translated = copy.deepcopy(native)
                translated.required = native.required and (lang == settings.LANGUAGE_CODE)
                translated.label = u"%s [%s]" % (unicode(translated.label), lang)
                self.fields[name] = translated
                # Keep track of replacements
                self._translated.setdefault(modelfield, []).append(name)

    def save(self, *args, **kwargs):
        """ Manually saves translated fields on instance.
        """
        # Save translated fields
        for fields in self._translated.values():
            for field in fields:
                value = self.cleaned_data.get(field)
                if value:
                    setattr(self.instance, field, value)
        return super(TranslatedModelForm, self).save(*args, **kwargs)

    def populate_fields(self):
        """ Manually loads translated fields from instance.
        """
        if self.instance:
            for fields in self._translated.values():
                for field in fields:
                    self.fields[field].initial = getattr(self.instance, field)


class MapEntityForm(TranslatedModelForm):

    pk = forms.Field(required=False, widget=forms.Field.hidden_widget)
    model = forms.Field(required=False, widget=forms.Field.hidden_widget)

    helper = FormHelper()
    fieldslayout = None
    geomfields = []

    class Meta:
        fields = ['pk', 'model']

    # TODO: this is obvisouly wrong MapEntity should not depend on core
    # TODO: Django inserts Media in <head> https://code.djangoproject.com/ticket/13978
    MEDIA_JS = ("core/formfield.js",)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(MapEntityForm, self).__init__(*args, **kwargs)

        actions = [
            Submit('save_changes', _('Save changes'), css_class="btn-primary pull-right offset1"),
            Button('cancel', _('Cancel'), css_class="pull-right offset1"),
        ]

        # Generic behaviour
        if self.instance.pk:
            self.helper.form_action = self.instance.get_update_url()
            # Put delete url in Delete button
            actions.insert(0, HTML('<a class="btn btn-danger delete" href="%s"><i class="icon-white icon-trash"></i> %s</a>' % (
                self.instance.get_delete_url(),
                unicode(_("Delete")))))
        else:
            self.helper.form_action = self.instance.get_add_url()

        self.fields['pk'].initial = self.instance.pk
        self.fields['model'].initial = self.instance._meta.module_name

        # Check if fieldslayout is defined, otherwise use Meta.fields
        fieldslayout = self.fieldslayout
        if not fieldslayout:
            # Remove geomfields from left part
            fieldslayout = [fl for fl in self._meta.fields if fl not in self.geomfields]
        # Replace native fields in Crispy layout by translated fields
        fieldslayout = self.__replace_translatable_fields(fieldslayout)

        has_geomfield = len(self.geomfields) > 0
        leftpanel = Div(
            *fieldslayout,
            css_class="scrollable span" + ('4' if has_geomfield else '12'),
            css_id="modelfields"
        )

        rightpanel = tuple()
        if has_geomfield:
            rightpanel = (Div(
                *self.geomfields,
                css_class="span8",
                css_id="geomfield"
            ),)

        # Main form layout
        self.helper.help_text_inline = True
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Div(
                Div(
                    leftpanel,
                    *rightpanel,
                    css_class="row-fluid"
                ),
                css_class="container-fluid"
            ),
            FormActions(*actions, css_class="form-actions"),
        )

        # formfield_callback sucks and does not work with inherited fields
        for formfield in self.fields.values():
            if formfield and formfield.widget.__class__ in (forms.widgets.Textarea,
                                                            django_forms.widgets.Textarea):
                formfield.widget = TinyMCE()

    def __replace_translatable_fields(self, fieldslayout):
        newlayout = []
        for field in fieldslayout:
            # Layout fields can be nested (e.g. Div('f1', 'f2', Div('f3')))
            if hasattr(field, 'fields'):
                field.fields = self.__replace_translatable_fields(field.fields)
                newlayout.append(field)
            else:
                if field in self._translated:
                    newlayout.append(self.__tabbed_layout_for_field(field))
                else:
                    newlayout.append(field)
        return newlayout

    def __tabbed_layout_for_field(self, field):
        fields = []
        for replacement in self._translated[field]:
            active = "active" if replacement.endswith('_%s' % settings.LANGUAGE_CODE) else ""
            fields.append(Div(replacement,
                              css_class="tab-pane " + active,
                              css_id=replacement))

        layout = Div(
            HTML("""
            <ul class="nav nav-pills">
            {% for lang in LANGUAGES %}
                <li {% if lang.0 == LANGUAGE_CODE %}class="active"{% endif %}><a href="#%s_{{ lang.0 }}" data-toggle="tab">{{ lang.0 }}</a></li>
            {% endfor %}
            </ul>
            """.replace("%s", field)),
            Div(
                *fields,
                css_class="tab-content"
            ),
            css_class="tabbable"
        )
        return layout
