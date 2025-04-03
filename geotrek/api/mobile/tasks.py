import os

from celery import current_task, shared_task
from django.conf import settings
from django.core.management import call_command
from django.utils.translation import gettext as _

from geotrek.common.tasks import GeotrekImportTask


@shared_task(base=GeotrekImportTask, name="geotrek.api.mobile.sync-mobile")
def launch_sync_mobile(*args, **kwargs):
    """
    celery shared task - sync mobile command
    """
    if not os.path.exists(settings.SYNC_MOBILE_ROOT):
        os.mkdir(settings.SYNC_MOBILE_ROOT)

    print("Sync mobile started")

    try:
        current_task.update_state(
            state="PROGRESS",
            meta={
                "name": current_task.name,
                "current": 5,
                "total": 100,
                "infos": _("Init sync ..."),
            },
        )
        sync_mobile_options = {
            "url": kwargs.get("url"),
        }
        sync_mobile_options.update(settings.SYNC_MOBILE_OPTIONS)
        call_command(
            "sync_mobile",
            settings.SYNC_MOBILE_ROOT,
            verbosity=2,
            task=current_task,
            **sync_mobile_options,
        )

    except Exception:
        raise

    print("Sync mobile ended")

    return {
        "name": current_task.name,
    }
