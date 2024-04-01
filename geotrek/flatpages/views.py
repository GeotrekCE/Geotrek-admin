from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@require_http_methods(["POST"])
@csrf_exempt
@login_required
def tinymce_upload(request):
    file = request.FILES.get('file')
    filename = f"flatpages/content/upload/{uuid4()}/{str(file)}"
    default_storage.save(filename, file)
    return JsonResponse({"location": request.build_absolute_uri(default_storage.url(filename))})
