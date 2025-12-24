import logging
from typing import cast

from django.conf import settings
from django.core.management.color import no_style
from django.db import connection, migrations, models, utils
from django.db.models import Field, Model
from modeltranslation.translator import TranslationOptions, translator
from modeltranslation.utils import build_localized_fieldname

from geotrek.sensitivity.models import SensitiveArea

logger = logging.getLogger(__name__)


def get_sync_sql(
    field_name: str, missing_langs: list[str], model: type[Model]
) -> list[str]:
    """
    Returns SQL needed for sync schema for a new translatable field.
    """
    qn = connection.ops.quote_name
    style = no_style()
    sql_output: list[str] = []
    db_table = model._meta.db_table
    for lang in missing_langs:
        new_field = build_localized_fieldname(field_name, lang)
        f = cast(Field, model._meta.get_field(new_field))
        col_type = f.db_type(connection=connection)
        field_sql = [style.SQL_FIELD(qn(f.column)), style.SQL_COLTYPE(col_type)]  # type: ignore[arg-type]
        # column creation
        stmt = "ALTER TABLE {} ADD COLUMN IF NOT EXISTS {}".format(qn(db_table), " ".join(field_sql))
        if not f.null:
            stmt += " " + style.SQL_KEYWORD("NOT NULL")
        sql_output.append(stmt + ";")
    return sql_output


def create_translation_fields(apps, schema_editor):
    translated_fields = [
        "name",
        "description",
    ]

    class SensitiveAreaTO(TranslationOptions):
        fields = translated_fields

    SensitiveArea = apps.get_model("sensitivity", "SensitiveArea")
    translator.register(SensitiveArea, SensitiveAreaTO)

    langs = settings.MODELTRANSLATION_LANGUAGES

    for field in translated_fields:
        sql_statements = get_sync_sql(field, langs, SensitiveArea)
        with connection.cursor() as cursor:
            for sql in sql_statements:
                cursor.execute(sql)

def generate_name(apps, schema_editor):
    """Populate SensitiveAreas name from Species"""

    sensitive_area = SensitiveArea
    languages = settings.MODELTRANSLATION_LANGUAGES
    update_fields = [
        "name",
    ]
    update_fields += [f"name_{lang}" for lang in languages]
    for row in sensitive_area.objects.existing().filter(species__category=2):
        for field in update_fields:
            try:
                setattr(row, field, getattr(row.species, field))
                row.save(update_fields=update_fields)
            except utils.ProgrammingError as e:
                logger.warning('[Update sensitive areas] An error occured during migration : %s', e)
        for field in update_fields:
            # print(f"species.manager {row.species._meta.managers}")
            # print(f"row {row.species} | field {field}")
            try:
                setattr(row.species, field, "")
                row.species.save(update_fields=update_fields)
            except utils.ProgrammingError as e:
                logger.warning('[Update sensitive species] An error occured during migration : %s', e)

class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0030_alter_sensitivearea_eid"),
    ]

    operations = [
        migrations.AddField(
            model_name="sensitivearea",
            name="name",
            field=models.CharField(default="", max_length=250, verbose_name="Name"),
        ),
        # migrations.RunPython(update_translation_fields_func, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(create_translation_fields, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(generate_name, reverse_code=migrations.RunPython.noop),
    ]
