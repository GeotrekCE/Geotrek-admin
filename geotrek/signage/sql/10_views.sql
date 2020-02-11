SELECT create_schema_if_not_exist('gestion');

CREATE OR REPLACE VIEW gestion.a_v_signaletique AS (
	SELECT e.geom, t.*
	FROM signage_signage AS t, signage_signagetype AS b, core_topology AS e
	WHERE t.topo_object_id = e.id AND t.type_id = b.id
	AND e.deleted = FALSE
);
