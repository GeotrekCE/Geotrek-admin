-------------------------------------------------------------------------------
-- Date trigger functions
-------------------------------------------------------------------------------

DROP FUNCTION IF EXISTS ft_date_insert() CASCADE;
DROP FUNCTION IF EXISTS ft_date_update() CASCADE;

CREATE FUNCTION {# geotrek.common #}.ft_date_insert() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    NEW.date_insert := statement_timestamp();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION {# geotrek.common #}.ft_date_update() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    NEW.date_update := statement_timestamp();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
