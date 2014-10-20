SELECT create_schema_if_not_exist('zonage');

SELECT set_schema('l_commune', 'zonage');
SELECT set_schema('l_secteur', 'zonage');
SELECT set_schema('l_zonage_reglementaire', 'zonage');
SELECT set_schema('f_b_zonage', 'zonage');
SELECT set_schema('f_t_commune', 'zonage');
SELECT set_schema('f_t_secteur', 'zonage');
SELECT set_schema('f_t_zonage', 'zonage');
SELECT set_schema('f_v_commune', 'zonage');
SELECT set_schema('f_v_secteur', 'zonage');
SELECT set_schema('f_v_zonage', 'zonage');
