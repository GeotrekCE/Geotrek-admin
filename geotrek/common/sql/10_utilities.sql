-------------------------------------------------------------------------------
-- Schema utilities
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION create_schema_if_not_exist(schemaname varchar) RETURNS void AS $$
BEGIN
    -- We can't use IF NOT EXISTS until PostgreSQL 9.3.
    BEGIN
        EXECUTE 'CREATE SCHEMA '|| quote_ident(schemaname) ||';';
    EXCEPTION
      WHEN OTHERS THEN
        RAISE NOTICE 'Schema exists.';
    END;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION set_schema(tablename varchar, schemaname varchar) RETURNS void AS $$
BEGIN
    -- Move only if the right schema is not already set.
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name=tablename AND table_schema!=schemaname) THEN
        EXECUTE 'ALTER TABLE '|| quote_ident(tablename) ||' SET SCHEMA '|| quote_ident(schemaname) ||';';
    END IF;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- Date trigger functions
-------------------------------------------------------------------------------

SELECT create_schema_if_not_exist('geotrek');

CREATE OR REPLACE FUNCTION geotrek.ft_date_insert() RETURNS trigger AS $$
BEGIN
    NEW.date_insert := statement_timestamp();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION geotrek.ft_date_update() RETURNS trigger AS $$
BEGIN
    NEW.date_update := statement_timestamp();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
