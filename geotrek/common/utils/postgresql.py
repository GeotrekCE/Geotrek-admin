import re
import logging
from functools import wraps

from django.db import connection


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
