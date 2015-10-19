# -*- encoding: UTF-8 -

import os

from celery import shared_task, current_task
from django.conf import settings
from django.core.management import call_command


@shared_task(name='geotrek.trekking.sync-rando')
def launch_sync_rando(*args, **kwargs):
    """
    celery shared task - sync rando command
    """
    if not os.path.exists(settings.SYNC_RANDO_ROOT):
        os.mkdir(settings.SYNC_RANDO_ROOT)

    print 'Sync rando started'

    try:
        current_task.update_state(
            state='PROGRESS',
            meta={
                'name': current_task.name,
            }
        )

        call_command(
            'sync_rando',
            settings.SYNC_RANDO_ROOT,
            url=kwargs.get('url'),
            verbosity='2',
            skip_profile_png=True,
        )

    except Exception:
        raise

    print 'Sync rando ended'

    return {
        'name': current_task.name,
    }
