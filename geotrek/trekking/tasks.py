import os
from django.core.management import call_command
from django.conf import settings
from celery import shared_task, current_task


@shared_task(name='geotrek.trekking.sync-rando')
def launch_sync_rando(*args, **kwargs):
    if not os.path.exists(settings.SYNC_RANDO_ROOT):
        os.mkdir(settings.SYNC_RANDO_ROOT)

    print 'Sync rando started'

    try:
        current_task.update_state(
            state='PROGRESS',
            meta={
                'name': current_task.name
            }
        )
        call_command(
            'sync_rando',
            settings.SYNC_RANDO_ROOT,
            url=kwargs.get('url'),
            verbosity='2'
        )
    except Exception:
        raise

    print 'Sync rando ended'

    return {
        'name': current_task.name
    }
