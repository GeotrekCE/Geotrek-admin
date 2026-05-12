from django.test import TestCase
from django.utils.translation import gettext_lazy as _
from mapentity.tests.factories import SuperUserFactory

from geotrek.authent.tests.factories import StructureFactory
from geotrek.common.tests import (
    CommonLiveTest,
    CommonMultiActionsViewsPublishedMixin,
    CommonMultiActionViewsMixin,
    CommonMultiActionViewsStructureMixin,
    CommonTest,
)

from ..models import Dive
from .factories import (
    DiveFactory,
    DiveWithLevelsFactory,
    DivingManagerFactory,
    PracticeFactory,
)


class DiveViewsTests(CommonTest):
    model = Dive
    modelfactory = DiveWithLevelsFactory
    userfactory = DivingManagerFactory
    expected_json_geom = {
        "type": "Point",
        "coordinates": [-1.3630812, -5.9838563],
    }
    extra_column_list = ["depth", "advice"]
    expected_column_list_extra = ["id", "name", "depth", "advice"]
    expected_column_formatlist_extra = ["id", "depth", "advice"]

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            "id": self.obj.pk,
            "name": self.obj.name,
            "published": True,
        }

    def get_expected_datatables_attrs(self):
        return {
            "id": self.obj.pk,
            "levels": self.obj.levels_display,
            "name": self.obj.name_display,
            "thumbnail": "None",
        }

    def get_bad_data(self):
        return {"geom": "doh!"}, _("Invalid geometry value.")

    def get_good_data(self):
        return {
            "structure": StructureFactory.create().pk,
            "name_en": "test",
            "practice": PracticeFactory.create().pk,
            "geom": '{"type": "Point", "coordinates":[0, 0]}',
        }

    def get_expected_popup_content(self):
        return (
            f'<div class="d-flex flex-column justify-content-center">\n'
            f'    <p class="text-center m-0 p-1"><strong>{str(self.obj)}</strong></p>\n    \n'
            f'        <p class="m-0 p-1">\n'
            f"            {str(self.obj.practice)}<br>\n"
            f"        </p>\n    \n"
            f'    <button id="detail-btn" class="btn btn-sm btn-info mt-2" onclick="window.location.href=\'/dive/{self.obj.pk}/\'">Detail sheet</button>\n'
            f"</div>"
        )


class DiveViewsLiveTests(CommonLiveTest):
    model = Dive
    modelfactory = DiveFactory
    userfactory = SuperUserFactory


class DiveMultiActionsViewTest(
    CommonMultiActionsViewsPublishedMixin,
    CommonMultiActionViewsStructureMixin,
    CommonMultiActionViewsMixin,
    TestCase,
):
    model = Dive
    modelFactory = DiveFactory
    expected_fields = [
        "Published [fr]",
        "Published [en]",
        "Waiting for publication",
        "Related structure",
        "Practice",
        "Difficulty level",
    ]
