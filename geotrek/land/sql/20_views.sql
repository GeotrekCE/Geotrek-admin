SELECT create_schema_if_not_exist('foncier');

CREATE OR REPLACE VIEW foncier.f_v_nature AS (
	SELECT e.*, b.nom, b.structure
	FROM e_t_evenement AS e, f_t_nature AS f, f_b_nature AS b
	WHERE f.evenement = e.id AND f.type = b.id
	AND supprime = FALSE
);

CREATE OR REPLACE VIEW foncier.f_v_foncier AS (
	SELECT e.*, b.structure, b.foncier, b.droit_de_passage
	FROM e_t_evenement AS e, f_t_foncier AS f, f_b_foncier AS b
	WHERE f.evenement = e.id AND f.type = b.id
	AND supprime = FALSE
);

CREATE OR REPLACE VIEW foncier.f_v_competence AS (
	SELECT e.*, b.structure, b.organisme
	FROM e_t_evenement AS e, f_t_competence AS f, m_b_organisme AS b
	WHERE f.evenement = e.id AND f.organisme = b.id
	AND supprime = FALSE
);

CREATE OR REPLACE VIEW foncier.f_v_gestion_signaletique AS (
	SELECT e.*, b.structure, b.organisme
	FROM e_t_evenement AS e, f_t_gestion_signaletique AS f, m_b_organisme AS b
	WHERE f.evenement = e.id AND f.organisme = b.id
	AND supprime = FALSE
);

CREATE OR REPLACE VIEW foncier.f_v_gestion_travaux AS (
	SELECT e.*, b.structure, b.organisme
	FROM e_t_evenement AS e, f_t_gestion_travaux AS f, m_b_organisme AS b
	WHERE f.evenement = e.id AND f.organisme = b.id
	AND supprime = FALSE
);