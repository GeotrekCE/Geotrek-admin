CREATE SCHEMA IF NOT EXISTS {# django #};

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='django_migrations' AND table_schema!='{# django #}') THEN
        EXECUTE 'ALTER TABLE django_migrations SET SCHEMA {# django #};';
    END IF;
END;
$$ LANGUAGE plpgsql;
