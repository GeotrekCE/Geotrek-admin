from typing import cast

from django.core.management.color import no_style
from django.db import connection
from django.db.models import Field, Model
from modeltranslation.management.commands.sync_translation_fields import (
    Command as BaseSyncCommand,
)
from modeltranslation.utils import build_localized_fieldname


class Command(BaseSyncCommand):
    def get_sync_sql(
        self, field_name: str, missing_langs: list[str], model: type[Model]
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
            stmt = "ALTER TABLE {} ADD COLUMN {}".format(
                qn(db_table), " ".join(field_sql)
            )
            if not f.null:
                stmt += " " + style.SQL_KEYWORD("NOT NULL")
            if f.has_default() and f.db_default:
                editor = connection.schema_editor()
                default_value = editor.effective_default(f)
                stmt += " " + style.SQL_KEYWORD("DEFAULT") + " " + editor.quote_value(default_value)
            sql_output.append(stmt + ";")
        return sql_output
