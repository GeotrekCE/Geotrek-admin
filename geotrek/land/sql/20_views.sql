DROP VIEW IF EXISTS f_v_commune;
CREATE VIEW f_v_commune AS (
	SELECT e.*, l.insee, l.commune
	FROM e_t_evenement AS e, f_t_commune AS f, l_commune AS l
	WHERE f.evenement = e.id AND f.commune = l.insee
	AND supprime = FALSE
);

DROP VIEW IF EXISTS f_v_secteur;
CREATE VIEW f_v_secteur AS (
	SELECT e.*, l.secteur
	FROM e_t_evenement AS e, f_t_secteur AS f, l_secteur AS l
	WHERE f.evenement = e.id AND f.secteur = l.id
	AND supprime = FALSE
);

DROP VIEW IF EXISTS f_v_zonage;
CREATE VIEW f_v_zonage AS (
	SELECT e.*, l.id AS zonage_id, l.zonage, b.nom
	FROM e_t_evenement AS e, f_t_zonage AS f, f_b_zonage AS b, l_zonage_reglementaire AS l
	WHERE f.evenement = e.id AND f.zone = l.id AND l.type = b.id
	AND supprime = FALSE
);

DROP VIEW IF EXISTS f_v_nature;
CREATE VIEW f_v_nature AS (
	SELECT e.*, b.nom, b.structure
	FROM e_t_evenement AS e, f_t_nature AS f, f_b_nature AS b
	WHERE f.evenement = e.id AND f.type = b.id
	AND supprime = FALSE
);

DROP VIEW IF EXISTS f_v_foncier;
CREATE VIEW f_v_foncier AS (
	SELECT e.*, b.structure, b.foncier, b.droit_de_passage
	FROM e_t_evenement AS e, f_t_foncier AS f, f_b_foncier AS b
	WHERE f.evenement = e.id AND f.type = b.id
	AND supprime = FALSE
);

DROP VIEW IF EXISTS f_v_competence;
CREATE VIEW f_v_competence AS (
	SELECT e.*, b.structure, b.organisme
	FROM e_t_evenement AS e, f_t_competence AS f, m_b_organisme AS b
	WHERE f.evenement = e.id AND f.organisme = b.id
	AND supprime = FALSE
);

DROP VIEW IF EXISTS f_v_gestion_signaletique;
CREATE VIEW f_v_gestion_signaletique AS (
	SELECT e.*, b.structure, b.organisme
	FROM e_t_evenement AS e, f_t_gestion_signaletique AS f, m_b_organisme AS b
	WHERE f.evenement = e.id AND f.organisme = b.id
	AND supprime = FALSE
);

DROP VIEW IF EXISTS f_v_gestion_travaux;
CREATE VIEW f_v_gestion_travaux AS (
	SELECT e.*, b.structure, b.organisme
	FROM e_t_evenement AS e, f_t_gestion_travaux AS f, m_b_organisme AS b
	WHERE f.evenement = e.id AND f.organisme = b.id
	AND supprime = FALSE
);