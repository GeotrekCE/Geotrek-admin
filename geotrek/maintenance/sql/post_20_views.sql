CREATE VIEW {# geotrek.maintenance #}.v_interventions AS (

	SELECT e.geom, e.uuid, i.*
	FROM maintenance_intervention AS i, core_topology AS e,  signage_blade as b
	WHERE (i.target_id = e.id AND i.target_type_id NOT IN (SELECT id FROM django_content_type  AS ct WHERE ct.model = 'blade')) OR
	(i.target_id = b.id AND i.target_type_id IN (SELECT id FROM django_content_type  AS ct WHERE ct.model = 'blade') AND e.id=b.signage_id)
	AND i.deleted = FALSE
);

CREATE VIEW {# geotrek.maintenance #}.v_projects AS (
	SELECT ST_Union(t.geom) AS geom, s.*
	FROM v_interventions AS t, maintenance_project AS s
	WHERE t.project_id = s.id
	GROUP BY t.project_id, s.id
);
