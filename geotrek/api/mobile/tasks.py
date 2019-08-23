# -*- encoding: UTF-8 -

import os

from celery import shared_task, current_task
from django.conf import settings
from django.core.management import call_command
from django.utils.translation import ugettext as _


@shared_task(name='geotrek.api.mobile.sync-mobile')
def launch_sync_mobile(*args, **kwargs):
    """
    celery shared task - sync mobile command
    """
    if not os.path.exists(settings.SYNC_MOBILE_ROOT):
        os.mkdir(settings.SYNC_MOBILE_ROOT)

    print('Sync mobile started')

    try:
        current_task.update_state(
            state='PROGRESS',
            meta={
                'name': current_task.name,
                'current': 5,
                'total': 100,
                'infos': u"{}".format(_(u"Init sync ..."))
            }
        )
        sync_mobile_options = {
            'url': kwargs.get('url'),
        }
        sync_mobile_options.update(settings.SYNC_MOBILE_OPTIONS)

        call_command(
            'sync_mobile',
            settings.SYNC_MOBILE_ROOT,
            verbosity='2',
            task=current_task,
            **sync_mobile_options
        )

    except Exception:
        raise

    print('Sync mobile ended')

    return {
        'name': current_task.name,
    }
