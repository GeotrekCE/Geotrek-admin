from django.conf import settings
from django.test import TestCase

from geotrek.core.factories import PathFactory

import os


class ModelsTest(TestCase):
    def test_delete_with_attachment(self):
        path = PathFactory.create()
        with open(os.path.join(settings.MEDIA_ROOT, 'maps', 'path-%s.png' % path.pk), mode='w') as f:
            path.delete()
        self.assertFalse(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'maps', 'path-%s.png' % path.pk)))
