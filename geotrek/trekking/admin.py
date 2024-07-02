from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db import models
from django.utils.translation import gettext_lazy as _

from django.utils.html import format_html

from geotrek.common.mixins.actions import MergeActionMixin
from .models import (
    POIType, TrekNetwork, Practice, Accessibility, AccessibilityLevel, Route, DifficultyLevel,
    WebLink, WebLinkCategory, Trek, ServiceType, Rating, RatingScale
)

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
else:
    from django.contrib.admin import ModelAdmin as TabbedTranslationAdmin, TabularInline as TranslationTabularInline


class POITypeAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('label', 'cirkwi', 'pictogram_img')
    search_fields = ('label',)
    merge_field = 'label'


class TrekNetworkAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('network', 'pictogram_img')
    search_fields = ('network',)
    merge_field = 'network'


class PracticeAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('id', 'name', 'order', 'cirkwi', 'distance', 'pictogram_img')
    search_fields = ('name',)
    merge_field = 'network'


class AccessibilityAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name', 'cirkwi', 'pictogram_img')
    search_fields = ('name',)
    merge_field = 'network'


class AccessibilityLevelAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    merge_field = 'name'


class RouteAdmin(MergeActionMixin, TabbedTranslationAdmin):
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


class DifficultyLevelAdmin(MergeActionMixin, TabbedTranslationAdmin):
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
        return super().response_change(request, obj)


class WebLinkAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name', 'url', )
    search_fields = ('name', 'url', )
    merge_field = 'name'


class WebLinkCategoryAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label', )
    merge_field = 'label'


class RatingAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name', 'scale', 'order', 'color_markup', 'pictogram_img')
    list_filter = ('scale', 'scale__practice')
    search_fields = ('name', 'description', 'scale__name')
    merge_field = 'name'

    @admin.display(
        description=_("Color")
    )
    def color_markup(self, obj):
        if not obj.color:
            return ''
        return format_html('<span style="color: {code};">⬤</span> {code}', code=obj.color)


class RatingAdminInLine(TranslationTabularInline):
    model = Rating
    extra = 1   # We need one extra to generate Tabbed Translation Tabular inline
    formfield_overrides = {
        models.TextField: {'widget': widgets.AdminTextareaWidget(
            attrs={'rows': 1,
                   'cols': 40,
                   'style': 'height: 1em;'})},
    }


class RatingScaleAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name', 'practice', 'order')
    list_filter = ('practice', )
    search_fields = ('name', )
    merge_field = 'name'
    inlines = [RatingAdminInLine]


class ServiceTypeAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name', 'pictogram_img', 'practices_display')
    search_fields = ('name',)
    merge_field = 'name'

    @admin.display(
        description=_("Practices")
    )
    def practices_display(self, obj):
        return ', '.join([practice.name for practice in obj.practices.all()])


# Register previously defined modeladmins
trek_admin_to_register = [
    (POIType, POITypeAdmin),
    (TrekNetwork, TrekNetworkAdmin),
    (Practice, PracticeAdmin),
    (Accessibility, AccessibilityAdmin),
    (AccessibilityLevel, AccessibilityLevelAdmin),
    (Route, RouteAdmin),
    (DifficultyLevel, DifficultyLevelAdmin),
    (WebLink, WebLinkAdmin),
    (WebLinkCategory, WebLinkCategoryAdmin),
    (ServiceType, ServiceTypeAdmin),
    (Rating, RatingAdmin),
    (RatingScale, RatingScaleAdmin),
]

for model, model_admin in trek_admin_to_register:
    admin.site.register(model, model_admin)
