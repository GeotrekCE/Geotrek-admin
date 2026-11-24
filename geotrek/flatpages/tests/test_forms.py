from django.conf import settings
from django.forms import modelform_factory
from django.test import TestCase, override_settings
from modeltranslation.utils import build_localized_fieldname

from geotrek.common.tests.factories import TargetPortalFactory
from geotrek.flatpages.forms import BannerForm, ModalWindowForm
from geotrek.flatpages.tests.factories import BannerFactory, ModalWindowFactory


class UniquePublicationPerPortalFormTestMixin:
    """Tests for forms using `UniquePublicationPerPortalFormMixin`.

    Concrete classes must define `form_class`, `factory`, `conflict_message` and
    `content_message`. Run them with `@override_settings(PUBLISHED_BY_LANG=...)` to test both
    publication modes.
    """

    form_class = None
    factory = None
    conflict_message = None
    content_message = None

    @classmethod
    def setUpTestData(cls):
        cls.portal = TargetPortalFactory.create(name="Portal A")
        cls.other_portal = TargetPortalFactory.create(name="Portal B")

    @property
    def model(self):
        return self.form_class._meta.model

    def get_form(self, portals, published_langs=(), instance=None, content_langs=None):
        """Builds a bound form. `content_langs` lists the languages in which a content is given
        (all languages by default)."""
        if content_langs is None:
            content_langs = settings.MODELTRANSLATION_LANGUAGES
        if settings.PUBLISHED_BY_LANG:
            published_fields = [
                build_localized_fieldname("published", lang) for lang in published_langs
            ]
        else:
            published_fields = ["published"]
        content_fields = [
            build_localized_fieldname("content", lang) for lang in content_langs
        ]
        form_class = modelform_factory(
            self.model,
            form=self.form_class,
            fields=["name", "portals", *content_fields, *published_fields],
        )
        data = {
            "name": "New object",
            "portals": [portal.pk for portal in portals],
        }
        data.update({field: "<p>Content</p>" for field in content_fields})
        data.update(self.published_data(*published_langs))
        return form_class(data=data, instance=instance)

    def published_data(self, *langs):
        """Form data to publish in the given languages. When PUBLISHED_BY_LANG is False, any
        language means published."""
        if not langs:
            return {}
        if settings.PUBLISHED_BY_LANG:
            return {
                build_localized_fieldname("published", lang): True for lang in langs
            }
        return {"published": True}

    def create_published(self, langs=("en",), **kwargs):
        """Creates an object published in the given languages (or simply published when
        PUBLISHED_BY_LANG is False)."""
        if settings.PUBLISHED_BY_LANG:
            for lang in langs:
                kwargs[build_localized_fieldname("published", lang)] = True
        else:
            kwargs["published"] = True
        return self.factory(**kwargs)

    def assertConflict(self, form, *conflicts):
        self.assertFalse(form.is_valid())
        error = form.non_field_errors()[0]
        self.assertTrue(error.startswith(self.conflict_message), error)
        for conflict in conflicts:
            self.assertIn(conflict, error)

    def test_cannot_publish_on_portal_with_published_object(self):
        self.create_published(name="Existing", portals=[self.portal])
        form = self.get_form([self.portal, self.other_portal], published_langs=["en"])
        self.assertConflict(form, "Existing (Portal A)")

    def test_cannot_publish_without_portal_if_object_without_portal_published(self):
        self.create_published(name="Existing")
        form = self.get_form([], published_langs=["en"])
        self.assertConflict(form, "Existing (no portal)")

    def test_can_publish_on_portal_without_published_object(self):
        self.create_published(portals=[self.other_portal])
        form = self.get_form([self.portal], published_langs=["en"])
        self.assertTrue(form.is_valid(), form.errors)

    def test_can_publish_without_portal_if_existing_object_has_portal(self):
        self.create_published(portals=[self.portal])
        form = self.get_form([], published_langs=["en"])
        self.assertTrue(form.is_valid(), form.errors)

    def test_can_publish_on_portal_with_unpublished_object(self):
        self.factory(portals=[self.portal])
        form = self.get_form([self.portal], published_langs=["en"])
        self.assertTrue(form.is_valid(), form.errors)

    def test_can_save_unpublished_object_on_portal_with_published_object(self):
        self.create_published(portals=[self.portal])
        form = self.get_form([self.portal])
        self.assertTrue(form.is_valid(), form.errors)

    def test_can_update_already_published_object(self):
        obj = self.create_published(portals=[self.portal])
        form = self.get_form([self.portal], published_langs=["en"], instance=obj)
        self.assertTrue(form.is_valid(), form.errors)

        form.save()
        obj.refresh_from_db()
        self.assertEqual(obj.name, "New object")

    def test_can_publish_in_another_language(self):
        if not settings.PUBLISHED_BY_LANG:
            self.skipTest("Only relevant when PUBLISHED_BY_LANG is True")

        self.create_published(langs=["fr"], portals=[self.portal])
        form = self.get_form([self.portal], published_langs=["en"])
        self.assertTrue(form.is_valid(), form.errors)

    def test_cannot_publish_in_same_language_among_several(self):
        if not settings.PUBLISHED_BY_LANG:
            self.skipTest("Only relevant when PUBLISHED_BY_LANG is True")

        self.create_published(name="Existing", langs=["fr"], portals=[self.portal])
        form = self.get_form([self.portal], published_langs=["en", "fr"])
        self.assertConflict(form, "Existing (Portal A)")

    def test_cannot_publish_in_a_language_without_content(self):
        if not settings.PUBLISHED_BY_LANG:
            self.skipTest("Only relevant when PUBLISHED_BY_LANG is True")

        form = self.get_form(
            [self.portal], published_langs=["en"], content_langs=["fr"]
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), [self.content_message % {"lang": "en"}]
        )

    def test_can_publish_in_a_language_with_content(self):
        if not settings.PUBLISHED_BY_LANG:
            self.skipTest("Only relevant when PUBLISHED_BY_LANG is True")

        form = self.get_form(
            [self.portal], published_langs=["en", "fr"], content_langs=["en", "fr"]
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_can_save_unpublished_object_without_content(self):
        form = self.get_form([self.portal], content_langs=[])
        self.assertTrue(form.is_valid(), form.errors)


class ModalWindowFormMixin:
    form_class = ModalWindowForm
    factory = ModalWindowFactory
    conflict_message = (
        "Each platform (rando, widget, mobile instance) can only have one modal window. "
        "The following modal windows are already published on the selected platforms: "
    )
    content_message = "The modal window is published in language '%(lang)s' but no content is given in this language."


class BannerFormMixin:
    form_class = BannerForm
    factory = BannerFactory
    conflict_message = (
        "Each platform (rando, widget, mobile instance) can only have one banner. "
        "The following banners are already published on the selected platforms: "
    )
    content_message = "The banner is published in language '%(lang)s' but no content is given in this language."


@override_settings(PUBLISHED_BY_LANG=True)
class ModalWindowFormPublishedByLangTest(
    ModalWindowFormMixin, UniquePublicationPerPortalFormTestMixin, TestCase
):
    pass


@override_settings(PUBLISHED_BY_LANG=False)
class ModalWindowFormNotPublishedByLangTest(
    ModalWindowFormMixin, UniquePublicationPerPortalFormTestMixin, TestCase
):
    pass


@override_settings(PUBLISHED_BY_LANG=True)
class BannerFormPublishedByLangTest(
    BannerFormMixin, UniquePublicationPerPortalFormTestMixin, TestCase
):
    pass


@override_settings(PUBLISHED_BY_LANG=False)
class BannerFormNotPublishedByLangTest(
    BannerFormMixin, UniquePublicationPerPortalFormTestMixin, TestCase
):
    pass
