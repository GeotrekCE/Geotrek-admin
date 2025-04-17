"""Third script (3/3) of the migration for the MenuItem model

The FlatPage model is changed:

- obsolete fields (moved to MenuItem) are removed,
- new fields are added with `django-treebeard` to support the tree hierarchy.
"""

from django.db import migrations, models
from treebeard.mp_tree import MP_Node
from treebeard.numconv import NumConv


def get_treenode_path(position):
    """Support function to initialize DB field `path` from django-treebeard package's model MP_Node"""
    numconv = NumConv(len(MP_Node.alphabet), MP_Node.alphabet)
    key = numconv.int2str(position)
    path = f"{MP_Node.alphabet[0] * (MP_Node.steplen - len(key))}{key}"
    return path


def set_treebeard_path_fields(apps, schema_editor):
    FlatPage = apps.get_model("flatpages", "FlatPage")
    pages = FlatPage.objects.all()
    for position, page in enumerate(pages):
        page.path = get_treenode_path(position)
        page.save()


class Migration(migrations.Migration):
    dependencies = [
        ("flatpages", "0011_migrate_flatpage_data"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="flatpage",
            options={
                "permissions": (("read_flatpage", "Can read FlatPage"),),
                "verbose_name": "Flat page",
                "verbose_name_plural": "Flat pages",
            },
        ),
        migrations.RenameField(
            model_name="flatpage",
            old_name="portal",
            new_name="portals",
        ),
        migrations.RemoveField(
            model_name="flatpage",
            name="external_url",
        ),
        migrations.RemoveField(
            model_name="flatpage",
            name="order",
        ),
        migrations.RemoveField(
            model_name="flatpage",
            name="target",
        ),
        migrations.AddField(
            model_name="flatpage",
            name="depth",
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="flatpage",
            name="numchild",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="flatpage",
            name="path",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.RunPython(
            set_treebeard_path_fields, reverse_code=migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="flatpage",
            name="path",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
