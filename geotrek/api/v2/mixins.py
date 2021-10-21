from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import serializers

from geotrek.api.v2.utils import build_url
from geotrek.common import models as common_models


class PDFSerializerMixin:

    def _get_pdf_url_lang(self, obj, lang):
        namespace = self.Meta.model._meta.app_label
        modelname = self.Meta.model._meta.object_name.lower()
        if settings.ONLY_EXTERNAL_PUBLIC_PDF:
            file_type = get_object_or_404(common_models.FileType, type="Topoguide")
            if not common_models.Attachment.objects.attachments_for_object_only_type(obj, file_type).exists():
                return None
        urlname = '{}:{}_{}printable'.format(namespace, modelname, 'booklet_' if settings.USE_BOOKLET_PDF else '')
        url = reverse(urlname, kwargs={'lang': lang, 'pk': obj.pk, 'slug': obj.slug})
        request = self.context.get('request')
        if request:
            url = request.build_absolute_uri(url)
        return url

    def get_pdf_url(self, obj):
        lang = self.context.get('request').GET.get('language', 'all') if self.context.get('request') else 'all'
        if lang != 'all':
            data = self._get_pdf_url_lang(obj, lang)
        else:
            data = {}
            for language in settings.MODELTRANSLATION_LANGUAGES:
                data[language] = self._get_pdf_url_lang(obj, language)
        return data
