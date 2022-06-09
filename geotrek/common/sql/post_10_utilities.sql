-------------------------------------------------------------------------------
-- Date trigger functions
-------------------------------------------------------------------------------

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

CREATE FUNCTION {# geotrek.common #}.ft_uuid_insert() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    NEW.uuid := gen_random_uuid();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
