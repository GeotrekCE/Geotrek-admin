from django.contrib import admin

from .models import CirkwiLocomotion, CirkwiPOICategory, CirkwiTag


@admin.register(CirkwiLocomotion, CirkwiPOICategory, CirkwiTag)
class CirkwiAdmin(admin.ModelAdmin):
    list_display = ("name", "eid")
    search_fields = ("name", "=eid")
