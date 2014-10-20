SELECT create_schema_if_not_exist('foncier');

-- Move land tables its schema
SELECT set_schema('f_b_foncier', 'foncier');
SELECT set_schema('f_b_nature', 'foncier');
SELECT set_schema('f_b_zonage', 'foncier');
SELECT set_schema('f_t_nature', 'foncier');
SELECT set_schema('f_t_foncier', 'foncier');
SELECT set_schema('f_t_competence', 'foncier');
SELECT set_schema('f_t_gestion_signaletique', 'foncier');
SELECT set_schema('f_t_gestion_travaux', 'foncier');
SELECT set_schema('f_v_nature', 'foncier');
SELECT set_schema('f_v_foncier', 'foncier');
SELECT set_schema('f_v_competence', 'foncier');
SELECT set_schema('f_v_gestion_signaletique', 'foncier');
SELECT set_schema('f_v_gestion_travaux', 'foncier');
