from django.conf import settings
from modeltranslation.translator import TranslationOptions, translator

from geotrek.flatpages import models as flatpages_models


class FlatPageTO(TranslationOptions):
    fields = (
        "title",
        "content",
    ) + (("published",) if settings.PUBLISHED_BY_LANG else tuple())


translator.register(flatpages_models.FlatPage, FlatPageTO)


class MenuItemTO(TranslationOptions):
    fields = (
        "title",
        "link_url",
    ) + (("published",) if settings.PUBLISHED_BY_LANG else tuple())


translator.register(flatpages_models.MenuItem, MenuItemTO)


class ModalWindowTO(TranslationOptions):
    fields = (
        "name",
        "content",
    ) + (("published",) if settings.PUBLISHED_BY_LANG else tuple())


translator.register(flatpages_models.ModalWindow, ModalWindowTO)


class BannerTO(TranslationOptions):
    fields = (
        "name",
        "content",
    ) + (("published",) if settings.PUBLISHED_BY_LANG else tuple())


translator.register(flatpages_models.Banner, BannerTO)
