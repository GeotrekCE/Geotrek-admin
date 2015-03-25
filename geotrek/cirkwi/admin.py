from django.contrib import admin

from .models import CirkwiTag, CirkwiLocomotion, CirkwiPOICategory


class CirkwiAdmin(admin.ModelAdmin):
    list_display = ('name', 'eid')
    search_fields = ('name', '=eid')


admin.site.register(CirkwiTag, CirkwiAdmin)
admin.site.register(CirkwiLocomotion, CirkwiAdmin)
admin.site.register(CirkwiPOICategory, CirkwiAdmin)
