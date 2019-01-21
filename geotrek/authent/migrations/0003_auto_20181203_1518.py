# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command
from django.conf import settings


def add_permissions(apps, schema_editor):
    if 'geotrek.infrastructure' in settings.INSTALLED_APPS:
        call_command('update_geotrek_permissions', verbosity=0)
        UserModel = apps.get_model('auth', 'User')
        GroupModel = apps.get_model('auth', 'Group')
        PermissionModel = apps.get_model('auth', 'Permission')
        ContentTypeModel = apps.get_model("contenttypes", "ContentType")
        type_permissions = ['add', 'change', 'change_geom', 'delete', 'export', 'read']
        content_type_signage = ContentTypeModel.objects.get(model='signage')
        content_type_infrastructure = ContentTypeModel.objects.get(model='infrastructure')
        for user in UserModel.objects.all():
            for type_perm in type_permissions:
                if user.user_permissions.filter(codename='%s_infrastructure' % type_perm).exists():
                    user.user_permissions.add(PermissionModel.objects.get(
                        codename='%s_infrastructure' % type_perm, content_type=content_type_infrastructure))
                if user.user_permissions.filter(codename='%s_signage' % type_perm).exists():
                    user.user_permissions.add(PermissionModel.objects.get(
                        codename='%s_signage' % type_perm, content_type=content_type_signage))
        for group in GroupModel.objects.all():
            for type_perm in type_permissions:
                if group.permissions.filter(codename='%s_infrastructure' % type_perm).exists():
                    group.permissions.add(PermissionModel.objects.get(
                        codename='%s_infrastructure' % type_perm, content_type=content_type_infrastructure))
                if group.permissions.filter(codename='%s_signage' % type_perm).exists():
                    group.permissions.add(PermissionModel.objects.get(
                        codename='%s_signage' % type_perm, content_type=content_type_signage))

        PermissionModel.objects.filter(content_type__model='baseinfrastructure').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('authent', '0002_auto_20181107_1620'),
    ]

    operations = [
        migrations.RunPython(add_permissions)
    ]
