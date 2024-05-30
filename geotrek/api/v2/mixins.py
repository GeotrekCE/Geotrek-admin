from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from modeltranslation.utils import build_localized_fieldname

from geotrek.common import models as common_models


class PDFSerializerMixin:

    def _get_pdf_url_lang(self, obj, lang, portal=None):
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
            url = f'{request.build_absolute_uri(url)}?portal={portal.split(",")[0]}' \
                if portal else request.build_absolute_uri(url)
        return url

    def get_pdf_url(self, obj):
        lang = self.context.get('request').GET.get('language', 'all') if self.context.get('request') else 'all'
        portal = self.context.get('request').GET.get('portals', None) if self.context.get('request') else None
        if lang != 'all':
            data = self._get_pdf_url_lang(obj, lang, portal)
        else:
            data = {}
            for language in settings.MODELTRANSLATION_LANGUAGES:
                data[language] = self._get_pdf_url_lang(obj, language, portal)
        return data


class PublishedRelatedObjectsSerializerMixin:

    def get_values_on_published_related_objects(self, related_queryset, field):
        """
        Retrieve values for `field` on objects from `related_queryset` only if they are published according to requested language
        """
        request = self.context['request']
        language = request.GET.get('language')
        if language:
            published_by_lang = build_localized_fieldname('published', language)
            return list(related_queryset.filter(**{published_by_lang: True}).values_list(field, flat=True))
        else:
            all_values = []
            for item in related_queryset:
                if getattr(item, "any_published"):
                    all_values.append(getattr(item, field))
        return all_values

    def get_value_on_published_related_object(self, related_object, field):
        """
        Retrieve value for `field` on instance `related_object` only if it is published according to requested language
        """
        value = None
        request = self.context['request']
        language = request.GET.get('language')
        if related_object:
            if language:
                if getattr(related_object, build_localized_fieldname('published', language)):
                    value = getattr(related_object, field)
            else:
                if related_object.published:
                    value = getattr(related_object, field)
        return value
