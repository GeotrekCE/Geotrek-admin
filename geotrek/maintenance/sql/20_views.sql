DROP VIEW IF EXISTS m_v_intervention CASCADE;
DROP VIEW IF EXISTS v_interventions CASCADE;
DROP VIEW IF EXISTS m_v_chantier;
DROP VIEW IF EXISTS v_projects;

CREATE VIEW {# geotrek.maintenance #}.v_interventions AS (
	SELECT e.geom, i.*
	FROM maintenance_intervention AS i, core_topology AS e
	WHERE i.topology_id = e.id
	AND i.deleted = FALSE
);

CREATE VIEW {# geotrek.maintenance #}.v_projects AS (
	SELECT ST_Union(t.geom) AS geom, s.*
	FROM v_interventions AS t, maintenance_project AS s
	WHERE t.project_id = s.id
	GROUP BY t.project_id, s.id
);
