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