"""
    Administration of authentication
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from geotrek.authent.models import Structure
from geotrek.authent.models import UserProfile
from geotrek.common.admin import MergeActionMixin


User = get_user_model()


admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    """ Custom form """
    model = UserProfile


class UserProfileAdmin(UserAdmin):
    """ Custom adminsite """
    inlines = [UserProfileInline]


class StructureAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    merge_field = "name"


if not settings.AUTHENT_TABLENAME:
    # If users are authenticated in a custom database, do not manage them here.
    admin.site.register(User, UserProfileAdmin)
    admin.site.register(Structure, StructureAdmin)
