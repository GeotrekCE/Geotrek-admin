"""First script (1/3) of the migration for the MenuItem model

It is divided over 3 migration scripts:

- 0010 creates the MenuItem model,
- 0011 performs the partial data migration between FlatPages and MenuItems,
- 0012 changes the FlatPage model.

This migration script performs a RunPython operation in order to create the translation fields for MenuItem DURING the
migration process (it normally takes place at the end, modeltranslation `sync_translation_fields` and `update_translation_fields`
are run by the overridden `migrate` command).

Translation fields are "title_en", "title_fr", etc...

The translation fields are needed during the migration for the data migration from the FlatPages.
"""

import django.db.models.deletion
from django.conf import settings
from django.core.management.color import no_style
from django.db import connection, migrations, models
from modeltranslation.translator import TranslationOptions, translator
from modeltranslation.utils import build_localized_fieldname


def get_sync_sql(field_name, missing_langs, model):
    """
    Returns SQL (as a list of statements) needed to update schema for new translatable fields.
    From django-modeltranslation: https://github.com/deschler/django-modeltranslation/blob/c34f67491ab59bb6a31eabeb96938c43d2fdd303/modeltranslation/management/commands/sync_translation_fields.py#L137
    """
    qn = connection.ops.quote_name
    style = no_style()
    sql_output = []
    db_table = model._meta.db_table
    for lang in missing_langs:
        new_field = build_localized_fieldname(field_name, lang)
        f = model._meta.get_field(new_field)
        col_type = f.db_type(connection=connection)
        field_sql = [style.SQL_FIELD(qn(f.column)), style.SQL_COLTYPE(col_type)]
        # column creation
        stmt = "ALTER TABLE {} ADD COLUMN {}".format(qn(db_table), " ".join(field_sql))
        if not f.null:
            stmt += " " + "NOT NULL"
        sql_output.append(stmt + ";")
    return sql_output


def create_translation_fields(apps, schema_editor):
    translated_fields = [
        "title",
        "link_url",
    ]
    if settings.PUBLISHED_BY_LANG:
        translated_fields.append("published")

    class MenuItemTO(TranslationOptions):
        fields = translated_fields

    MenuItem = apps.get_model("flatpages", "MenuItem")
    translator.register(MenuItem, MenuItemTO)

    langs = settings.MODELTRANSLATION_LANGUAGES

    for field in translated_fields:
        sql_statements = get_sync_sql(field, langs, MenuItem)
        with connection.cursor() as cursor:
            for sql in sql_statements:
                cursor.execute(sql)


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0036_accessmean"),
        ("flatpages", "0009_auto_20210121_0943"),
    ]

    operations = [
        migrations.CreateModel(
            name="MenuItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_insert",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Insertion date"
                    ),
                ),
                (
                    "date_update",
                    models.DateTimeField(
                        auto_now=True, db_index=True, verbose_name="Update date"
                    ),
                ),
                (
                    "published",
                    models.BooleanField(
                        default=False,
                        help_text="Visible on Geotrek-rando",
                        verbose_name="Published",
                    ),
                ),
                (
                    "publication_date",
                    models.DateField(
                        blank=True,
                        editable=False,
                        null=True,
                        verbose_name="Publication date",
                    ),
                ),
                (
                    "pictogram",
                    models.FileField(
                        blank=True,
                        max_length=512,
                        null=True,
                        upload_to="upload",
                        verbose_name="Pictogram",
                    ),
                ),
                ("path", models.CharField(max_length=255, unique=True)),
                ("depth", models.PositiveIntegerField()),
                ("numchild", models.PositiveIntegerField(default=0)),
                ("title", models.CharField(max_length=200, verbose_name="Title")),
                (
                    "target_type",
                    models.CharField(
                        blank=True,
                        choices=[("page", "Page"), ("link", "Link")],
                        max_length=10,
                        null=True,
                        verbose_name="Target type",
                    ),
                ),
                (
                    "link_url",
                    models.CharField(
                        max_length=200, blank=True, default="", verbose_name="Link URL"
                    ),
                ),
                (
                    "platform",
                    models.CharField(
                        choices=[("all", "All"), ("mobile", "Mobile"), ("web", "Web")],
                        default="all",
                        max_length=12,
                        verbose_name="Platform",
                    ),
                ),
                (
                    "open_in_new_tab",
                    models.BooleanField(
                        default=True, verbose_name="Open the link in a new tab"
                    ),
                ),
                (
                    "page",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="menu_items",
                        to="flatpages.flatpage",
                    ),
                ),
                (
                    "portals",
                    models.ManyToManyField(
                        blank=True,
                        related_name="menu_items",
                        to="common.TargetPortal",
                        verbose_name="Portals",
                    ),
                ),
            ],
            options={
                "verbose_name": "Menu item",
                "verbose_name_plural": "Menu items",
            },
        ),
        migrations.RunPython(
            create_translation_fields, reverse_code=migrations.RunPython.noop
        ),
    ]
