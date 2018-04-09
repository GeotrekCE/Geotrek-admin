# -*- encoding: UTF-8 -

import os

from celery import shared_task, current_task
from django.conf import settings
from django.core.management import call_command
from django.utils.translation import ugettext as _


@shared_task(name='geotrek.trekking.sync-rando')
def launch_sync_rando(*args, **kwargs):
    """
    celery shared task - sync rando command
    """
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
            verbosity='2',
            task=current_task,
            **sync_rando_options
        )

    except Exception:
        raise

    print('Sync rando ended')

    return {
        'name': current_task.name,
    }
