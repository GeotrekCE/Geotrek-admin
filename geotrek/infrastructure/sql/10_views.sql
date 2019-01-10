SELECT create_schema_if_not_exist('gestion');

CREATE OR REPLACE VIEW gestion.a_v_amenagement AS (
	SELECT e.geom, t.*
	FROM a_t_infrastructure AS t, a_b_amenagement AS b, e_t_evenement AS e
	WHERE t.evenement = e.id AND t.type = b.id
	AND e.supprime = FALSE
);

