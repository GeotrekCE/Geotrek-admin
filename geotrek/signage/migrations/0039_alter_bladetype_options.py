# Generated by Django 3.2.21 on 2023-12-21 08:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("signage", "0038_auto_20231023_1233"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="bladetype",
            options={
                "ordering": ("label",),
                "verbose_name": "Blade type",
                "verbose_name_plural": "Blade types",
            },
        ),
    ]
