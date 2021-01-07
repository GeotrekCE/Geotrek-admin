from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from geotrek.common.mixins import MergeActionMixin
from .models import (
    Practice, Difficulty, Level, Dive
)

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TranslationAdmin
else:
    TranslationAdmin = admin.ModelAdmin


class PracticeAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', 'order', 'pictogram_img')
    search_fields = ('name', )


class DifficultyForm(forms.ModelForm):
    def clean_id(self):
        self.oldid = self.instance.pk if self.instance else None
        self.newid = self.cleaned_data.get('id')

        exists = len(Difficulty.objects.filter(pk=self.newid)) > 0
        if self.oldid != self.newid and exists:
            raise ValidationError(_("Difficulty with id '%s' already exists") % self.newid)
        return self.newid


class DifficultyAdmin(MergeActionMixin, TranslationAdmin):
    form = DifficultyForm
    list_display = ('name', 'id', 'pictogram_img')
    search_fields = ('name',)
    fields = ('id', 'name', 'pictogram')
    merge_field = "name"

    def save_model(self, request, obj, form, change):
        """
        Allows to change Difficulty id from Admin form.
        It will migrate all dives using this difficulty to the new id.
        """
        self.oldid = None

        # Nominal case. No migration.
        if form.oldid is None or form.oldid == form.newid:
            obj.save()
            return

        with transaction.atomic():
            # Migrate Dives
            migrated = []
            for t in Dive.objects.filter(difficulty=form.oldid):
                t.difficulty = None
                t.save()
                migrated.append(t)
            # Apply id change
            self.oldid = form.oldid
            obj.save()  # Will create new row in DB
            old = Difficulty.objects.get(id=self.oldid)
            old.delete()
            # Restore
            for t in migrated:
                t.difficulty = obj
                t.save()

    def response_change(self, request, obj):
        """
        If id was changed, always returns to the list (prevent 404).
        Otherwise, behave as usual.
        """
        if self.oldid is not None:
            msg = _('Difficulty id {old} was changed to {new} successfully.').format(
                old=self.oldid, new=obj.pk)
            self.message_user(request, msg)
            return self.response_post_save_change(request, obj)
        return super(DifficultyAdmin, self).response_change(request, obj)


class LevelForm(forms.ModelForm):
    def clean_id(self):
        self.oldid = self.instance.pk if self.instance else None
        self.newid = self.cleaned_data.get('id')

        exists = len(Level.objects.filter(pk=self.newid)) > 0
        if self.oldid != self.newid and exists:
            raise ValidationError(_("Level with id '%s' already exists") % self.newid)
        return self.newid


class LevelAdmin(MergeActionMixin, TranslationAdmin):
    form = LevelForm
    list_display = ('name', 'id', 'pictogram_img')
    search_fields = ('name',)
    fields = ('id', 'name', 'description', 'pictogram')
    merge_field = "name"

    def save_model(self, request, obj, form, change):
        """
        Allows to change Level id from Admin form.
        It will migrate all dives using these levels to the new id.
        """
        self.oldid = None

        # Nominal case. No migration.
        if form.oldid is None or form.oldid == form.newid:
            obj.save()
            return

        with transaction.atomic():
            # Migrate Dives
            migrated = []
            for t in Dive.objects.filter(levels__in=[form.oldid]):
                t.levels.remove(Level.objects.get(id=form.oldid))
                t.save()
                migrated.append(t)
            # Apply id change
            self.oldid = form.oldid
            obj.save()  # Will create new row in DB
            old = Level.objects.get(id=self.oldid)
            old.delete()
            # Restore
            for t in migrated:
                t.levels.add(obj)
                t.save()

    def response_change(self, request, obj):
        """
        If id was changed, always returns to the list (prevent 404).
        Otherwise, behave as usual.
        """
        if self.oldid is not None:
            msg = _('Level id {old} was changed to {new} successfully.').format(
                old=self.oldid, new=obj.pk)
            self.message_user(request, msg)
            return self.response_post_save_change(request, obj)
        return super(LevelAdmin, self).response_change(request, obj)


# Register previously defined modeladmins
admin_to_register = [
    (Practice, PracticeAdmin),
    (Difficulty, DifficultyAdmin),
    (Level, LevelAdmin),
]

for model, model_admin in admin_to_register:
    admin.site.register(model, model_admin)
