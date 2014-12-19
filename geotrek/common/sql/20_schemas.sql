--
-- Move tables to their schema
--
-- All apps managed by South are moved by Geotrek on a post-migrate signal.
-- Here we move the tables of apps that are not managed by South basically.
--
SELECT create_schema_if_not_exist('django');

-- Move Django internal tables to its schema
SELECT set_schema('auth_group', 'django');
SELECT set_schema('auth_group_permissions', 'django');
SELECT set_schema('auth_permission', 'django');
SELECT set_schema('auth_user', 'django');
SELECT set_schema('auth_user_groups', 'django');
SELECT set_schema('auth_user_user_permissions', 'django');
SELECT set_schema('django_admin_log', 'django');
SELECT set_schema('django_content_type', 'django');
SELECT set_schema('django_session', 'django');
SELECT set_schema('south_migrationhistory', 'django');

-- Django-paperclip is not managed by South
SELECT set_schema('fl_t_fichier', 'geotrek');
