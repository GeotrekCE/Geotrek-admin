CREATE OR REPLACE VIEW geotrek.v_trails AS (
    SELECT e.geom, t.*
    FROM core_trail AS t, core_topology AS e
    WHERE t.topo_object_id = e.id
    AND e.deleted = FALSE
);
