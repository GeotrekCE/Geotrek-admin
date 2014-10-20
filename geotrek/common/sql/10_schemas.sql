SELECT create_schema_if_not_exist('geotrek');
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
SELECT set_schema('easy_thumbnails_source', 'django');
SELECT set_schema('easy_thumbnails_thumbnail', 'django');
SELECT set_schema('south_migrationhistory', 'django');

-- Move Geotrek internal tables to their schema
SELECT set_schema('authent_structure', 'geotrek');
SELECT set_schema('authent_userprofile', 'geotrek');
SELECT set_schema('fl_b_fichier', 'geotrek');
SELECT set_schema('fl_t_fichier', 'geotrek');
