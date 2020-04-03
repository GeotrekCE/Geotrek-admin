DROP VIEW IF EXISTS a_v_amenagement;
DROP VIEW IF EXISTS a_v_equipement;
DROP VIEW IF EXISTS a_v_infrastructure;
DROP VIEW IF EXISTS v_infrastructure;
DROP VIEW IF EXISTS v_infrastructures;

CREATE VIEW {# geotrek.maintenance #}.v_infrastructures AS (
	SELECT e.geom, t.*
	FROM infrastructure_infrastructure AS t, infrastructure_infrastructuretype AS b, core_topology AS e
	WHERE t.topo_object_id = e.id AND t.type_id = b.id
	AND e.deleted = FALSE
);
