--
-- Create database schemas.
-- We can't use IF NOT EXISTS until PostgreSQL 9.3.
--
DO $$
BEGIN
    BEGIN
      CREATE SCHEMA geotrek;
      CREATE SCHEMA django;
    EXCEPTION
      WHEN OTHERS THEN
        RAISE WARNING '%', SQLERRM;
    END;
END$$;


-- Move Django internal tables to its schema
ALTER TABLE auth_group SET SCHEMA django;
ALTER TABLE auth_group_permissions SET SCHEMA django;
ALTER TABLE auth_permission SET SCHEMA django;
ALTER TABLE auth_user SET SCHEMA django;
ALTER TABLE auth_user_groups SET SCHEMA django;
ALTER TABLE auth_user_user_permissions SET SCHEMA django;
ALTER TABLE django_admin_log SET SCHEMA django;
ALTER TABLE django_content_type SET SCHEMA django;
ALTER TABLE django_session SET SCHEMA django;
ALTER TABLE easy_thumbnails_source SET SCHEMA django;
ALTER TABLE easy_thumbnails_thumbnail SET SCHEMA django;
ALTER TABLE south_migrationhistory SET SCHEMA django;

-- Move Geotrek internal tables to their schema
ALTER TABLE authent_structure SET SCHEMA geotrek;
ALTER TABLE authent_userprofile SET SCHEMA geotrek;
