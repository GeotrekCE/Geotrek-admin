-- 10

DROP FUNCTION IF EXISTS troncons_unpublish_trek_d() CASCADE;
DROP FUNCTION IF EXISTS paths_unpublish_trek_d() CASCADE;

-- 20

DROP FUNCTION IF EXISTS create_relationships_iu() CASCADE;
DROP FUNCTION IF EXISTS cleanup_relationships_d() CASCADE;

-- 30

DROP VIEW IF EXISTS o_v_itineraire CASCADE;
DROP VIEW IF EXISTS v_treks CASCADE;
DROP VIEW IF EXISTS o_v_poi CASCADE;
DROP VIEW IF EXISTS v_pois CASCADE;