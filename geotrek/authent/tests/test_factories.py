from django.test import TestCase
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType

from .. import factories


class AuthentFactoriesTest(TestCase):
    """
    Ensure factories work as expected.
    Here we just call each one to ensure they do not trigger any random
    error without verifying any other expectation.
    """

    @classmethod
    def get_or_create_dummy_perm(cls):
        """
        Create programmatically some dummy permission, just to create one.

        Taken from:
        https://docs.djangoproject.com/en/dev/topics/auth/#programmatically-creating-permissions
        """
        content_type, _ = ContentType.objects.get_or_create(
                app_label='auth', model='user')

        permission, _ = auth_models.Permission.objects.get_or_create(
                codename='can_foobar', name='Can foobar',
                content_type=content_type)

        return permission

    def test_user_factory(self):
        factories.UserFactory()

    def test_super_user_factory(self):
        factories.SuperUserFactory()

    def test_structure_factory(self):
        factories.StructureFactory()

    def test_user_profile_factory(self):
        factories.UserProfileFactory()

    def test_user_factory_with_groups(self):
        """Test that our UserFactory behave well with groups keyword"""

        group = auth_models.Group.objects.create(name='Group boobies')
        user = factories.UserFactory(groups=[ group ])

        # Would fails if the group did not exist
        user.groups.get(pk=group.pk)

    def test_user_factory_with_perms(self):
        """Test that our UserFactory behave well with permissions keyword"""

        perm = self.get_or_create_dummy_perm()
        user = factories.UserFactory(permissions=[ perm ])

        # Would fails if the group did not exist
        user.user_permissions.get(pk=perm.pk)

        # An "has_perm" function exists... use it (even if bloated !)
        self.assertTrue(
            user.has_perm(
                '%s.%s' % (perm.content_type.app_label, perm.codename)
            )
        )
