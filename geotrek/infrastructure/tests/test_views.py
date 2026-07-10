import json

from django.conf import settings
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from mapentity.tests import SuperUserFactory, UserFactory

from geotrek.authent.tests.factories import (
    PathManagerFactory,
    StructureFactory,
    UserProfileFactory,
)
from geotrek.common.tests import (
    CommonMultiActionsViewsPublishedMixin,
    CommonMultiActionViewsMixin,
    CommonMultiActionViewsStructureMixin,
    CommonTest,
)
from geotrek.common.tests.factories import AccessMeanFactory
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
        cls.infrastructure.access = AccessMeanFactory.create()
        cls.infrastructure.save()

        cls.structure = StructureFactory.create()
        cls.type = InfrastructureTypeFactory.create()
        cls.access = AccessMeanFactory.create()
        cls.maintenance_difficulty = (
            InfrastructureMaintenanceDifficultyLevelFactory.create()
        )
        cls.usage_difficulty = InfrastructureUsageDifficultyLevelFactory.create()
        cls.condition_1 = InfrastructureConditionFactory.create()
        cls.condition_2 = InfrastructureConditionFactory.create()

        cls.superuser = SuperUserFactory.create(password="password")
        UserProfileFactory(user=cls.superuser, structure=cls.structure)

        cls.user = UserFactory.create(password="password")
        UserProfileFactory(user=cls.user, structure=cls.structure)
        cls.user.user_permissions.add(
            Permission.objects.get(codename="add_infrastructure")
        )
        cls.user.user_permissions.add(
            Permission.objects.get(codename="change_infrastructure")
        )

        cls.list_url = "/api/infrastructure/drf/infrastructures?format=gtam"
        cls.detail_url = f"/api/infrastructure/drf/infrastructures/{cls.infrastructure.id}?format=gtam"

        cls.foreign_keys = [
            ("type", InfrastructureTypeFactory),
            ("maintenance_difficulty", InfrastructureMaintenanceDifficultyLevelFactory),
            ("usage_difficulty", InfrastructureUsageDifficultyLevelFactory),
        ]

        cls.many_to_many = [
            ("conditions", InfrastructureConditionFactory),
        ]

    def authenticate(self, user):
        r = self.client.post(
            reverse("common:token_obtain_pair"),
            data={"username": user.username, "password": "password"},
        )
        data = r.json()
        return f"Bearer {data['access']}"

    def test_data(self):
        token = self.authenticate(self.superuser)
        response = self.client.get(self.list_url, headers={"Authorization": token})
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
                "geom": {
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
                "access": {
                    "id": self.infrastructure.access.id,
                    "name": self.infrastructure.access.label,
                },
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

    def _get_data(self):
        data = {
            "geom": {
                "type": "Point",
                "coordinates": [6.0, 49.5],
            },
            "published": False,
            "name": "toto",
            "description": "description",
            "implantation_year": 1964,
            "accessibility": "accessible",
            "structure_id": self.structure.id,
            "access_id": self.access.id,
            "type_id": self.type.id,
            "maintenance_difficulty_id": self.maintenance_difficulty.id,
            "usage_difficulty_id": self.usage_difficulty.id,
            "conditions_id": [self.condition_1.id, self.condition_2.id],
        }

        return data

    def _check_data(self, infrastructure_id):
        infrastructure = Infrastructure.objects.get(pk=infrastructure_id)
        self.assertEqual(infrastructure.published, False)
        self.assertEqual(infrastructure.name, "toto")
        self.assertEqual(infrastructure.description, "description")
        self.assertEqual(infrastructure.implantation_year, 1964)
        self.assertEqual(infrastructure.accessibility, "accessible")
        self.assertEqual(infrastructure.structure, self.structure)
        self.assertEqual(infrastructure.access, self.access)
        self.assertEqual(infrastructure.type, self.type)
        self.assertEqual(
            infrastructure.maintenance_difficulty, self.maintenance_difficulty
        )
        self.assertEqual(infrastructure.usage_difficulty, self.usage_difficulty)
        self.assertEqual(
            list(infrastructure.conditions.all()), [self.condition_1, self.condition_2]
        )
        geom = infrastructure.geom
        geom.transform(4326)
        self.assertAlmostEqual(infrastructure.geom.x, 6.0, 2)
        self.assertAlmostEqual(infrastructure.geom.y, 49.5, 2)

    def test_post(self):
        token = self.authenticate(self.superuser)

        response = self.client.post(
            self.list_url,
            json.dumps(self._get_data()),
            content_type="application/json",
            headers={"Authorization": token},
        )
        response_data = response.json()

        self.assertEqual(response.status_code, 201)

        infrastructure_id = response_data["id"]
        self._check_data(infrastructure_id)

    def test_patch(self):
        token = self.authenticate(self.superuser)

        response = self.client.patch(
            self.detail_url,
            json.dumps(self._get_data()),
            content_type="application/json",
            headers={"Authorization": token},
        )

        self.assertEqual(response.status_code, 200)
        self._check_data(self.infrastructure.id)

    def _test_structure_post(self, user):
        token = self.authenticate(user)
        structure = StructureFactory.create()

        data = self._get_data()
        data["structure_id"] = structure.id

        response = self.client.post(
            self.list_url,
            json.dumps(data),
            content_type="application/json",
            headers={"Authorization": token},
        )
        response_data = response.json()

        self.assertEqual(response.status_code, 201)

        infrastructure_id = response_data["id"]
        infrastructure = Infrastructure.objects.get(pk=infrastructure_id)

        return infrastructure, structure

    def _test_structure_patch(self, user):
        token = self.authenticate(user)

        structure = StructureFactory.create()

        response = self.client.patch(
            self.detail_url,
            {"structure_id": structure.id},
            content_type="application/json",
            headers={"Authorization": token},
        )
        self.assertEqual(response.status_code, 200)

        return structure

    def test_structure_as_superuser_post(self):
        infrastructure, structure = self._test_structure_post(self.superuser)
        self.assertEqual(infrastructure.structure, structure)

    def test_structure_as_superuser_patch(self):
        structure = self._test_structure_patch(self.superuser)

        self.infrastructure.refresh_from_db()
        self.assertEqual(self.infrastructure.structure, structure)

    def test_structure_as_user_post(self):
        infrastructure, _ = self._test_structure_post(self.user)
        self.assertEqual(infrastructure.structure, self.user.profile.structure)

    def test_structure_as_user_patch(self):
        self._test_structure_patch(self.user)

        self.infrastructure.refresh_from_db()
        self.assertEqual(self.infrastructure.structure, self.user.profile.structure)

    def _test_foreign_key_structure_post(
        self, user, new_structure=True, status_code=201
    ):
        token = self.authenticate(user)

        structure = (
            StructureFactory.create() if new_structure else user.profile.structure
        )

        data = self._get_data()

        foreign_keys_data = {}
        for attribute, factory in self.foreign_keys:
            foreign_keys_data[attribute] = factory.create(structure=structure)
            data[f"{attribute}_id"] = foreign_keys_data[attribute].id

        many_to_many_data = {}
        for attribute, factory in self.many_to_many:
            many_to_many_data[attribute] = [
                factory.create(structure=structure),
                factory.create(structure=structure),
            ]
            data[f"{attribute}_id"] = [
                instance.id for instance in many_to_many_data[attribute]
            ]

        response = self.client.post(
            self.list_url,
            json.dumps(data),
            content_type="application/json",
            headers={"Authorization": token},
        )
        response_data = response.json()

        self.assertEqual(response.status_code, status_code)

        infrastructure_id = response_data.get("id", None)
        infrastructure = (
            Infrastructure.objects.get(pk=infrastructure_id)
            if infrastructure_id
            else None
        )

        return infrastructure, foreign_keys_data, many_to_many_data, response.json()

    def _test_foreign_key_structure_patch(
        self, user, new_structure=True, status_code=200
    ):
        token = self.authenticate(user)

        structure = (
            StructureFactory.create() if new_structure else user.profile.structure
        )

        data = {}

        foreign_keys_data = {}
        for attribute, factory in self.foreign_keys:
            foreign_keys_data[attribute] = factory.create(structure=structure)
            data[f"{attribute}_id"] = foreign_keys_data[attribute].id

        many_to_many_data = {}
        for attribute, factory in self.many_to_many:
            many_to_many_data[attribute] = [
                factory.create(structure=structure),
                factory.create(structure=structure),
            ]
            data[f"{attribute}_id"] = [
                instance.id for instance in many_to_many_data[attribute]
            ]

        response = self.client.patch(
            self.detail_url,
            json.dumps(data),
            content_type="application/json",
            headers={"Authorization": token},
        )
        self.assertEqual(response.status_code, status_code)

        return foreign_keys_data, many_to_many_data, response.json()

    def test_foreign_key_structure_as_superuser_post(self):
        infrastructure, foreign_keys_data, many_to_many_data, _ = (
            self._test_foreign_key_structure_post(self.superuser)
        )

        for attribute, value in foreign_keys_data.items():
            self.assertEqual(getattr(infrastructure, attribute), value)

        for attribute, value in many_to_many_data.items():
            self.assertEqual(list(getattr(infrastructure, attribute).all()), value)

    def test_foreign_key_structure_as_superuser_patch(self):
        foreign_keys_data, many_to_many_data, _ = (
            self._test_foreign_key_structure_patch(self.superuser)
        )

        self.infrastructure.refresh_from_db()
        for attribute, value in foreign_keys_data.items():
            self.assertEqual(getattr(self.infrastructure, attribute), value)

        for attribute, value in many_to_many_data.items():
            self.assertEqual(list(getattr(self.infrastructure, attribute).all()), value)

    def test_foreign_key_structure_as_user_with_correspondant_structure_post(self):
        """
        User can assign foreign key values if the selected values are related to the user structure
        """
        infrastructure, foreign_keys_data, many_to_many_data, _ = (
            self._test_foreign_key_structure_post(self.user, new_structure=False)
        )

        for attribute, value in foreign_keys_data.items():
            self.assertEqual(getattr(infrastructure, attribute), value)

        for attribute, value in many_to_many_data.items():
            self.assertEqual(list(getattr(infrastructure, attribute).all()), value)

    def test_foreign_key_structure_as_user_with_correspondant_structure_patch(self):
        """
        User can change foreign key values if the selected values are related to the user structure
        """
        foreign_keys_data, many_to_many_data, _ = (
            self._test_foreign_key_structure_patch(self.user, new_structure=False)
        )

        self.infrastructure.refresh_from_db()
        for attribute, value in foreign_keys_data.items():
            self.assertEqual(getattr(self.infrastructure, attribute), value)

        for attribute, value in many_to_many_data.items():
            self.assertEqual(list(getattr(self.infrastructure, attribute).all()), value)

    def test_foreign_key_structure_as_user_without_correspondant_structure_post(self):
        """
        User cannot assign foreign key values if the selected values are not related to the user structure or not related to a structure
        """
        _, fk_data, m2m_data, response_data = self._test_foreign_key_structure_post(
            self.user, status_code=400
        )

        error_msg = {
            "type_id": [f'Invalid pk "{fk_data["type"].id}" - object does not exist.'],
            "maintenance_difficulty_id": [
                f'Invalid pk "{fk_data["maintenance_difficulty"].id}" - object does not exist.'
            ],
            "usage_difficulty_id": [
                f'Invalid pk "{fk_data["usage_difficulty"].id}" - object does not exist.'
            ],
            "conditions_id": [
                f'Invalid pk "{m2m_data["conditions"][0].id}" - object does not exist.'
            ],
        }
        self.assertEqual(response_data, error_msg)

    def test_foreign_key_structure_as_user_without_correspondant_structure_patch(self):
        """
        User cannot change foreign key values if the selected values are not related to the user structure or not related to a structure
        """
        foreign_keys_data = {}
        for attribute, _ in self.foreign_keys:
            foreign_keys_data[attribute] = getattr(self.infrastructure, attribute)

        many_to_many_data = {}
        for attribute, _ in self.many_to_many:
            foreign_keys_data[attribute] = getattr(self.infrastructure, attribute)

        fk_data, m2m_data, response_data = self._test_foreign_key_structure_patch(
            self.user, status_code=400
        )

        error_msg = {
            "type_id": [f'Invalid pk "{fk_data["type"].id}" - object does not exist.'],
            "maintenance_difficulty_id": [
                f'Invalid pk "{fk_data["maintenance_difficulty"].id}" - object does not exist.'
            ],
            "usage_difficulty_id": [
                f'Invalid pk "{fk_data["usage_difficulty"].id}" - object does not exist.'
            ],
            "conditions_id": [
                f'Invalid pk "{m2m_data["conditions"][0].id}" - object does not exist.'
            ],
        }
        self.assertEqual(response_data, error_msg)

        self.infrastructure.refresh_from_db()
        for attribute, value in foreign_keys_data.items():
            self.assertEqual(getattr(self.infrastructure, attribute), value)

        for attribute, value in many_to_many_data.items():
            self.assertEqual(list(getattr(self.infrastructure, attribute).all()), value)
