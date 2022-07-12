CREATE VIEW {{ schema_geotrek }}.v_signages AS (
	SELECT e.geom, e.id, e.uuid, t.*
	FROM signage_signage AS t, signage_signagetype AS b, core_topology AS e
	WHERE t.topo_object_id = e.id AND t.type_id = b.id
	AND e.deleted = FALSE
);
