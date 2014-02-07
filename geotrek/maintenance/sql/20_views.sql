DROP VIEW IF EXISTS m_v_intervention;
CREATE VIEW m_v_intervention AS (
	SELECT e.geom, i.*
	FROM m_t_intervention AS i, e_t_evenement AS e
	WHERE i.topology_id = e.id
	AND i.supprime = FALSE
);