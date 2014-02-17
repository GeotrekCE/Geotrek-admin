"""
    Administration of authentication
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from geotrek.authent.models import Structure
from geotrek.authent.models import UserProfile


admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    """ Custom form """
    model = UserProfile


class UserProfileAdmin(UserAdmin):
    """ Custom adminsite """
    inlines = [UserProfileInline]


if settings.AUTHENT_TABLENAME:
    # If users are authenticated in a custom database, do not manage them here.
    admin.site.unregister(Group)
else:
    admin.site.register(User, UserProfileAdmin)
    admin.site.register(Structure)


class AuthentModelAdmin(admin.ModelAdmin):
    """
    Custom AuthentModelAdmin in order to show specific models in AdminSite.
    """

    def _has_permission(self, user):
        return True  # Likely to be overriden :)

    def _is_admin(self, user):
        return user.is_active and user.is_superuser

    def has_add_permission(self, request):
        return self._is_admin(request.user) or self._has_permission(request.user)

    def has_change_permission(self, request, obj=None):
        return self._is_admin(request.user) or self._has_permission(request.user)

    def has_delete_permission(self, request, obj=None):
        return self._is_admin(request.user) or self._has_permission(request.user)


class PathManagerModelAdmin(AuthentModelAdmin):
    def _has_permission(self, user):
        return user.profile.is_path_manager


class TrekkingManagerModelAdmin(AuthentModelAdmin):
    def _has_permission(self, user):
        return user.profile.is_trekking_manager
