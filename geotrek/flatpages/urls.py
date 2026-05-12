from django.urls import path

from geotrek.flatpages.views import tinymce_upload

app_name = "flatpages"

urlpatterns = [
    path("tinymce/upload/", tinymce_upload, name="tinymce_upload"),
]
