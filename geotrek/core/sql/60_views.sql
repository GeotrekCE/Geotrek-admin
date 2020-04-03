DROP VIEW IF EXISTS l_v_sentier;
DROP VIEW IF EXISTS v_trails;

CREATE VIEW {# geotrek.core #}.v_trails AS (
    SELECT core_topology.geom, core_trail.*
    FROM core_trail, core_topology
    WHERE core_trail.topo_object_id = core_topology.id
    AND core_topology.deleted = FALSE
);
