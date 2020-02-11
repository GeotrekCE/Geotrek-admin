SELECT create_schema_if_not_exist('gestion');

CREATE OR REPLACE VIEW gestion.v_infrastructure AS (
	SELECT e.geom, t.*
	FROM infrastructure_infrastructure AS t, infrastructure_infrastructuretype AS b, core_topology AS e
	WHERE t.topo_object_id = e.id AND t.type_id = b.id
	AND e.deleted = FALSE
);

