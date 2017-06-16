import logging
import traceback
from functools import wraps

import os
import re
from django.conf import settings
from django.db import connection, models
from django.db.models import get_app, get_models

logger = logging.getLogger(__name__)


def debug_pg_notices(f):

    @wraps(f)
    def wrapped(*args, **kwargs):
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
                        context = re.sub("\s+", " ", context)
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
                    prefix = '' if context == '' else '        '
                    logger.debug('%s%s' % (prefix, notice.strip()))
        return r

    return wrapped


def load_sql_files(app_label):
    """
    Look for SQL files in Django app, and load them into database.
    We remove RAISE NOTICE instructions from SQL outside unit testing
    since they lead to interpolation errors of '%' character in python.
    """
    app_dir = os.path.dirname(models.get_app(app_label).__file__)
    sql_dir = os.path.normpath(os.path.join(app_dir, 'sql'))
    if not os.path.exists(sql_dir):
        logger.debug("No SQL folder for %s" % app_label)
        return

    r = re.compile(r'^.*\.sql$')
    sql_files = [os.path.join(sql_dir, f)
                 for f in os.listdir(sql_dir)
                 if r.match(f) is not None]
    sql_files.sort()

    if len(sql_files) == 0:
        logger.warning("Empty folder %s" % sql_dir)

    cursor = connection.cursor()
    for sql_file in sql_files:
        try:
            logger.info("Loading initial SQL data from '%s'" % sql_file)
            f = open(sql_file)
            sql = f.read()
            f.close()
            if not settings.TEST:
                # Remove RAISE NOTICE (/!\ only one-liners)
                sql = re.sub(r"\n.*RAISE NOTICE.*\n", "\n", sql)
                # TODO: this is the ugliest driver hack ever
                sql = sql.replace('%', '%%')

            # Replace curly braces with settings values
            pattern = re.compile(r'{{\s*(.*)\s*}}')
            for m in pattern.finditer(sql):
                value = getattr(settings, m.group(1))
                sql = sql.replace(m.group(0), unicode(value))
            cursor.execute(sql)
        except Exception as e:
            logger.critical("Failed to install custom SQL file '%s': %s\n" %
                            (sql_file, e))
            traceback.print_exc()
            raise


def move_models_to_schemas(app_label):
    """
    Move models tables to PostgreSQL schemas.

    Views, functions and triggers will be moved in Geotrek app SQL files.
    """
    app = get_app(app_label)
    default_schema = settings.DATABASE_SCHEMAS.get('default')
    app_schema = settings.DATABASE_SCHEMAS.get(app_label, default_schema)

    table_schemas = {}
    for model in get_models(app):
        model_name = model._meta.model_name
        table_name = model._meta.db_table
        model_schema = settings.DATABASE_SCHEMAS.get(model_name, app_schema)
        table_schemas.setdefault(model_schema, []).append(table_name)

        for m2m_field in model._meta.many_to_many:
            table_name = m2m_field.db_table
            if table_name:
                table_schemas[model_schema].append(table_name)

    cursor = connection.cursor()

    for schema_name in table_schemas.keys():
        try:
            sql = "CREATE SCHEMA %s;" % model_schema
            cursor.execute(sql)
            logger.info("Created schema %s" % model_schema)
        except Exception:
            logger.debug("Schema %s already exists." % model_schema)

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
    if app_label == 'common':
        dbname = settings.DATABASES['default']['NAME']
        dbuser = settings.DATABASES['default']['USER']
        search_path = 'public,%s' % ','.join(set(settings.DATABASE_SCHEMAS.values()))
        sql = "ALTER ROLE %s IN DATABASE %s SET search_path=%s;" % (dbuser, dbname, search_path)
        cursor.execute(sql)
