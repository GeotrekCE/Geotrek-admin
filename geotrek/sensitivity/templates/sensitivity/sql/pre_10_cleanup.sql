-- 10

DROP VIEW IF EXISTS v_sensitivearea CASCADE;
DROP FUNCTION IF EXISTS {{ schema_geotrek }}.sensitive_area_update_geom_buffered_intersection() CASCADE;
