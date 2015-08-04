from django.core.management import call_command
from celery import shared_task, current_task

@shared_task(name='geotrek.trekking.sync-rando')
def launch_sync_rando(*args, **kwargs):
    print('Sync rando started')
    try:
        current_task.update_state()
        call_command(
            'sync_rando',
            '/tmp/geotest',
            url=kwargs.get('url'),
            verbosity='2'
        )
    except:
        pass
    print('Sync rando ended')

    return 'Sync rando ended'