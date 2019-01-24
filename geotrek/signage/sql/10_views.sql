SELECT create_schema_if_not_exist('gestion');

CREATE OR REPLACE VIEW gestion.a_v_signaletique AS (
	SELECT e.geom, t.*
	FROM s_t_signaletique AS t, s_b_signaletique AS b, e_t_evenement AS e
	WHERE t.evenement = e.id AND t.type = b.id
	AND e.supprime = FALSE
);
