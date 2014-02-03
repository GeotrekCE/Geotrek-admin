import re
import os
import logging
import traceback
from functools import wraps

from django.db import connection, transaction, models
from django.conf import settings


logger = logging.getLogger(__name__)


def debug_pg_notices(f):

    @wraps(f)
    def wrapped(*args, **kwargs):
        before = len(connection.connection.notices) if connection.connection else 0
        try:
            r = f(*args, **kwargs)
        finally:
            # Show triggers output
            allnotices = []
            current = ''
            if connection.connection:
                notices = []
                for notice in connection.connection.notices[before:]:
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
