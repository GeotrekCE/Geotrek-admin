from django import forms as django_forms
from django.db.models.fields.related import ForeignKey, ManyToManyField, FieldDoesNotExist

import floppyforms as forms
from mapentity.forms import MapEntityForm

from geotrek.authent.models import (default_structure, StructureRelated,
                                    StructureRelatedQuerySet)

from .models import NoDeleteMixin


class CommonForm(MapEntityForm):

    class Meta(MapEntityForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super(CommonForm, self).__init__(*args, **kwargs)

        # Check if structure is present, if so, use hidden input
        if 'structure' in self.fields:
            self.fields['structure'].widget = forms.HiddenInput()
            # On entity creation, use user's structure
            if not self.instance or not self.instance.pk:
                structure = default_structure()
                if self.user:
                    structure = self.user.profile.structure
                self.fields['structure'].initial = structure

        for name, field in self.fields.items():
            if isinstance(field, django_forms.models.ModelChoiceField):
                try:
                    modelfield = self.instance._meta.get_field(name)
                except FieldDoesNotExist:
                    # be careful but custom form fields, not in model
                    modelfield = None
                if isinstance(modelfield, (ForeignKey, ManyToManyField)):
                    model = modelfield.related.parent_model
                    # Filter structured choice fields according to user's structure
                    if issubclass(model, StructureRelated):
                        field.queryset = StructureRelatedQuerySet.queryset_for_user(field.queryset, self.user)
                    if issubclass(model, NoDeleteMixin):
                        field.queryset = field.queryset.filter(deleted=False)
