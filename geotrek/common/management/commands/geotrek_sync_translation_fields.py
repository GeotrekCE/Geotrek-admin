from __future__ import annotations

from collections.abc import Iterator
from typing import cast

from django.conf.global_settings import LANGUAGES as ALL_LANGUAGES
from django.core.management.color import no_style
from django.db import connection
from django.db.models import Field, Model
from modeltranslation.management.commands.sync_translation_fields import (
    Command as BaseSyncCommand,
)
from modeltranslation.settings import AVAILABLE_LANGUAGES
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname


class Command(BaseSyncCommand):
    VALID_LANGUAGE_COLUMN_SUFFIXES = {
        code.replace("-", "_").lower() for code, _ in ALL_LANGUAGES
    }

    def handle(self, *args, **options) -> None:
        super().handle(*args, **options)
        # remove extra languages
        found_extra_fields = False
        models = translator.get_registered_models(abstract=False)
        for model in models:
            db_table = model._meta.db_table
            model_name = model._meta.model_name
            opts = translator.get_options_for_model(model)
            for field_name, fields in opts.local_fields.items():
                field = list(fields)[0]  # Take `db_column` attribute into account
                column_name = field.db_column if field.db_column else field_name
                extra_langs = list(self.get_extra_languages(column_name, db_table))
                if extra_langs:
                    found_extra_fields = True
                    self.stdout.write(
                        f"Extra languages in '{field_name}' field from '{model_name}' model: {', '.join(extra_langs)}"
                    )
                    sql_sentences = self.get_delete_sql(field_name, extra_langs, model)
                    self.stdout.write("Executing SQL...")
                    for sentence in sql_sentences:
                        self.stdout.write("    " + sentence)
                        self.cursor.execute(sentence)
                    self.stdout.write("Done")

        if not found_extra_fields:
            self.stdout.write("No old translatable fields detected")

    def get_extra_languages(self, field_name: str, db_table: str) -> Iterator[str]:
        """
        Gets languages that have a column in the table
        but are no longer in MODELTRANSLATION_LANGUAGES
        """
        prefix = f"{field_name}_"
        available_columns = {
            build_localized_fieldname(field_name, lang_code)
            for lang_code in AVAILABLE_LANGUAGES
        }
        for column in self.get_table_fields(db_table):
            if not column.startswith(prefix) or column in available_columns:
                continue
            suffix = column[len(prefix) :]
            if suffix in self.VALID_LANGUAGE_COLUMN_SUFFIXES:
                yield suffix

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
            if f.has_db_default():
                editor = connection.schema_editor()
                default_value = editor.effective_default(f)
                stmt += (
                    " "
                    + style.SQL_KEYWORD("DEFAULT")
                    + " "
                    + editor.quote_value(default_value)
                )
            sql_output.append(stmt + ";")
        return sql_output

    def get_delete_sql(
        self, field_name: str, extra_langs: list[str], model: type[Model]
    ) -> list[str]:
        """
        Returns SQL needed for remove old translatable field.
        """
        qn = connection.ops.quote_name
        style = no_style()
        sql_output: list[str] = []
        db_table = model._meta.db_table
        for lang in extra_langs:
            old_field = build_localized_fieldname(field_name, lang)
            # column deletion
            sql_output.append(
                f"ALTER TABLE {qn(db_table)} DROP COLUMN {style.SQL_FIELD(qn(old_field))};"
            )
        return sql_output
