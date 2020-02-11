CREATE OR REPLACE VIEW geotrek.l_v_sentier AS (
    SELECT e.geom, t.*
    FROM core_trail AS t, core_topology AS e
    WHERE t.topo_object_id = e.id
    AND e.deleted = FALSE
);
