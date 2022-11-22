---------------------------------------------------------------------
-- Make sure cache key (base on lastest updated) is refresh on DELETE
---------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.sensitive_area_update_geom_buffered_intersection() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
BEGIN
    NEW.geom_buffered = ST_BUFFER(NEW.geom, {{ SENSITIVE_AREA_INTERSECTION_MARGIN }});
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER sensitivity_geom_buffered_intersection
    BEFORE INSERT OR UPDATE ON sensitivity_sensitivearea
    FOR EACH ROW EXECUTE PROCEDURE sensitive_area_update_geom_buffered_intersection();