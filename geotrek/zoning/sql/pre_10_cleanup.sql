-- 10
DROP FUNCTION IF EXISTS lien_auto_troncon_couches_sig_d() CASCADE;
DROP FUNCTION IF EXISTS auto_link_path_topologies_d() CASCADE;

DROP FUNCTION IF EXISTS nettoyage_auto_couches_sig_d() CASCADE;
DROP FUNCTION IF EXISTS auto_clean_topologies_sig_d() CASCADE;

DROP FUNCTION IF EXISTS lien_auto_troncon_couches_sig_iu() CASCADE;
DROP FUNCTION IF EXISTS auto_link_path_topologies_iu() CASCADE;

DROP FUNCTION IF EXISTS lien_auto_couches_sig_troncon_iu() CASCADE;
DROP FUNCTION IF EXISTS auto_link_topologies_path_iu() CASCADE;

-- 20

DROP VIEW IF EXISTS f_v_commune CASCADE;
DROP VIEW IF EXISTS v_cities CASCADE;
DROP VIEW IF EXISTS f_v_secteur CASCADE;
DROP VIEW IF EXISTS v_districts CASCADE;
DROP VIEW IF EXISTS f_v_zonage CASCADE;
DROP VIEW IF EXISTS v_restrictedareas CASCADE;
