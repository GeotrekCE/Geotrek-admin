"""
    Administration of authentication
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from caminae.authent.models import Structure
from caminae.authent.models import UserProfile


admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    """ Custom form """
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    """ Custom adminsite """
    inlines = [ UserProfileInline, ]

if settings.AUTHENT_TABLENAME:
    # If users are authenticated in a custom database, do not manage them here.
    admin.site.unregister(Group)
else:
    admin.site.register(User, UserProfileAdmin)
    admin.site.register(Structure)
