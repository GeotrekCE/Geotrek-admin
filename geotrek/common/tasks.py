import importlib

import os
from os.path import join
import sys
from celery import Task, shared_task, current_task
from django.contrib.auth.models import User
from django.core.management import call_command
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class GeotrekImportTask(Task):
    '''
    Task destined to define a on_failure callback
    This callback is called upon exception if need be by celery.
     It trigger the final update state and sets the relevant informations
     to be displayed on the web interface.
    '''
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        filename = kwargs.get('filename', '')
        class_name = kwargs.get('name', '')
        self.update_state(
            task_id,
            'FAILURE',
            {
                'exc_type': type(exc).__name__,
                'exc_message': str(exc),
                'filename': filename.split('/').pop(-1),
                'parser': class_name,
                'name': self.name
            }
        )


def get_parser_class(module_name, class_name):
    if module_name == 'parsers':
        module_path = join(settings.VAR_DIR, 'conf/parsers.py')
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        module = importlib.import_module(module_name)

    return getattr(module, class_name)


@shared_task(base=GeotrekImportTask, name='geotrek.common.import-file')
def import_datas(**kwargs):
    class_name = kwargs.get('name')
    filename = kwargs.get('filename')
    module_name = kwargs.get('module')
    encoding = kwargs.get('encoding')
    user_pk = kwargs.get('user', None)

    Parser = get_parser_class(module_name, class_name)

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

    user = user_pk and User.objects.get(pk=user_pk)

    try:
        parser = Parser(progress_cb=progress_cb, user=user, encoding=encoding)
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


@shared_task(base=GeotrekImportTask, name='geotrek.common.import-web')
def import_datas_from_web(**kwargs):
    class_name = kwargs.get('name')
    module_name = kwargs.get('module')
    user_pk = kwargs.get('user', None)

    Parser = get_parser_class(module_name, class_name)

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

    user = user_pk and User.objects.get(pk=user_pk)

    try:
        parser = Parser(progress_cb=progress_cb, user=user)
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


@shared_task(base=GeotrekImportTask, name='geotrek.trekking.sync-rando')
def launch_sync_rando(*args, **kwargs):
    """
    celery shared task - sync rando command
    """

    if not os.path.exists(settings.TMP_DIR):
        os.mkdir(settings.TMP_DIR)
    sync_rando_tmp_dir = os.path.join(settings.TMP_DIR, 'sync_rando')
    if not os.path.exists(sync_rando_tmp_dir):
        os.mkdir(sync_rando_tmp_dir)
    if not os.path.exists(settings.SYNC_RANDO_ROOT):
        os.mkdir(settings.SYNC_RANDO_ROOT)

    print('Sync rando started')

    try:
        current_task.update_state(
            state='PROGRESS',
            meta={
                'name': current_task.name,
                'current': 5,
                'total': 100,
                'infos': "{}".format(_("Init sync ..."))
            }
        )

        sync_rando_options = {
            'url': kwargs.get('url'),
        }
        sync_rando_options.update(settings.SYNC_RANDO_OPTIONS)

        call_command(
            'sync_rando',
            settings.SYNC_RANDO_ROOT,
            verbosity=2,
            task=current_task,
            **sync_rando_options
        )

    except Exception:
        raise

    print('Sync rando ended')

    return {
        'name': current_task.name,
    }
