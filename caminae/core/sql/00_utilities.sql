-------------------------------------------------------------------------------
-- Date trigger functions
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ft_date_insert() RETURNS trigger AS $$
BEGIN
    NEW.date_insert := statement_timestamp() AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION ft_date_update() RETURNS trigger AS $$
BEGIN
    NEW.date_update := statement_timestamp() AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-------------------------------------------------------------------------------
-- Length trigger function
-------------------------------------------------------------------------------

DROP FUNCTION IF EXISTS ft_longueur() CASCADE;
