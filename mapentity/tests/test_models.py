from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str
from django.utils.formats import localize

from mapentity.models import LogEntry, ADDITION, DELETION
from mapentity.factories import UserFactory
from geotrek.core.factories import PathFactory

import os


class ModelsTest(TestCase):
    def test_delete_with_attachment(self):
        path = PathFactory.create()
        with open(os.path.join(settings.MEDIA_ROOT, 'maps', 'path-%s.png' % path.pk), mode='w'):
            path.delete()
        self.assertFalse(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'maps', 'path-%s.png' % path.pk)))


class LogEntryTest(TestCase):
    def test_logentry(self):
        user = UserFactory.create()
        object = PathFactory.create()
        logentry = LogEntry.objects.log_action(
            user_id=user.pk,
            content_type_id=object.get_content_type_id(),
            object_id=object.pk,
            object_repr=force_str(object),
            action_flag=ADDITION
        )
        self.assertEqual('Added', logentry.action_flag_display)
        self.assertIn('{0}'.format(localize(logentry.action_time)), logentry.action_time_display)
        self.assertIn(object.name, logentry.object_display)

    def test_logentry_deleted(self):
        user = UserFactory.create()
        object = PathFactory.create()
        logentry = LogEntry.objects.log_action(
            user_id=user.pk,
            content_type_id=object.get_content_type_id(),
            object_id=object.pk,
            object_repr=force_str(object),
            action_flag=DELETION
        )
        object.delete()
        self.assertEqual('Deleted', logentry.action_flag_display)
        self.assertIn('{0}'.format(localize(logentry.action_time)), logentry.action_time_display)
        self.assertIn(object.name, logentry.object_display)
