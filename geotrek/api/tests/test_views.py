#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from mapentity.factories import SuperUserFactory


class SyncMobileViewTest(TestCase):
    def setUp(self):
        self.super_user = SuperUserFactory.create(username='admin', password='super')
        self.simple_user = User.objects.create_user(username='homer', password='doooh')

    def test_get_sync_mobile_superuser(self):
        self.client.login(username='admin', password='super')
        response = self.client.get(reverse('apimobile:sync_mobiles_view'))
        self.assertEqual(response.status_code, 200)

    def test_get_sync_mobile_simpleuser(self):
        self.client.login(username='homer', password='doooh')
        response = self.client.get(reverse('apimobile:sync_mobiles_view'))
        self.assertRedirects(response, '/login/?next=/api/mobile/commands/syncview')
