-------------------------------------------------------------------------------
-- Date trigger functions
-------------------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.ft_date_insert() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    NEW.date_insert := statement_timestamp();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION {{ schema_geotrek }}.ft_date_update() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    NEW.date_update := statement_timestamp();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION {{ schema_geotrek }}.ft_uuid_insert() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    NEW.uuid := gen_random_uuid();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Possible to have collection of GeometryCollection
-- we need to flatten the geometrycollection to avoid problem with export and edition (#3397)

CREATE FUNCTION {{ schema_geotrek }}.flatten_geometrycollection_iu() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    geoms geometry[];
    geom geometry;
BEGIN
    FOR geom IN SELECT (ST_Dump(NEW.geom)).geom LOOP
        geoms := array_append(geoms, geom);
    END LOOP;
    NEW.geom := ST_ForceCollection(ST_COLLECT(geoms));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
