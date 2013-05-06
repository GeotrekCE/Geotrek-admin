# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group

from geotrek.authent.factories import UserProfileFactory
from geotrek.authent.models import (
    GROUP_PATH_MANAGER, GROUP_TREKKING_MANAGER, GROUP_EDITOR,
)


def populate_groups():
    """
    Create (or get) each group. Returns dict: group_name -> Group
    """
    groups = (GROUP_PATH_MANAGER, GROUP_TREKKING_MANAGER, GROUP_EDITOR)

    return dict((group, Group.objects.get_or_create(name=group)[0]) for group in groups)


def populate_users():
    """
    Create and returns a list of user, each one belonging to a relevant group.
    Create those group if needed.
    """

    users_to_create = [
        { 'username': 'path_manager_user' , 'groups': [GROUP_PATH_MANAGER] },
        { 'username': 'comm_manager_user' , 'groups': [GROUP_TREKKING_MANAGER] },
        { 'username': 'editor_user'       , 'groups': [GROUP_EDITOR] },
    ]

    # Get or create all needed relevant groups
    populate_groups()

    created_user_profiles = []

    for user in users_to_create:
        created_user_profiles.append(
            UserProfileFactory(
                user__username=user['username'],
                user__groups=Group.objects.filter(name__in=user['groups']),
        ))

    return created_user_profiles
