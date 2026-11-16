# Generated manually for django-treebeard migration

import django.db.models.deletion
from django.db import migrations, models
from treebeard.mp_tree import MP_Node


def migrate_mptt_to_treebeard(apps, schema_editor):
    Site = apps.get_model("outdoor", "Site")
    if Site.objects.count() == 0:
        return

    # Fetch all sites ordered by tree_id, lft
    sites = list(Site.objects.all().order_by("tree_id", "lft"))
    by_parent = {}
    for site in sites:
        by_parent.setdefault(site.parent_id, []).append(site)

    def build_tree(parent_id, parent_path, depth):
        children = by_parent.get(parent_id, [])
        for pos, child in enumerate(children, start=1):
            child_path = MP_Node._get_path(parent_path, depth, pos)
            child.path = child_path
            child.depth = depth
            child.numchild = len(by_parent.get(child.id, []))
            child.save(update_fields=["path", "depth", "numchild"])
            build_tree(child.id, child_path, depth + 1)

    build_tree(None, None, 1)

    # In case any orphaned or disconnected sites remain without path
    remaining_sites = Site.objects.filter(path="")
    if remaining_sites.exists():
        start_pos = len(by_parent.get(None, [])) + 1
        for pos, site in enumerate(remaining_sites, start=start_pos):
            site.path = MP_Node._get_path(None, 1, pos)
            site.depth = 1
            site.numchild = 0
            site.save(update_fields=["path", "depth", "numchild"])


class Migration(migrations.Migration):
    dependencies = [
        ("outdoor", "0048_site_outdoor_site_tree_id_lft_idx"),
    ]

    operations = [
        # 1. Add treebeard fields with temporary defaults
        migrations.AddField(
            model_name="site",
            name="depth",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="site",
            name="numchild",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="site",
            name="path",
            field=models.CharField(default="", max_length=255),
        ),
        # 2. Populate path, depth, numchild from existing parent_id & tree_id/lft
        migrations.RunPython(
            migrate_mptt_to_treebeard, reverse_code=migrations.RunPython.noop
        ),
        # 3. Alter path to be unique and depth without default
        migrations.AlterField(
            model_name="site",
            name="path",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="site",
            name="depth",
            field=models.PositiveIntegerField(),
        ),
        # 4. Alter parent field from TreeForeignKey to standard ForeignKey
        migrations.AlterField(
            model_name="site",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="children",
                to="outdoor.site",
                verbose_name="Parent",
            ),
        ),
        # 5. Remove MPTT index and fields
        migrations.RemoveIndex(
            model_name="site",
            name="outdoor_site_tree_id_lft_idx",
        ),
        migrations.RemoveField(
            model_name="site",
            name="level",
        ),
        migrations.RemoveField(
            model_name="site",
            name="lft",
        ),
        migrations.RemoveField(
            model_name="site",
            name="rght",
        ),
        migrations.RemoveField(
            model_name="site",
            name="tree_id",
        ),
    ]
