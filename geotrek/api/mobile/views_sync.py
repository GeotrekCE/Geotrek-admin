import json
from datetime import timedelta

import redis
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView
from django_celery_results.models import TaskResult

from geotrek.api.mobile.forms import SyncMobileForm
from geotrek.celery import app as celery_app

from .tasks import launch_sync_mobile


class SyncMobileRedirect(RedirectView):
    http_method_names = ["post"]
    pattern_name = "apimobile:sync_mobiles_view"

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request, *args, **kwargs):
        url = "{scheme}://{host}".format(
            scheme="https" if self.request.is_secure() else "http",
            host=self.request.get_host(),
        )
        self.job = launch_sync_mobile.delay(url=url)
        return super().post(request, *args, **kwargs)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def sync_mobile_view(request):
    """
    Custom views to view / track / launch a sync mobile
    """

    return render(
        request,
        "mobile/sync_mobile.html",
        {
            "form": SyncMobileForm(),
        },
    )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def sync_mobile_update_json(request):
    """
    get info from sync_mobile celery_task
    """
    results = []
    threshold = timezone.now() - timedelta(seconds=60)
    for task in TaskResult.objects.filter(date_done__gte=threshold, status="PROGRESS"):
        json_results = json.loads(task.result)

        if json_results.get("name", "").startswith("geotrek.api.mobile"):
            results.append(
                {
                    "id": task.task_id,
                    "result": json_results or {"current": 0, "total": 0},
                    "status": task.status,
                }
            )
    i = celery_app.control.inspect(["celery@geotrek"])
    try:
        reserved = i.reserved()
    except redis.exceptions.ConnectionError:
        reserved = None
    tasks = [] if reserved is None else reversed(reserved["celery@geotrek"])
    for task in tasks:
        if task["name"].startswith("geotrek.api.mobile"):
            results.append(
                {
                    "id": task["id"],
                    "result": {"current": 0, "total": 0},
                    "status": "PENDING",
                }
            )
    for task in TaskResult.objects.filter(
        date_done__gte=threshold, status="FAILURE"
    ).order_by("-date_done"):
        json_results = json.loads(task.result)
        if json_results.get("name", "").startswith("geotrek.api.mobile"):
            results.append(
                {
                    "id": task.task_id,
                    "result": json_results or {"current": 0, "total": 0},
                    "status": task.status,
                }
            )

    return HttpResponse(json.dumps(results), content_type="application/json")
