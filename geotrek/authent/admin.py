"""
Administration of authentication
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from mapentity.settings import app_settings as MAPENTITY_SETTINGS

from geotrek.authent.models import Structure, UserProfile
from geotrek.common.mixins.actions import MergeActionMixin

admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    """Custom form"""

    model = UserProfile


class UserProfileAdmin(UserAdmin):
    """Custom adminsite"""
    list_display = ("username", "first_name", "last_name", "email", "is_active", "is_staff", "is_superuser")
    inlines = [UserProfileInline]

    def get_readonly_fields(self, request, obj=None):
        """Make the password field read-only"""
        ro_fields = super().get_readonly_fields(request, obj)
        if obj and obj.username == MAPENTITY_SETTINGS["INTERNAL_USER"]:
            # If the user is the internal user, make all fields read-only
            ro_fields += ("username", "password", "is_active", "is_staff", "is_superuser", "groups", "user_permissions", "first_name", "last_name", "email")
        return ro_fields

    def get_inlines(self, request, obj=None):
        """Remove the UserProfileInline if the user is the internal user"""
        if obj and obj.username == MAPENTITY_SETTINGS["INTERNAL_USER"]:
            return []
        return super().get_inlines(request, obj)

    def has_change_permission(self, request, obj = None):
        if obj and obj.username == MAPENTITY_SETTINGS["INTERNAL_USER"]:
            return []
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj = None):
        if obj and obj.username == MAPENTITY_SETTINGS["INTERNAL_USER"]:
            return []
        return super().has_delete_permission(request, obj)

class StructureAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    merge_field = "name"


if not settings.AUTHENT_TABLENAME:
    # If users are authenticated in a custom database, do not manage them here.
    admin.site.register(User, UserProfileAdmin)
    admin.site.register(Structure, StructureAdmin)
