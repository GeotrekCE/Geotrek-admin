-- Cleanup public schema if installed before release 0.28
DROP VIEW IF EXISTS public.f_v_commune;
DROP VIEW IF EXISTS zonage.f_v_commune;
DROP VIEW IF EXISTS zonage.v_cities;
DROP VIEW IF EXISTS public.f_v_secteur;
DROP VIEW IF EXISTS zonage.f_v_secteur;
DROP VIEW IF EXISTS zonage.v_districts;
DROP VIEW IF EXISTS public.f_v_zonage;
DROP VIEW IF EXISTS zonage.f_v_zonage;
DROP VIEW IF EXISTS zonage.v_restrictedareas;
DROP FUNCTION IF EXISTS public.lien_auto_troncon_couches_sig_d() CASCADE;
DROP FUNCTION IF EXISTS public.nettoyage_auto_couches_sig_d() CASCADE;
DROP FUNCTION IF EXISTS public.lien_auto_couches_sig_troncon_iu() CASCADE;
DROP FUNCTION IF EXISTS public.lien_auto_troncon_couches_sig_iu() CASCADE;
