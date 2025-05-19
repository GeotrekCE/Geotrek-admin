import csv
from io import StringIO
from operator import attrgetter
from unittest.mock import patch

from django.conf import settings
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.files.storage import default_storage
from django.test.utils import override_settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from geotrek.authent.tests.factories import StructureFactory, TrekkingManagerFactory
from geotrek.common.tests import AttachmentImageFactory, CommonTest
from geotrek.tourism.models import TouristicContent, TouristicEvent
from geotrek.zoning.tests.factories import CityFactory

from .factories import (
    TouristicContentCategoryFactory,
    TouristicContentFactory,
    TouristicEventFactory,
    TouristicEventParticipantCategoryFactory,
    TouristicEventParticipantCountFactory,
)


class TouristicContentViewsTests(CommonTest):
    model = TouristicContent
    modelfactory = TouristicContentFactory
    userfactory = TrekkingManagerFactory
    expected_json_geom = {"type": "Point", "coordinates": [-1.3630812, -5.9838563]}
    extra_column_list = ["type1", "type2", "eid"]

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {"id": self.obj.pk, "name": self.obj.name}

    def get_expected_datatables_attrs(self):
        return {
            "category": self.obj.category.label,
            "id": self.obj.pk,
            "name": self.obj.name_display,
        }

    def get_bad_data(self):
        return {"geom": "doh!"}, _("Invalid geometry value.")

    def get_good_data(self):
        return {
            "structure": StructureFactory.create().pk,
            "name_en": "test",
            "category": TouristicContentCategoryFactory.create().pk,
            "geom": '{"type": "Point", "coordinates":[0, 0]}',
        }

    def test_intersection_zoning(self):
        self.modelfactory.create()
        CityFactory.create(
            name="Are",
            code="09000",
            geom=MultiPolygon(
                Polygon(
                    ((0, 0), (300, 0), (300, 100), (200, 100), (0, 0)),
                    srid=settings.SRID,
                )
            ),
        )
        CityFactory.create(
            name="Nor",
            code="09001",
            geom=MultiPolygon(
                Polygon(
                    ((200, 0), (300, 0), (300, 100), (200, 100), (200, 0)),
                    srid=settings.SRID,
                )
            ),
        )
        params = "?city=09000"
        response = self.client.get(self.model.get_datatablelist_url() + params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["recordsFiltered"], 1)
        params = "?city=09001"
        response = self.client.get(self.model.get_datatablelist_url() + params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 0)

    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(
            COLUMNS_LISTS={"touristic_content_view": self.extra_column_list}
        ):
            self.assertEqual(
                import_string(
                    f"geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List"
                )().columns,
                ["id", "name", "type1", "type2", "eid"],
            )

    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(
            COLUMNS_LISTS={"touristic_content_export": self.extra_column_list}
        ):
            self.assertEqual(
                import_string(
                    f"geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList"
                )().columns,
                ["id", "type1", "type2", "eid"],
            )


class TouristicEventViewsTests(CommonTest):
    model = TouristicEvent
    modelfactory = TouristicEventFactory
    userfactory = TrekkingManagerFactory
    expected_json_geom = {"type": "Point", "coordinates": [-1.3630812, -5.9838563]}
    extra_column_list = ["type", "eid", "themes"]

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {"id": self.obj.pk, "name": self.obj.name}

    def get_expected_datatables_attrs(self):
        return {
            "begin_date": "20/02/2002",
            "end_date": "22/02/2202",
            "id": self.obj.pk,
            "name": self.obj.name_display,
            "type": self.obj.type.type,
        }

    def get_bad_data(self):
        return {"geom": "doh!"}, _("Invalid geometry value.")

    def get_good_data(self):
        return {
            "structure": StructureFactory.create().pk,
            "name_en": "test",
            "geom": '{"type": "Point", "coordinates":[0, 0]}',
            "begin_date": "2002-02-20",
            "end_date": "2002-02-20",
        }

    @patch("mapentity.helpers.requests")
    def test_document_export_with_attachment(self, mock_requests):
        obj = self.modelfactory.create()
        attachment = AttachmentImageFactory.create(content_object=obj, title="mapimage")
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = '<p id="properties">Mock</p>'
        response = self.client.get(obj.get_document_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            default_storage.size(obj.get_map_image_path()),
            attachment.attachment_file.size,
        )

    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(
            COLUMNS_LISTS={"touristic_event_view": self.extra_column_list}
        ):
            self.assertEqual(
                import_string(
                    f"geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List"
                )().columns,
                ["id", "name", "type", "eid", "themes"],
            )

    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(
            COLUMNS_LISTS={"touristic_event_export": self.extra_column_list}
        ):
            self.assertEqual(
                import_string(
                    f"geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList"
                )().columns,
                ["id", "type", "eid", "themes"],
            )

    def test_participant_models(self):
        category = TouristicEventParticipantCategoryFactory()
        self.assertEqual(str(category), category.label)

        count = TouristicEventParticipantCountFactory()
        self.assertEqual(str(count), f"{count.count} {count.category}")

    def test_form_with_participant_categories(self):
        category = TouristicEventParticipantCategoryFactory()
        event = self.modelfactory.create()
        response = self.client.get(event.get_update_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, category.label)

    def test_event_with_participant_categories(self):
        categories = TouristicEventParticipantCategoryFactory.create_batch(2)

        data = self.get_good_data()
        data.update(
            {
                f"participant_count_{categories[0].pk}": 10,
            }
        )
        response = self.client.post(self._get_add_url(), data)
        self.assertEqual(response.status_code, 302)
        event = TouristicEvent.objects.last()
        self.assertEqual(event.participants.count(), 1)
        count = event.participants.first()
        self.assertEqual(count.count, 10)
        self.assertEqual(count.category, categories[0])

        data.update(
            {
                f"participant_count_{categories[1].pk}": 20,
            }
        )
        response = self.client.post(event.get_update_url(), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(event.participants.count(), 2)

        data.pop(f"participant_count_{categories[0].pk}")
        response = self.client.post(event.get_update_url(), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(event.participants.count(), 1)
        count = event.participants.first()
        self.assertEqual(count.count, 20)
        self.assertEqual(count.category, categories[1])

    def test_csv_participants_count(self):
        event = self.modelfactory.create()
        counts = TouristicEventParticipantCountFactory.create_batch(2, event=event)
        total_count = sum(map(attrgetter("count"), counts))
        self.assertEqual(event.participants_total, total_count)
        self.assertEqual(
            event.participants_total_verbose_name, "Number of participants"
        )
        with self.assertNumQueries(17):
            response = self.client.get(event.get_format_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get("Content-Type"), "text/csv")
        reader = csv.DictReader(
            StringIO(response.content.decode("utf-8")), delimiter=","
        )
        for row in reader:
            if row["ID"] == event.pk:
                self.assertEqual(row["Number of participants"], total_count)
