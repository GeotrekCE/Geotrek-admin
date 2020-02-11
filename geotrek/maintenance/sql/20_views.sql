CREATE OR REPLACE VIEW gestion.m_v_intervention AS (
	SELECT e.geom, i.*
	FROM maintenance_intervention AS i, core_topology AS e
	WHERE i.topology_id = e.id
	AND i.deleted = FALSE
);

CREATE OR REPLACE VIEW gestion.m_v_chantier AS (
	SELECT ST_Union(t.geom) AS geom_chantier, s.*
	FROM m_v_intervention AS t, maintenance_project AS s
	WHERE t.project_id = s.id
	GROUP BY t.project_id, s.id
);
