CREATE SCHEMA IF NOT EXISTS {{ schema_django }};

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='django_migrations' AND table_schema!='{{ schema_django }}') THEN
        EXECUTE 'ALTER TABLE django_migrations SET SCHEMA {{ schema_django }};';
    END IF;
END;
$$ LANGUAGE plpgsql;
