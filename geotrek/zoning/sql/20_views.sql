CREATE OR REPLACE VIEW zonage.f_v_commune AS (
	SELECT e.*, l.insee, l.commune
	FROM e_t_evenement AS e, f_t_commune AS f, l_commune AS l
	WHERE f.evenement = e.id AND f.commune = l.insee
	AND supprime = FALSE
);

CREATE OR REPLACE VIEW zonage.f_v_secteur AS (
	SELECT e.*, l.secteur
	FROM e_t_evenement AS e, f_t_secteur AS f, l_secteur AS l
	WHERE f.evenement = e.id AND f.secteur = l.id
	AND supprime = FALSE
);

CREATE OR REPLACE VIEW zonage.f_v_zonage AS (
	SELECT e.*, l.id AS zonage_id, l.zonage, b.nom
	FROM e_t_evenement AS e, f_t_zonage AS f, f_b_zonage AS b, l_zonage_reglementaire AS l
	WHERE f.evenement = e.id AND f.zone = l.id AND l.type = b.id
	AND supprime = FALSE
);
