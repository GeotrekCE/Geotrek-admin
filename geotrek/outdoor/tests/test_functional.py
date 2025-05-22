from django.test.utils import override_settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from geotrek.authent.tests.factories import StructureFactory
from geotrek.common.tests import CommonTest
from geotrek.outdoor.models import Course, Site
from geotrek.outdoor.tests.factories import (
    CourseFactory,
    OutdoorManagerFactory,
    SiteFactory,
)


class SiteViewsTests(CommonTest):
    model = Site
    modelfactory = SiteFactory
    userfactory = OutdoorManagerFactory
    expected_json_geom = {
        "type": "GeometryCollection",
        "geometries": [{"type": "Point", "coordinates": [-1.3630812, -5.9838563]}],
    }
    extra_column_list = ["orientation", "ratings", "period"]

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {"id": self.obj.pk, "name": self.obj.name}

    def get_bad_data(self):
        return {"geom": "doh!"}, _("Invalid geometry value.")

    def get_good_data(self):
        return {
            "structure": StructureFactory.create().pk,
            "name_en": "test en",
            "name_fr": "test fr",
            "geom": '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates":[0, 0]}]}',
        }

    def get_expected_datatables_attrs(self):
        return {
            "date_update": "17/03/2020 00:00:00",
            "id": self.obj.pk,
            "name": self.obj.name_display,
            "super_practices": self.obj.super_practices_display,
        }

    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(
            COLUMNS_LISTS={
                f"outdoor_{self.model._meta.model_name}_view": self.extra_column_list
            }
        ):
            self.assertEqual(
                import_string(
                    f"geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List"
                )().columns,
                ["id", "name", "orientation", "ratings", "period"],
            )

    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(
            COLUMNS_LISTS={
                f"outdoor_{self.model._meta.model_name}_export": self.extra_column_list
            }
        ):
            self.assertEqual(
                import_string(
                    f"geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList"
                )().columns,
                ["id", "orientation", "ratings", "period"],
            )


class CourseViewsTests(CommonTest):
    model = Course
    modelfactory = CourseFactory
    userfactory = OutdoorManagerFactory
    expected_json_geom = {
        "type": "GeometryCollection",
        "geometries": [{"type": "Point", "coordinates": [-1.3630812, -5.9838563]}],
    }
    extra_column_list = ["equipment", "ratings", "eid"]

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {"id": self.obj.pk, "name": self.obj.name}

    def get_expected_datatables_attrs(self):
        return {
            "date_update": "17/03/2020 00:00:00",
            "id": self.obj.pk,
            "name": self.obj.name_display,
            "parent_sites": self.obj.parent_sites_display,
        }

    def get_bad_data(self):
        return {"geom": "doh!"}, _("Invalid geometry value.")

    def get_good_data(self):
        return {
            "structure": StructureFactory.create().pk,
            "parent_sites": [SiteFactory.create().pk],
            "name_en": "test en",
            "name_fr": "test fr",
            "geom": '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates":[0, 0]}]}',
        }

    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(
            COLUMNS_LISTS={
                f"outdoor_{self.model._meta.model_name}_view": self.extra_column_list
            }
        ):
            self.assertEqual(
                import_string(
                    f"geotrek.{self.model._meta.app_label}.views.{self.model.__name__}List"
                )().columns,
                ["id", "name", "equipment", "ratings", "eid"],
            )

    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatory columns plus custom extra columns
        if self.model is None:
            return
        with override_settings(
            COLUMNS_LISTS={
                f"outdoor_{self.model._meta.model_name}_export": self.extra_column_list
            }
        ):
            self.assertEqual(
                import_string(
                    f"geotrek.{self.model._meta.app_label}.views.{self.model.__name__}FormatList"
                )().columns,
                ["id", "equipment", "ratings", "eid"],
            )
