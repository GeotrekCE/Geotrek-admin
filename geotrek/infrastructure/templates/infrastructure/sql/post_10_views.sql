CREATE VIEW {{ schema_geotrek }}.v_infrastructures AS (
	SELECT e.geom, e.id, e.uuid, t.*
	FROM infrastructure_infrastructure AS t, infrastructure_infrastructuretype AS b, core_topology AS e
	WHERE t.topo_object_id = e.id AND t.type_id = b.id
	AND e.deleted = FALSE
);
