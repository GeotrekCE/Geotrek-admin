from django.core.management import call_command
from django.test import TestCase
from django.core import mail
from django.conf import settings
from geotrek.authent.factories import StructureFactory
from geotrek.infrastructure.factories import InfrastructureFactory, InfrastructureTypeFactory
from geotrek.infrastructure.models import InfrastructureType, Infrastructure
from geotrek.core.models import Usage, Path
from geotrek.core.factories import UsageFactory
from geotrek.core.factories import PathFactory


class CommandTests(TestCase):
    def test_command_emails_manager(self):
        call_command('test_managers_emails')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, u'[%s] Test email for managers' % settings.TITLE)

    def test_command_unset_structure(self):
        structure1 = StructureFactory.create(name="coucou")
        structure2 = StructureFactory.create(name="coco")

        infratype1 = InfrastructureTypeFactory.create(label="annyeong", structure=structure1, pictogram=None)
        infratype2 = InfrastructureTypeFactory.create(label="annyeong", structure=structure2, pictogram=None)

        path = PathFactory.create(name="pass")
        usage1 = UsageFactory.create(usage="hello", structure=structure1)
        usage2 = UsageFactory.create(usage="hello", structure=structure2)
        path.usages.add(usage1)
        path.usages.add(usage2)

        infrastructure1 = InfrastructureFactory.create(name='pissenlit', type=infratype1)
        infrastructure2 = InfrastructureFactory.create(name='rhododendron', type=infratype2)

        self.assertEqual(InfrastructureType.objects.count(), 2)
        self.assertEqual(Usage.objects.count(), 2)

        self.assertEqual(infrastructure1.type.label, 'annyeong')
        self.assertEqual(infrastructure1.type.structure.name, 'coucou')
        self.assertEqual(infrastructure2.type.label, 'annyeong')
        self.assertEqual(infrastructure2.type.structure.name, 'coco')

        self.assertEqual(path.usages.count(), 2)
        self.assertEqual(usage1.structure.name, 'coucou')
        self.assertEqual(usage2.structure.name, 'coco')

        call_command('unset_structure', '--all', verbosity=0)

        self.assertEqual(InfrastructureType.objects.count(), 1)
        self.assertEqual(Usage.objects.count(), 1)

        infra = Infrastructure.objects.first()

        self.assertEqual(infra.type.label, 'annyeong')
        self.assertEqual(infra.type.structure, None)

        path_usages = Path.objects.first().usages.first()

        self.assertEqual(path_usages.usage, 'hello')
        self.assertEqual(path_usages.structure, None)
