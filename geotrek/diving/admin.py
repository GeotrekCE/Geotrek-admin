from django.conf import settings
from django.contrib import admin
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from geotrek.common.mixins.actions import MergeActionMixin

from . import forms, models

if "modeltranslation" in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin
else:
    from django.contrib.admin import ModelAdmin as TabbedTranslationAdmin

if settings.DIVE_MODEL_ENABLED:

    @admin.register(models.Practice)
    class PracticeAdmin(MergeActionMixin, TabbedTranslationAdmin):
        list_display = ("name", "order", "pictogram_img")
        search_fields = ("name",)

    @admin.register(models.Difficulty)
    class DifficultyAdmin(MergeActionMixin, TabbedTranslationAdmin):
        form = forms.DifficultyForm
        list_display = ("name", "id", "pictogram_img")
        search_fields = ("name",)
        fields = ("id", "name", "pictogram")
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
                for t in models.Dive.objects.filter(difficulty=form.oldid):
                    t.difficulty = None
                    t.save()
                    migrated.append(t)
                # Apply id change
                self.oldid = form.oldid
                obj.save()  # Will create new row in DB
                old = models.Difficulty.objects.get(id=self.oldid)
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
                msg = _(
                    "Difficulty id {old} was changed to {new} successfully."
                ).format(old=self.oldid, new=obj.pk)
                self.message_user(request, msg)
                return self.response_post_save_change(request, obj)
            return super().response_change(request, obj)

    @admin.register(models.Level)
    class LevelAdmin(MergeActionMixin, TabbedTranslationAdmin):
        form = forms.LevelForm
        list_display = ("name", "id", "pictogram_img")
        search_fields = ("name",)
        fields = ("id", "name", "description", "pictogram")
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
                for t in models.Dive.objects.filter(levels__in=[form.oldid]):
                    t.levels.remove(models.Level.objects.get(id=form.oldid))
                    t.save()
                    migrated.append(t)
                # Apply id change
                self.oldid = form.oldid
                obj.save()  # Will create new row in DB
                old = models.Level.objects.get(id=self.oldid)
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
                msg = _("Level id {old} was changed to {new} successfully.").format(
                    old=self.oldid, new=obj.pk
                )
                self.message_user(request, msg)
                return self.response_post_save_change(request, obj)
            return super().response_change(request, obj)
