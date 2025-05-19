import logging
import os
import re
import traceback

from django.conf import settings
from django.db import connection
from django.db.models import ManyToManyField
from django.template.loader import get_template

from geotrek.common.utils import spatial_reference

logger = logging.getLogger(__name__)


def load_sql_files(app, stage):
    """
    Look for SQL files in Django app, and load them into database.
    """
    if "geotrek" not in app.name:
        return
    sql_dir = os.path.normpath(os.path.join(app.path, "templates", app.label, "sql"))
    custom_sql_dir = os.path.join(settings.VAR_DIR, "conf", "extra_sql", app.label)
    sql_files = []
    r = re.compile(rf"^{stage}_.*\.sql$")
    if os.path.exists(sql_dir):
        sql_files += [
            os.path.join(sql_dir, f)
            for f in os.listdir(sql_dir)
            if r.match(f) is not None
        ]
    if os.path.exists(custom_sql_dir):
        sql_files += [
            os.path.join(custom_sql_dir, f)
            for f in os.listdir(custom_sql_dir)
            if r.match(f) is not None
        ]
    sql_files.sort()

    schemas = settings.DATABASE_SCHEMAS

    schema_app = schemas.get(app.name)
    schema = schema_app if schema_app else schemas.get("default", "public")

    schema_django = schemas.get("django")
    schema_django = schema_django if schema_django else schemas.get("default", "public")

    cursor = connection.cursor()
    for sql_file in sql_files:
        try:
            logger.info("Loading initial SQL data from '%s'", sql_file)
            template = get_template(sql_file)
            context_settings = settings.__dict__["_wrapped"].__dict__
            # fix languages in sql TEMPLATES
            # (django-modeltranslations use _ instead of - in sub languages)
            fixed_languages = []
            for language in context_settings["MODELTRANSLATION_LANGUAGES"]:
                fixed_languages.append(language.replace("-", "_"))
            context_settings["MODELTRANSLATION_LANGUAGES"] = fixed_languages
            context = dict(
                schema_geotrek=schema,
                schema_django=schema_django,
                spatial_reference=spatial_reference(),
            )
            context.update(context_settings)
            rendered_sql = template.render(context)

            cursor.execute(rendered_sql)
        except Exception as e:
            logger.critical("Failed to install custom SQL file '%s': %s\n", sql_file, e)
            traceback.print_exc()
            raise


def set_search_path():
    # Set search path with all existing schema + new ones
    cursor = connection.cursor()
    cursor.execute("SELECT schema_name FROM information_schema.schemata")
    search_path = set([s[0] for s in cursor.fetchall() if not s[0].startswith("pg_")])
    search_path |= set(settings.DATABASE_SCHEMAS.values())
    search_path.discard("public")
    search_path.discard("information_schema")
    search_path = ("public", *tuple(search_path))
    cursor.execute("SET search_path TO {}".format(", ".join(search_path)))


def move_models_to_schemas(app):
    """
    Move models tables to PostgreSQL schemas.

    Views, functions and triggers will be moved in Geotrek app SQL files.
    """
    default_schema = settings.DATABASE_SCHEMAS.get("default", "public")
    app_schema = settings.DATABASE_SCHEMAS.get(app.name, default_schema)

    table_schemas = {}
    for model in app.get_models():
        model_name = model._meta.model_name
        table_name = model._meta.db_table
        model_schema = settings.DATABASE_SCHEMAS.get(model_name, app_schema)
        table_schemas.setdefault(model_schema, []).append(table_name)

        for field in model._meta.get_fields():
            if isinstance(field, ManyToManyField):
                table_schemas[model_schema].append(field.m2m_db_table())

    cursor = connection.cursor()

    for schema_name in table_schemas.keys():
        sql = f"CREATE SCHEMA IF NOT EXISTS {model_schema};"
        cursor.execute(sql)
        logger.info("Created schema %s", model_schema)

    for schema_name, tables in table_schemas.items():
        for table_name in tables:
            sql = "SELECT 1 FROM information_schema.tables WHERE table_name=%s AND table_schema!=%s"
            cursor.execute(sql, [table_name, schema_name])
            if cursor.fetchone():
                sql = f"ALTER TABLE {table_name} SET SCHEMA {schema_name};"
                cursor.execute(sql)
                logger.info("Moved %s to schema %s", table_name, schema_name)

    # For Django, search_path is set in connection options.
    # But when accessing the database using QGis or ETL, search_path must be
    # set database level (for all users, and for this database only).
    if app.name == "geotrek.common":
        dbname = settings.DATABASES["default"]["NAME"]
        dbuser = settings.DATABASES["default"]["USER"]
        search_path = ", ".join(
            ("public", *tuple(set(settings.DATABASE_SCHEMAS.values())))
        )
        sql = f'ALTER ROLE "{dbuser}" IN DATABASE "{dbname}" SET search_path={search_path};'
        cursor.execute(sql)
