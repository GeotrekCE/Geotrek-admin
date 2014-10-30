SELECT create_schema_if_not_exist('rando');

SELECT set_schema('o_v_itineraire', 'rando');
SELECT set_schema('o_v_poi', 'rando');
SELECT set_schema_ft('troncons_unpublish_trek_d()', 'rando');
SELECT set_schema_ft('create_relationships_iu()', 'rando');
SELECT set_schema_ft('cleanup_relationships_d()', 'rando');
