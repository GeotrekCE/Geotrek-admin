import logging
import traceback
from functools import wraps

import os
import re
from django.conf import settings
from django.db import connection
from django.db.models import ManyToManyField

logger = logging.getLogger(__name__)


def debug_pg_notices(f):

    @wraps(f)
    def wrapped(*args, **kwargs):
        r = None

        if connection.connection:
            del connection.connection.notices[:]
        try:
            r = f(*args, **kwargs)
        finally:
            # Show triggers output
            allnotices = []
            current = ''
            if connection.connection:
                notices = []
                for notice in connection.connection.notices:
                    try:
                        notice, context = notice.split('CONTEXT:', 1)
                        context = re.sub(r"\s+", " ", context)
                    except ValueError:
                        context = ''
                    notices.append((context, notice))
                    if context != current:
                        allnotices.append(notices)
                        notices = []
                        current = context
                allnotices.append(notices)
            current = ''
            for notices in allnotices:
                for context, notice in notices:
                    if context != current:
                        if context != '':
                            logger.debug('Context %s...:' % context.strip()[:80])
                        current = context
                    notice = notice.replace('NOTICE: ', '')
                    prefix = ''
                    logger.debug('%s%s' % (prefix, notice.strip()))
        return r

    return wrapped


def load_sql_files(app, stage):
    """
    Look for SQL files in Django app, and load them into database.
    We remove RAISE NOTICE instructions from SQL outside unit testing
    since they lead to interpolation errors of '%' character in python.
    """
    app_dir = app.path
    sql_dir = os.path.normpath(os.path.join(app_dir, 'sql'))
    custom_sql_dir = os.path.join(settings.VAR_DIR, 'conf/extra_sql', app.label)
    sql_files = []
    r = re.compile(r'^{}_.*\.sql$'.format(stage))
    if os.path.exists(sql_dir):
        sql_files += [
            os.path.join(sql_dir, f) for f in os.listdir(sql_dir) if r.match(f) is not None
        ]
    if os.path.exists(custom_sql_dir):
        sql_files += [
            os.path.join(custom_sql_dir, f) for f in os.listdir(custom_sql_dir) if r.match(f) is not None
        ]
    sql_files.sort()

    cursor = connection.cursor()
    for sql_file in sql_files:
        try:
            logger.info("Loading initial SQL data from '%s'" % sql_file)
            f = open(sql_file)
            sql = f.read()
            f.close()
            if not settings.TEST and not settings.DEBUG:
                # Remove RAISE NOTICE (/!\ only one-liners)
                sql = re.sub(r"\n.*RAISE NOTICE.*\n", "\n", sql)
                # TODO: this is the ugliest driver hack ever
                sql = sql.replace('%', '%%')

            # Replace curly braces with settings values
            pattern = re.compile(r'{{\s*([^\s]*)\s*}}')
            for m in pattern.finditer(sql):
                value = getattr(settings, m.group(1))
                sql = sql.replace(m.group(0), str(value))

            # Replace sharp braces with schemas
            pattern = re.compile(r'{#\s*([^\s]*)\s*#}')
            for m in pattern.finditer(sql):
                try:
                    value = settings.DATABASE_SCHEMAS[m.group(1)]
                except KeyError:
                    value = settings.DATABASE_SCHEMAS.get('default', 'public')
                sql = sql.replace(m.group(0), str(value))

            cursor.execute(sql)
        except Exception as e:
            logger.critical("Failed to install custom SQL file '%s': %s\n" %
                            (sql_file, e))
            traceback.print_exc()
            raise


def set_search_path():
    # Set search path with all existing schema + new ones
    cursor = connection.cursor()
    cursor.execute('SELECT schema_name FROM information_schema.schemata')
    search_path = set([s[0] for s in cursor.fetchall() if not s[0].startswith('pg_')])
    search_path |= set(settings.DATABASE_SCHEMAS.values())
    search_path.discard('public')
    search_path.discard('information_schema')
    search_path = ('public', ) + tuple(search_path)
    cursor.execute('SET search_path TO {}'.format(', '.join(search_path)))


def move_models_to_schemas(app):
    """
    Move models tables to PostgreSQL schemas.

    Views, functions and triggers will be moved in Geotrek app SQL files.
    """
    default_schema = settings.DATABASE_SCHEMAS.get('default', 'public')
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
        sql = "CREATE SCHEMA IF NOT EXISTS %s;" % model_schema
        cursor.execute(sql)
        logger.info("Created schema %s" % model_schema)

    for schema_name, tables in table_schemas.items():
        for table_name in tables:
            sql = "SELECT 1 FROM information_schema.tables WHERE table_name=%s AND table_schema!=%s"
            cursor.execute(sql, [table_name, schema_name])
            if cursor.fetchone():
                sql = "ALTER TABLE %s SET SCHEMA %s;" % (table_name, schema_name)
                cursor.execute(sql)
                logger.info("Moved %s to schema %s" % (table_name, schema_name))

    # For Django, search_path is set in connection options.
    # But when accessing the database using QGis or ETL, search_path must be
    # set database level (for all users, and for this database only).
    if app.name == 'geotrek.common':
        dbname = settings.DATABASES['default']['NAME']
        dbuser = settings.DATABASES['default']['USER']
        search_path = ', '.join(('public', ) + tuple(set(settings.DATABASE_SCHEMAS.values())))
        sql = "ALTER ROLE %s IN DATABASE %s SET search_path=%s;" % (dbuser, dbname, search_path)
        cursor.execute(sql)
