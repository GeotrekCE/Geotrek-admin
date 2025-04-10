# Generated by Django 3.1.14 on 2022-04-05 16:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0022_accessibilityattachment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accessibilityattachment",
            name="author",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Original creator",
                max_length=128,
                verbose_name="Author",
            ),
        ),
        migrations.AlterField(
            model_name="accessibilityattachment",
            name="legend",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Details displayed",
                max_length=128,
                verbose_name="Legend",
            ),
        ),
        migrations.AlterField(
            model_name="accessibilityattachment",
            name="title",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Renames the file",
                max_length=128,
                verbose_name="Filename",
            ),
        ),
    ]
