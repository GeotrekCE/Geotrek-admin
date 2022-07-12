-------------------------------------------------------------------------------
-- Compute elevation and elevation-based indicators
-------------------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.elevation_outdoor_iu() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    geom geometry;
    elevation elevation_infos;
    length2d float;
BEGIN
    NEW.geom_3d := NULL;
    NEW.length := 0;
    NEW.slope := 0;
    NEW.min_elevation := NULL;
    NEW.max_elevation := NULL;
    NEW.ascent := 0;
    NEW.descent := 0;
    FOR geom IN SELECT (ST_Dump(NEW.geom)).geom LOOP
        IF ST_Dimension(geom) = 2 THEN
            WITH pixel AS (SELECT (ST_Intersection(rast, geom)).val FROM altimetry_dem WHERE ST_Intersects(rast, geom))
            SELECT NULL AS geom_3d, NULL AS slope,
                   MIN(val) AS min_elevation, MAX(val) AS max_elevation,
                   NULL AS ascent, NULL AS descent
                   FROM pixel
                   INTO elevation;
        ELSE
            SELECT * FROM ft_elevation_infos(geom, {{ ALTIMETRIC_PROFILE_STEP }}) INTO elevation;
        END IF;
        -- Update site geometry
        IF NEW.geom_3d = NULL THEN
            NEW.geom_3d := ST_Collect(elevation.draped);
        ELSE
            NEW.geom_3d := ST_Collect(NEW.geom_3d, elevation.draped);
        END IF;
        NEW.length := NEW.length + ST_3DLength(elevation.draped);
        length2d = ST_Length(geom);
        IF NEW.length + length2d > 0 THEN
            NEW.slope := (NEW.slope * NEW.length + elevation.slope * length2d) / (NEW.length + length2d);
        END IF;
        NEW.min_elevation := least(NEW.min_elevation, elevation.min_elevation);
        NEW.max_elevation := greatest(NEW.max_elevation, elevation.max_elevation);
        NEW.ascent := NEW.ascent + elevation.positive_gain;
        NEW.descent := NEW.descent + elevation.negative_gain;
    END LOOP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER outdoor_site_10_elevation_iu_tgr
BEFORE INSERT OR UPDATE OF geom ON outdoor_site
FOR EACH ROW EXECUTE PROCEDURE elevation_outdoor_iu();

CREATE TRIGGER outdoor_course_10_elevation_iu_tgr
BEFORE INSERT OR UPDATE OF geom ON outdoor_course
FOR EACH ROW EXECUTE PROCEDURE elevation_outdoor_iu();
