# -*- coding: utf-8 -*-

from django import forms
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from tinymce.widgets import TinyMCE

from geotrek.authent.admin import TrekkingManagerModelAdmin
from .models import (
    POIType, Theme, TrekNetwork, Usage, Route, DifficultyLevel, WebLink,
    WebLinkCategory, InformationDesk, Trek
)


class POITypeAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label',)


class ThemeAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label',)


class TrekNetworkAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('network',)
    search_fields = ('network',)


class UsageAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('usage', 'pictogram_img')
    search_fields = ('usage',)


class RouteAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('route',)
    search_fields = ('route',)


class DifficultyLevelForm(forms.ModelForm):

    def clean_id(self):
        self.oldid = self.instance.pk if self.instance else None
        self.newid = self.cleaned_data.get('id')

        exists = len(DifficultyLevel.objects.filter(pk=self.newid)) > 0
        if self.oldid != self.newid and exists:
            raise ValidationError(_("Difficulty with id '%s' already exists") % self.newid)
        return self.newid


class DifficultyLevelAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    form = DifficultyLevelForm
    list_display = ('id', 'difficulty',)
    search_fields = ('difficulty',)
    fields = ('id', 'difficulty')

    def save_model(self, request, obj, form, change):
        """
        Allows to change DifficultyLevel id from Admin form.
        It will migrate all treks using this difficulty to the new id.
        """
        self.oldid = None

        # Nominal case. No migration.
        if form.oldid is None or form.oldid == form.newid:
            obj.save()
            return

        with transaction.atomic():
            # Migrate Treks
            migrated = []
            for t in Trek.objects.filter(difficulty=form.oldid):
                t.difficulty = None
                t.save()
                migrated.append(t)
            # Apply id change
            self.oldid = form.oldid
            obj.save()  # Will create new row in DB
            old = DifficultyLevel.objects.get(id=self.oldid)
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
            msg = _('Difficulty id %s was changed to %s successfully.') % (
                self.oldid, obj.pk)
            self.message_user(request, msg)
            return self.response_post_save_change(request, obj)
        return super(DifficultyLevelAdmin, self).response_change(request, obj)


class WebLinkAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('name', 'url', )
    search_fields = ('name', 'url', )


class WebLinkCategoryAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label', )


class InformationDeskAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE},
    }


# Register previously defined modeladmins
trek_admin_to_register = [
    (POIType, POITypeAdmin),
    (Theme, ThemeAdmin),
    (TrekNetwork, TrekNetworkAdmin),
    (Usage, UsageAdmin),
    (Route, RouteAdmin),
    (DifficultyLevel, DifficultyLevelAdmin),
    (WebLink, WebLinkAdmin),
    (WebLinkCategory, WebLinkCategoryAdmin),
    (InformationDesk, InformationDeskAdmin),
]

for model, model_admin in trek_admin_to_register:
    admin.site.register(model, model_admin)
