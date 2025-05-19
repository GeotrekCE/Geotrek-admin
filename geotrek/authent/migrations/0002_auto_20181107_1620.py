from django.core.management import call_command
from django.db import migrations


def add_permissions(apps, schema_editor):
    call_command("update_geotrek_permissions", verbosity=0)
    UserModel = apps.get_model("auth", "User")
    GroupModel = apps.get_model("auth", "Group")
    PermissionModel = apps.get_model("auth", "Permission")
    permissions = [
        "path",
        "service",
        "poi",
        "touristicevent",
        "touristiccontent",
        "project",
        "trek",
        "intervention",
        "signage",
        "workmanagementedge",
        "signagemanagementedge",
        "physicaledge",
        "competenceedge",
        "infrastructure",
        "report",
        "trail",
        "path",
    ]
    for user in UserModel.objects.all():
        for perm in permissions:
            if user.user_permissions.filter(codename=f"change_{perm}").exists():
                user.user_permissions.add(
                    PermissionModel.objects.get(codename=f"change_geom_{perm}")
                )

    for group in GroupModel.objects.all():
        for perm in permissions:
            if group.permissions.filter(codename=f"change_{perm}").exists():
                group.permissions.add(
                    PermissionModel.objects.get(codename=f"change_geom_{perm}")
                )


class Migration(migrations.Migration):
    dependencies = [
        ("authent", "0001_initial"),
    ]

    operations = [migrations.RunPython(add_permissions)]
