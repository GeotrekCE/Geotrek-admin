"""
    Administration of authentication
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from caminae.authent.models import Structure
from caminae.authent.models import UserProfile


admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    """ Custom form """
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    """ Custom adminsite """
    inlines = [ UserProfileInline, ]

admin.site.register(User, UserProfileAdmin)
admin.site.register(Structure)
