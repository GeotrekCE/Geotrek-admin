from django.conf import settings
from django.db.models import Q
from modeltranslation.manager import MultilingualManager
from modeltranslation.utils import build_localized_fieldname

from geotrek.common.mixins.managers import NoDeleteManager, ProviderChoicesMixin


class TouristicContentTypeFilteringManager(MultilingualManager):
    def has_content_published_not_deleted_in_list(self, list_index, category=None, portals=None, language=None):
        """ Retrieves content types for which there exists an event that is published and not deleted in list (type1 or type2)
        """
        i = list_index
        q_total = Q()
        qs = super().get_queryset().filter(in_list=i)
        # Building following logic :
        # return type1 if:
        #            (contents1__portal__in==portals)
        #          & (contents1__category==category)
        #          & (contents1_published_fr | contents1_published_en)
        #          & not(contents1_deleted)
        #
        # q_total  =      q_portal
        #               & q_category
        #               & q_lang
        #               & q_deleted

        q_portal = Q()
        if portals:
            portal_field_name = f"contents{i}__portal__in"
            q_portal = Q(**{portal_field_name: portals})

        q_category = Q()
        if category:
            category_field_name = f"contents{i}__category"
            q_category = Q(**{category_field_name: category})

        if language:
            published_field_name = f"contents{i}__{build_localized_fieldname('published', language)}"
            q_lang = Q(**{published_field_name: True})
        else:
            q_lang = Q()
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                published_field_name = f"contents{i}__{build_localized_fieldname('published', lang)}"
                q_lang |= Q(**{published_field_name: True})

        deleted_field_name = f"contents{i}__deleted"
        q_deleted = Q(**{deleted_field_name: False})

        q_total = q_portal & q_category & q_lang & q_deleted

        return qs.filter(q_total).distinct()


class TouristicContentType1Manager(MultilingualManager):
    def get_queryset(self):
        return super().get_queryset().filter(in_list=1)


class TouristicContentType2Manager(MultilingualManager):
    def get_queryset(self):
        return super().get_queryset().filter(in_list=2)


class TouristicContentManager(NoDeleteManager, ProviderChoicesMixin):
    pass


class TouristicEventManager(NoDeleteManager, ProviderChoicesMixin):
    pass
