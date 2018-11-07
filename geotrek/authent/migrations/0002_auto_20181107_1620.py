# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import django.apps
from django.core.management import call_command


def add_permissions():
    call_command('update_geotrek_permissions', verbosity=0)
    UserModel = django.apps.apps.get_model('auth', 'User')
    PermissionModel = django.apps.apps.get_model('auth', 'Permission')
    permissions = ['path', 'service', 'poi', 'touristicevent', 'touristiccontent', 'project',
                   'trek', 'intervention', 'signage', 'workmanagementedge',
                   'signagemanagementedge', 'physicaledge', 'competenceedge', 'infrastructure',
                   'report', 'trail', 'path'
                   ]
    for user in UserModel.objects.all():
        for perm in permissions:
            user.user_permissions.add(PermissionModel.objects.get(
                codename='change_geom_%s' % perm))


class Migration(migrations.Migration):

    dependencies = [
        ('authent', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_permissions)
    ]
