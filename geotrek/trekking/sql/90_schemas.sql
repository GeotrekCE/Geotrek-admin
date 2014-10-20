SELECT create_schema_if_not_exist('rando');

SELECT set_schema('o_t_itineraire', 'rando');
SELECT set_schema('o_v_itineraire', 'rando');
SELECT set_schema('o_t_poi', 'rando');
SELECT set_schema('o_v_poi', 'rando');
SELECT set_schema('o_b_difficulte', 'rando');
SELECT set_schema('o_b_parcours', 'rando');
SELECT set_schema('o_b_poi', 'rando');
SELECT set_schema('o_b_reseau', 'rando');
SELECT set_schema('o_b_theme', 'rando');
SELECT set_schema('o_b_usage', 'rando');
SELECT set_schema('o_b_web_category', 'rando');
SELECT set_schema('o_r_itineraire_itineraire', 'rando');
SELECT set_schema('o_r_itineraire_renseignement', 'rando');
SELECT set_schema('o_r_itineraire_reseau', 'rando');
SELECT set_schema('o_r_itineraire_theme', 'rando');
SELECT set_schema('o_r_itineraire_usage', 'rando');
SELECT set_schema('o_r_itineraire_web', 'rando');
SELECT set_schema('o_b_renseignement', 'rando');
SELECT set_schema('o_t_web', 'rando');

SELECT set_schema_ft('troncons_unpublish_trek_d()', 'rando');
SELECT set_schema_ft('create_relationships_iu()', 'rando');
SELECT set_schema_ft('cleanup_relationships_d()', 'rando');
