-------------------------------------------------------------------------------
-- Compute elevation and elevation-based indicators
-------------------------------------------------------------------------------

-- Possible to have collection of GeometryCollection
-- we need to flatten the geometrycollection to avoid problem with export and edition (#3397)


CREATE FUNCTION {{ schema_geotrek }}.geometrycollection_flatten_outdoor_iu() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    geoms geometry[];
    geom geometry;
BEGIN
    FOR geom IN SELECT (ST_Dump(NEW.geom)).geom LOOP
        -- Update site geometry
        geoms := array_append(geoms, geom);
    END LOOP;
    NEW.geom := ST_ForceCollection(ST_COLLECT(geoms));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER outdoor_site_30_geometrycollection_flatten_iu_tgr
BEFORE INSERT OR UPDATE OF geom ON outdoor_site
FOR EACH ROW EXECUTE PROCEDURE geometrycollection_flatten_outdoor_iu();

CREATE TRIGGER outdoor_course_30_geometrycollection_flatten_iu_tgr
BEFORE INSERT OR UPDATE OF geom ON outdoor_course
FOR EACH ROW EXECUTE PROCEDURE geometrycollection_flatten_outdoor_iu();
