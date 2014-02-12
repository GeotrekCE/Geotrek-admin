DROP VIEW IF EXISTS l_v_sentier;
CREATE VIEW l_v_sentier AS (
	SELECT ST_UNION(t.geom) AS geom_sentier, s.*
	FROM l_t_troncon AS t, l_t_sentier AS s
	WHERE t.sentier = s.id
	GROUP BY s.id
);