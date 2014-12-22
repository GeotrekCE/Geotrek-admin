CREATE OR REPLACE VIEW gestion.m_v_intervention AS (
	SELECT e.geom, i.*
	FROM m_t_intervention AS i, e_t_evenement AS e
	WHERE i.topology_id = e.id
	AND i.supprime = FALSE
);

CREATE OR REPLACE VIEW gestion.m_v_chantier AS (
	SELECT ST_UNION(t.geom) AS geom_chantier, s.*
	FROM m_v_intervention AS t, m_t_chantier AS s
	WHERE t.chantier = s.id
	GROUP BY t.chantier, s.id
);
