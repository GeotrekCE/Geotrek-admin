from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from mapentity.tests import SuperUserFactory

from geotrek.authent.tests.factories import PathManagerFactory, UserProfileFactory
from geotrek.common.tests import (
    CommonMultiActionsViewsPublishedMixin,
    CommonMultiActionViewsMixin,
    CommonMultiActionViewsStructureMixin,
    CommonTest,
)
from geotrek.core.tests.factories import PathFactory
from geotrek.infrastructure.models import (
    Infrastructure,
    InfrastructureCondition,
    InfrastructureMaintenanceDifficultyLevel,
    InfrastructureType,
    InfrastructureTypeChoices,
    InfrastructureUsageDifficultyLevel,
)
from geotrek.infrastructure.tests.factories import (
    InfrastructureConditionFactory,
    InfrastructureFactory,
    InfrastructureMaintenanceDifficultyLevelFactory,
    InfrastructureTypeFactory,
    InfrastructureUsageDifficultyLevelFactory,
    PointInfrastructureFactory,
)


class InfrastructureViewsTest(CommonTest):
    model = Infrastructure
    modelfactory = InfrastructureFactory
    userfactory = PathManagerFactory
    expected_json_geom = {
        "type": "LineString",
        "coordinates": [[3.0, 46.5], [3.001304, 46.5009004]],
    }
    extra_column_list = ["type", "eid"]
    expected_column_list_extra = ["id", "name", "type", "eid"]
    expected_column_formatlist_extra = ["id", "type", "eid"]

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            "id": self.obj.pk,
            "name": self.obj.name,
            "published": self.obj.published,
        }

    def get_expected_datatables_attrs(self):
        return {
            "cities": "",
            "conditions": self.obj.conditions_display,
            "id": self.obj.pk,
            "name": self.obj.name_display,
            "type": self.obj.type.label,
        }

    def get_good_data(self):
        good_data = {
            "name_fr": "test",
            "name_en": "test_en",
            "description": "oh",
            "type": InfrastructureTypeFactory.create(
                type=InfrastructureTypeChoices.BUILDING
            ).pk,
            "conditions": [InfrastructureConditionFactory.create().pk],
            "accessibility": "description accessibility",
        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create()
            good_data["topology"] = f'{{"paths": [{path.pk}]}}'
        else:
            good_data["geom"] = "LINESTRING (0.0 0.0, 1.0 1.0)"
        return good_data

    def get_expected_popup_content(self):
        return (
            f'<div class="d-flex flex-column justify-content-center">\n'
            f'    <p class="text-center m-0 p-1"><strong>{str(self.obj)}</strong></p>\n    \n'
            f'        <p class="m-0 p-1">\n'
            f"            {str(self.obj.type)}<br>\n"
            f"        </p>\n    \n"
            f'    <a id="detail-btn" href="/infrastructure/{self.obj.pk}/" class="btn btn-sm btn-info mt-2">Detail sheet</a>\n'
            f"</div>"
        )

    def test_description_in_detail_page(self):
        infra = InfrastructureFactory.create(description="<b>Beautiful !</b>")
        response = self.client.get(infra.get_detail_url())
        self.assertContains(response, "<b>Beautiful !</b>")

    def test_check_structure_or_none_related_are_visible(self):
        infratype = InfrastructureTypeFactory.create(
            type=InfrastructureTypeChoices.BUILDING, structure=None
        )
        response = self.client.get(self.model.get_add_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
        form = response.context["form"]
        type = form.fields["type"]
        self.assertTrue((infratype.pk, str(infratype)) in type.choices)


class PointInfrastructureViewsTest(InfrastructureViewsTest):
    modelfactory = PointInfrastructureFactory
    expected_json_geom = {"type": "Point", "coordinates": [3.0, 46.5]}
    extra_column_list = ["type", "eid"]
    expected_column_list_extra = ["id", "name", "type", "eid"]
    expected_column_formatlist_extra = ["id", "type", "eid"]

    def get_good_data(self):
        good_data = {
            "accessibility": "description accessibility",
            "name_fr": "test",
            "name_en": "test_en",
            "description": "oh",
            "type": InfrastructureTypeFactory.create(
                type=InfrastructureTypeChoices.BUILDING
            ).pk,
            "conditions": [InfrastructureConditionFactory.create().pk],
        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create()
            good_data["topology"] = f'{{"paths": [{path.pk}]}}'
        else:
            good_data["geom"] = "POINT(0.42 0.666)"
        return good_data

    def get_expected_popup_content(self):
        return (
            f'<div class="d-flex flex-column justify-content-center">\n'
            f'    <p class="text-center m-0 p-1"><strong>{str(self.obj)}</strong></p>\n    \n'
            f'        <p class="m-0 p-1">\n'
            f"            {str(self.obj.type)}<br>\n"
            f"        </p>\n    \n"
            f'    <a id="detail-btn" href="/infrastructure/{self.obj.pk}/" class="btn btn-sm btn-info mt-2">Detail sheet</a>\n'
            f"</div>"
        )


class InfrastructureMultiActionsViewTest(
    CommonMultiActionsViewsPublishedMixin,
    CommonMultiActionViewsStructureMixin,
    CommonMultiActionViewsMixin,
    TestCase,
):
    model = Infrastructure
    modelFactory = InfrastructureFactory
    expected_fields = [
        "Published [fr]",
        "Published [en]",
        "Provider",
        "Related structure",
        "Access mean",
        "Type",
        "Maintenance difficulty",
        "Usage difficulty",
    ]


class InfrastructureReferencesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.type = InfrastructureTypeFactory.create()
        cls.maintenance_difficulty_level = (
            InfrastructureMaintenanceDifficultyLevelFactory.create()
        )
        cls.usage_difficulty_level = InfrastructureUsageDifficultyLevelFactory.create()
        cls.conditions = InfrastructureConditionFactory.create()
        cls.user = SuperUserFactory.create(password="password")
        UserProfileFactory(user=cls.user)

    def authenticate(self, user):
        r = self.client.post(
            reverse("common:token_obtain_pair"),
            data={"username": user.username, "password": "password"},
        )
        data = r.json()
        return f"Bearer {data['access']}"

    def test_data(self):
        token = self.authenticate(self.user)
        r = self.client.get(
            reverse("infrastructure:infrastructure_references"),
            headers={"Authorization": token},
        )
        data = r.json()

        self.assertEqual(
            len(data["infrastructuretype"]), InfrastructureType.objects.all().count()
        )
        self.assertEqual(
            len(data["infrastructuremaintenancedifficultylevel"]),
            InfrastructureMaintenanceDifficultyLevel.objects.all().count(),
        )
        self.assertEqual(
            len(data["infrastructureusagedifficultylevel"]),
            InfrastructureUsageDifficultyLevel.objects.all().count(),
        )
        self.assertEqual(
            len(data["infrastructurecondition"]),
            InfrastructureCondition.objects.all().count(),
        )
        self.assertEqual(
            data["infrastructuretype"][0], {"id": self.type.id, "name": self.type.label}
        )
        self.assertEqual(
            data["infrastructuremaintenancedifficultylevel"][0],
            {
                "id": self.maintenance_difficulty_level.id,
                "name": self.maintenance_difficulty_level.label,
            },
        )
        self.assertEqual(
            data["infrastructureusagedifficultylevel"][0],
            {
                "id": self.usage_difficulty_level.id,
                "name": self.usage_difficulty_level.label,
            },
        )
        self.assertEqual(
            data["infrastructurecondition"][0],
            {"id": self.conditions.id, "name": self.conditions.label},
        )
        self.assertEqual(
            data["pictogram"],
            {"url": "http://testserver/static/images/infrastructure.png"},
        )


class InfrastructureGTAMTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.infrastructure = InfrastructureFactory.create()

        cls.user = SuperUserFactory.create(password="password")
        UserProfileFactory(user=cls.user)

    def authenticate(self, user):
        r = self.client.post(
            reverse("common:token_obtain_pair"),
            data={"username": user.username, "password": "password"},
        )
        data = r.json()
        return f"Bearer {data['access']}"

    def test_data(self):
        token = self.authenticate(self.user)
        list_url = "/api/infrastructure/drf/infrastructures?format=gtam"
        response = self.client.get(list_url, headers={"Authorization": token})
        data = response.json()

        infrastructures = [
            {
                "id": self.infrastructure.id,
                "date_insert": self.infrastructure.date_insert.isoformat().replace(
                    "+00:00", "Z"
                ),
                "date_update": self.infrastructure.date_update.isoformat().replace(
                    "+00:00", "Z"
                ),
                "api_geom": {
                    "type": "LineString",
                    "coordinates": [[3.0, 46.5], [3.001304, 46.5009004]],
                },
                "published": self.infrastructure.published,
                "name": self.infrastructure.name,
                "description": self.infrastructure.description,
                "implantation_year": self.infrastructure.implantation_year,
                "accessibility": self.infrastructure.accessibility,
                "structure": {
                    "id": self.infrastructure.structure.id,
                    "name": self.infrastructure.structure.name,
                },
                "access": self.infrastructure.access,
                "type": {
                    "id": self.infrastructure.type.id,
                    "name": self.infrastructure.type.label,
                },
                "maintenance_difficulty": {
                    "id": self.infrastructure.maintenance_difficulty.id,
                    "name": self.infrastructure.maintenance_difficulty.label,
                },
                "usage_difficulty": {
                    "id": self.infrastructure.usage_difficulty.id,
                    "name": self.infrastructure.usage_difficulty.label,
                },
                "conditions": [],
            }
        ]
        self.assertEqual(data, infrastructures)
