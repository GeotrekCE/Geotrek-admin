from django import forms
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib import admin

from geotrek.common.mixins import MergeActionMixin
from .models import (
    POIType, TrekNetwork, Practice, Accessibility, Route, DifficultyLevel,
    WebLink, WebLinkCategory, Trek, ServiceType
)

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TranslationAdmin
else:
    TranslationAdmin = admin.ModelAdmin


class POITypeAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('label', 'cirkwi', 'pictogram_img')
    search_fields = ('label',)
    merge_field = 'label'


class TrekNetworkAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('network', 'pictogram_img')
    search_fields = ('network',)
    merge_field = 'network'


class PracticeAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', 'prefixed_id', 'order', 'cirkwi', 'distance', 'pictogram_img')
    search_fields = ('name',)
    merge_field = 'network'


class AccessibilityAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', 'cirkwi', 'pictogram_img')
    search_fields = ('name',)
    merge_field = 'network'


class RouteAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('route', 'pictogram_img')
    search_fields = ('route',)
    merge_field = 'route'


class DifficultyLevelForm(forms.ModelForm):

    def clean_id(self):
        self.oldid = self.instance.pk if self.instance else None
        self.newid = self.cleaned_data.get('id')

        exists = len(DifficultyLevel.objects.filter(pk=self.newid)) > 0
        if self.oldid != self.newid and exists:
            raise ValidationError(_("Difficulty with id '%s' already exists") % self.newid)
        return self.newid


class DifficultyLevelAdmin(MergeActionMixin, TranslationAdmin):
    form = DifficultyLevelForm
    list_display = ('id', 'difficulty', 'cirkwi_level', 'cirkwi', 'pictogram_img')
    search_fields = ('difficulty',)
    fields = ('id', 'difficulty', 'cirkwi_level', 'cirkwi', 'pictogram')
    merge_field = 'difficulty'

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
            msg = _('Difficulty id {old} was changed to {new} successfully.').format(
                old=self.oldid, new=obj.pk)
            self.message_user(request, msg)
            return self.response_post_save_change(request, obj)
        return super(DifficultyLevelAdmin, self).response_change(request, obj)


class WebLinkAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', 'url', )
    search_fields = ('name', 'url', )
    merge_field = 'name'


class WebLinkCategoryAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label', )
    merge_field = 'label'


class ServiceTypeAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', 'pictogram_img', 'practices_display')
    search_fields = ('name',)
    merge_field = 'name'

    def practices_display(self, obj):
        return ', '.join([practice.name for practice in obj.practices.all()])
    practices_display.short_description = _("Practices")


# Register previously defined modeladmins
trek_admin_to_register = [
    (POIType, POITypeAdmin),
    (TrekNetwork, TrekNetworkAdmin),
    (Practice, PracticeAdmin),
    (Accessibility, AccessibilityAdmin),
    (Route, RouteAdmin),
    (DifficultyLevel, DifficultyLevelAdmin),
    (WebLink, WebLinkAdmin),
    (WebLinkCategory, WebLinkCategoryAdmin),
    (ServiceType, ServiceTypeAdmin),
]

for model, model_admin in trek_admin_to_register:
    admin.site.register(model, model_admin)
