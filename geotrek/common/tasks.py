from __future__ import absolute_import

import importlib
import sys
from celery import shared_task, current_task
from django.utils.translation import ugettext as _


@shared_task(name='geotrek.common.import-file')
def import_datas(filename, class_name, module_name="bulkimport.parsers"):
    try:
        module = importlib.import_module(module_name)
        Parser = getattr(module, class_name)
    except:
        raise ImportError("Failed to import parser class '{0}' from module '{1}'".format(
            class_name, module_name))

    def progress_cb(progress, line, eid):
        current_task.update_state(
            state='PROGRESS',
            meta={
                'current': int(100 * progress),
                'total': 100,
                'filename': filename.split('/').pop(-1),
                'parser': class_name,
                'name': current_task.name
            }
        )
        sys.stdout.write(
            "{progress:02d}%".format(progress=int(100 * progress)))

    try:
        parser = Parser(progress_cb=progress_cb)
        parser.parse(filename)
    except Exception as e:
        raise e

    return {
        'current': 100,
        'total': 100,
        'filename': filename.split('/').pop(-1),
        'parser': class_name,
        'report': parser.report(output_format='html').replace('$celery_id', current_task.request.id),
        'name': current_task.name
    }


@shared_task(name='geotrek.common.import-web')
def import_datas_from_web(class_name, module_name="bulkimport.parsers"):
    try:
        module = importlib.import_module(module_name)
        Parser = getattr(module, class_name)
    except:
        raise ImportError("Failed to import parser class '{0}' from module '{1}'".format(
            class_name, module_name))

    def progress_cb(progress, line, eid):
        current_task.update_state(
            state='PROGRESS',
            meta={
                'current': int(100 * progress),
                'total': 100,
                'filename': _("Import from web."),
                'parser': class_name,
                'name': current_task.name
            }
        )
        sys.stdout.write(
            "{progress:02d}%".format(progress=int(100 * progress)))

    try:
        parser = Parser(progress_cb=progress_cb)
        parser.parse()
    except Exception as e:
        raise e

    return {
        'current': 100,
        'total': 100,
        'filename': _("Import from web."),
        'parser': class_name,
        'report': parser.report(output_format='html').replace('$celery_id', current_task.request.id),
        'name': current_task.name
    }
