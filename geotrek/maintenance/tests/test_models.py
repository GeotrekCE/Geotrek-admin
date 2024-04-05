from unittest import skipIf

from django.conf import settings
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import LineString, Point
from django.test import TestCase
from django.utils import translation

from geotrek.core.tests.factories import (PathFactory, StakeFactory,
                                          TopologyFactory, TrailFactory)
from geotrek.infrastructure.models import Infrastructure
from geotrek.infrastructure.tests.factories import InfrastructureFactory
from geotrek.maintenance.models import Funding, Intervention, ManDay
from geotrek.maintenance.tests.factories import (
    FundingFactory, InfrastructureInterventionFactory,
    InfrastructurePointInterventionFactory, InterventionDisorderFactory,
    InterventionFactory, InterventionJobFactory, ManDayFactory, ProjectFactory,
    SignageInterventionFactory, ContractorFactory)
from geotrek.outdoor.tests.factories import CourseFactory, SiteFactory
from geotrek.signage.tests.factories import BladeFactory, SignageFactory


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class InterventionTest(TestCase):
    def test_topology_has_intervention_kind(self):
        topo = TopologyFactory.create()
        self.assertEqual('TOPOLOGY', topo.kind)
        i = InterventionFactory.create(target_id=topo.pk)
        self.assertEqual('TOPOLOGY', i.target.kind)

    def test_default_stake(self):
        # Add paths to topology
        infra = InfrastructureFactory.create(paths=[])
        i = InterventionFactory.create(target=infra)
        i.stake = None
        self.assertTrue(i.stake is None)
        i.save()
        self.assertTrue(i.stake is None)

        lowstake = StakeFactory.create()
        highstake = StakeFactory.create()
        if lowstake > highstake:
            tmp = lowstake
            lowstake = highstake
            highstake = tmp

        # Add paths to topology
        infra.add_path(PathFactory.create(stake=lowstake))
        infra.add_path(PathFactory.create(stake=highstake))
        infra.add_path(PathFactory.create(stake=lowstake))
        # Stake is not None anymore
        i.save()
        self.assertFalse(i.stake is None)
        # Make sure it took higher stake
        self.assertEqual(i.stake, highstake)

    def test_mandays(self):
        i = InterventionFactory.create()
        md = ManDayFactory.create(intervention=i, nb_days=5)
        ManDayFactory.create(intervention=i, nb_days=8)
        self.assertEqual(i.total_manday, 14)  # intervention haz a default manday
        manday_pk = md.pk
        interv_pk = i.pk
        obj_repr = str(i)
        i.delete(force=True)
        model_num = ContentType.objects.get_for_model(ManDay).pk
        entry = LogEntry.objects.get(content_type=model_num, object_id=manday_pk)
        self.assertEqual(entry.change_message, f"Deleted by cascade from Intervention {interv_pk} - {obj_repr}")
        self.assertEqual(entry.action_flag, DELETION)

    def test_path_helpers(self):
        p = PathFactory.create()

        self.assertEqual(len(p.interventions), 0)
        self.assertEqual(len(p.projects), 0)

        sign = SignageFactory.create(paths=[p])

        infra = InfrastructureFactory.create(paths=[p])

        i1 = InterventionFactory.create(target=sign)

        self.assertCountEqual(p.interventions, [i1])

        i2 = InterventionFactory.create(target=infra)

        self.assertCountEqual(p.interventions, [i1, i2])

        proj = ProjectFactory.create()
        proj.interventions.add(i1)
        proj.interventions.add(i2)

        self.assertCountEqual(p.projects, [proj])

    def test_trails_property(self):
        p = PathFactory.create()
        TrailFactory.create(paths=[p], name='trail_1')
        TrailFactory.create(paths=[p], name='trail_2')
        infra = InfrastructureFactory.create(paths=[p])
        intervention = InterventionFactory.create(target=infra)
        self.assertQuerysetEqual(intervention.trails, ['trail_1', 'trail_2'], ordered=False, transform=str)

    def test_paths_property(self):
        p_infra = PathFactory.create(geom=LineString((0, 0), (0, 10)))
        infra = InfrastructureFactory.create(paths=[p_infra])
        intervention_infra = InterventionFactory.create(target=infra)
        self.assertQuerysetEqual(intervention_infra.paths, [p_infra.name, ], transform=str)

        p_signage = PathFactory.create(geom=LineString((10, 10), (20, 10)))
        signage = SignageFactory.create(paths=[p_signage])
        blade = BladeFactory.create(signage=signage)
        intervention_blade = InterventionFactory.create(target=blade)
        self.assertQuerysetEqual(intervention_blade.paths, [p_signage.name, ], transform=str)

        course = CourseFactory.create()
        intervention_course = InterventionFactory.create(target=course)
        self.assertQuerysetEqual(intervention_course.paths, [], transform=str)

    def test_helpers(self):
        """
        We check that all infrastructures and signages near/linked to the intervention are displayed
        """
        infra = InfrastructureFactory.create()
        sign = SignageFactory.create()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            geometry_extern = LineString(Point(700200, 6600100),
                                         Point(700300, 6600300),
                                         rid=settings.SRID)
            path_extern = PathFactory.create(geom=geometry_extern)
            SignageFactory.create(paths=[(path_extern,
                                          1,
                                          1)])
            InfrastructureFactory.create(paths=[(path_extern,
                                                 1,
                                                 1)])
        else:
            geometry_extern = Point(700300, 6600300, srid=settings.SRID)
            SignageFactory.create(geom=geometry_extern)
            InfrastructureFactory.create(geom=geometry_extern)
        interv = InterventionFactory.create(target=infra)
        proj = ProjectFactory.create()

        self.assertEqual(interv.target, infra)

        self.assertEqual(list(interv.signages), [sign])
        self.assertEqual(list(interv.infrastructures), [infra])

        interv.target = sign
        interv.save()

        self.assertEqual(list(interv.signages), [sign])
        self.assertEqual(list(interv.infrastructures), [infra])

        self.assertFalse(interv.in_project)
        interv.project = proj
        self.assertTrue(interv.in_project)
        interv.save()
        funding = FundingFactory(project=proj, amount=6)
        project_pk = proj.pk
        funding_pk = funding.pk
        obj_repr = str(proj)
        proj.delete(force=True)
        model_num = ContentType.objects.get_for_model(Funding).pk
        entry = LogEntry.objects.get(content_type=model_num, object_id=funding_pk)
        self.assertEqual(entry.change_message, f"Deleted by cascade from Project {project_pk} - {obj_repr}")
        self.assertEqual(entry.action_flag, DELETION)

    def test_delete_topology(self):
        infra = InfrastructureFactory.create()
        interv = InterventionFactory.create(target=infra)
        interv.save()
        infra.delete()
        self.assertEqual(Infrastructure.objects.existing().count(), 0)
        self.assertEqual(Intervention.objects.existing().count(), 0)

    def test_denormalized_fields(self):
        infra = InfrastructureFactory.create()
        infra.save()

        def create_interv():
            interv = InterventionFactory.create(target=infra)
            return interv

        if settings.TREKKING_TOPOLOGY_ENABLED:
            self.assertNotEqual(infra.length, 0.0)

            # After setting related infrastructure
            interv = create_interv()
            self.assertEqual(interv.length, infra.length)

            # After update related infrastructure
            infra.length = 3.14
            infra.save()
            interv.reload()
        else:
            interv = create_interv()
        self.assertEqual(interv.length, infra.length)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_length_auto(self):
        # Line intervention has auto length from topology
        interv = InfrastructureInterventionFactory.create()
        interv.length = 3.14
        interv.save()
        self.assertNotEqual(interv.length, 3.14)
        # Point intervention has manual length
        interv = InfrastructurePointInterventionFactory.create()
        interv.length = 3.14
        interv.save()
        self.assertEqual(interv.length, 3.14)

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_length_not_auto_nds(self):
        interv = InfrastructureInterventionFactory.create()
        interv.length = 3.14
        interv.save()
        self.assertEqual(interv.length, 3.14)
        # Point intervention has manual length
        interv = InfrastructurePointInterventionFactory.create()
        interv.length = 3.14
        interv.save()
        self.assertEqual(interv.length, 3.14)

    def test_area_auto(self):
        # Line
        interv = InfrastructureInterventionFactory.create(width=10.0)
        interv.reload()
        self.assertAlmostEqual(interv.area, interv.length * 10.0)

        # Points
        interv = InfrastructurePointInterventionFactory.create()
        interv.reload()
        self.assertEqual(interv.length, 0.0)
        self.assertEqual(interv.area, 0.0)

        interv = InfrastructurePointInterventionFactory.create(length=50, width=10.0)
        interv.reload()
        self.assertEqual(interv.area, 500)

        interv = InfrastructurePointInterventionFactory.create(width=0.5, length=0.5)
        interv.reload()
        self.assertEqual(interv.area, 0.25)

        interv = InfrastructurePointInterventionFactory.create(width=0.5)
        interv.reload()
        self.assertEqual(interv.area, 0.0)

    def test_infrastructure_display_is_path_by_default(self):
        translation.activate('en')
        on_path = InterventionFactory.create()
        self.assertIn('Path', on_path.target_display)
        self.assertIn('path-16.png', on_path.target_display)

    def test_infrastructure_display_shows_object_name(self):
        interv = InfrastructureInterventionFactory.create()
        self.assertIn('Infrastructure', interv.target_display)
        self.assertIn('infrastructure-16.png', interv.target_display)
        name = interv.target.name
        self.assertIn(name, interv.target_display)

        interv = SignageInterventionFactory.create()
        self.assertIn('Signage', interv.target_display)
        self.assertIn('signage-16.png', interv.target_display)
        name = interv.target.name
        self.assertIn(name, interv.target_display)

    def test_target_deleted_display_previous_object(self):
        course = CourseFactory.create()
        site = SiteFactory.create()
        interv_course = InterventionFactory.create(target=course)
        interv_site = InterventionFactory.create(target=site)
        course.delete()
        site.delete()

        self.assertIn('Deleted', interv_course.target_display)
        self.assertIn('Deleted', interv_site.target_display)

    def test_target_deleted_display_csv_previous_object(self):
        course = CourseFactory.create()
        site = SiteFactory.create()
        interv_course = InterventionFactory.create(target=course)
        interv_site = InterventionFactory.create(target=site)
        course.delete()
        site.delete()

        self.assertIn('Deleted', interv_course.target_csv_display)
        self.assertIn('Deleted', interv_site.target_csv_display)

    def test_total_cost(self):
        interv = InfrastructureInterventionFactory.create(
            material_cost=1,
            heliport_cost=2,
            contractor_cost=4,
            # implicit 1 manday x 500 €
        )
        self.assertEqual(interv.total_cost, 507)

    def test_disorders_display(self):
        interv = InterventionFactory.create()
        interv.disorders.add(InterventionDisorderFactory.create(disorder="foobar"))
        self.assertEqual(interv.disorders_display, f'{interv.disorders.first().disorder}, foobar')

    def test_jobs_display(self):
        interv = InterventionFactory.create()
        job = InterventionJobFactory(job="Worker", cost=12, active=False)
        ManDayFactory(nb_days=3, job=job, intervention=interv)
        interv.jobs.add(job)
        self.assertEqual(interv.jobs_display, f'{interv.jobs.first().job}, Worker')

    def test_target_display_none(self):
        infra = InterventionFactory.create(target=None, target_id=None, target_type=None)
        self.assertEqual(infra.target_display, '-')

    def test_target_display_csv_none(self):
        interv = InterventionFactory.create(target=None)
        self.assertIn('-', interv.target_csv_display)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class ProjectModelTest(TestCase):
    def test_paths_property(self):
        p_infra = PathFactory.create(geom=LineString((0, 0), (0, 10)))
        infra = InfrastructureFactory.create(paths=[p_infra])
        intervention_infra = InterventionFactory.create(target=infra)

        p_signage = PathFactory.create(geom=LineString((10, 10), (20, 10)))
        signage = SignageFactory.create(paths=[p_signage])
        blade = BladeFactory.create(signage=signage)
        intervention_blade = InterventionFactory.create(target=blade)

        course = CourseFactory.create()
        intervention_course = InterventionFactory.create(target=course)

        project = ProjectFactory.create()
        project.interventions.add(intervention_infra)
        project.interventions.add(intervention_blade)
        project.interventions.add(intervention_course)
        self.assertQuerysetEqual(list(project.paths), [p_infra.name, p_signage.name], ordered=False, transform=str)

    def test_trails_property(self):
        p_infra = PathFactory.create(geom=LineString((0, 0), (0, 10)))
        infra = InfrastructureFactory.create(paths=[p_infra])
        intervention_infra = InterventionFactory.create(target=infra)
        TrailFactory.create(paths=[p_infra], name='trail_1')
        TrailFactory.create(paths=[p_infra], name='trail_2')
        p_signage = PathFactory.create(geom=LineString((10, 10), (20, 10)))
        TrailFactory.create(paths=[p_signage], name='trail_signage')
        signage = SignageFactory.create(paths=[p_signage])
        blade = BladeFactory.create(signage=signage)
        intervention_blade = InterventionFactory.create(target=blade)

        course = CourseFactory.create()
        intervention_course = InterventionFactory.create(target=course)

        project = ProjectFactory.create()
        project.interventions.add(intervention_infra)
        project.interventions.add(intervention_blade)
        project.interventions.add(intervention_course)
        self.assertQuerysetEqual(list(project.trails), ['trail_1', 'trail_2', 'trail_signage'], ordered=False, transform=str)

    def test_intervention_contractors(self):
        project = ProjectFactory.create()
        contractor1 = ContractorFactory.create(contractor="contractor1")
        contractor2 = ContractorFactory.create(contractor="contractor2")
        intervention = InterventionFactory.create(project=project)
        intervention.contractors.set([contractor1, contractor2])
        self.assertEqual(project.intervention_contractors, ["contractor1", "contractor2"])
