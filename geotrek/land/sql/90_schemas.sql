SELECT create_schema_if_not_exist('foncier');

SELECT set_schema('f_v_nature', 'foncier');
SELECT set_schema('f_v_foncier', 'foncier');
SELECT set_schema('f_v_competence', 'foncier');
SELECT set_schema('f_v_gestion_signaletique', 'foncier');
SELECT set_schema('f_v_gestion_travaux', 'foncier');
