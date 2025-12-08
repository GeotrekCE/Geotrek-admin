"""
Fix migration 0012_change_flatpage_schema: MenuItem automatically created from an old FlatPage should have their
`open_in_new_tab` value to False when their target type is "page".
"""

from django.db import migrations


def update_open_in_new_tab(apps, schema_editor):
    MenuItem = apps.get_model("flatpages", "MenuItem")
    for menu_item in MenuItem.objects.all():
        if menu_item.target_type != "link":
            menu_item.open_in_new_tab = False
            menu_item.save()


class Migration(migrations.Migration):
    dependencies = [
        ("flatpages", "0014_alter_menu_item_title_max_length"),
    ]

    operations = [
        migrations.RunPython(
            update_open_in_new_tab, reverse_code=migrations.RunPython.noop
        ),
    ]
