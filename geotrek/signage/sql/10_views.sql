DROP VIEW IF EXISTS a_v_signaletique;
DROP VIEW IF EXISTS v_signages;

CREATE VIEW {# geotrek.signage #}.v_signages AS (
	SELECT e.geom, t.*
	FROM signage_signage AS t, signage_signagetype AS b, core_topology AS e
	WHERE t.topo_object_id = e.id AND t.type_id = b.id
	AND e.deleted = FALSE
);
