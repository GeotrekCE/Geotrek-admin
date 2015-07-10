from __future__ import absolute_import
from time import sleep

import importlib
import sys
from celery import shared_task, current_task


@shared_task
def import_datas(filename, class_name, module_name="bulkimport.parsers"):
    try:
        module = importlib.import_module(module_name)
        Parser = getattr(module, class_name)
    except:
        raise Exception("Failed to import parser class '{0}' from module '{1}".format(class_name, module_name))

    def progress_cb(progress):
        current_task.update_state(
            state='PROGRESS',
            meta={
                'current': int(100*progress),
                'total': 100,
            }
        )
        sys.stdout.write("{progress:02d}%".format(progress=int(100 * progress)))

    try:
        parser = Parser(progress_cb=progress_cb)
        parser.parse(filename)
    except Exception as e:
        raise e
    
    return
