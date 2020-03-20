CREATE VIEW {# geotrek.maintenance #}.v_interventions AS (
	SELECT e.geom, i.*
	FROM maintenance_intervention AS i, core_topology AS e
	WHERE i.target_id = e.id
	AND i.deleted = FALSE
);

CREATE VIEW {# geotrek.maintenance #}.v_projects AS (
	SELECT ST_Union(t.geom) AS geom, s.*
	FROM v_interventions AS t, maintenance_project AS s
	WHERE t.project_id = s.id
	GROUP BY t.project_id, s.id
);
