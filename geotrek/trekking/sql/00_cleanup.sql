-- Cleanup public schema if installed before release 0.28
DROP VIEW IF EXISTS public.o_v_itineraire;
DROP VIEW IF EXISTS public.o_v_poi;
DROP FUNCTION IF EXISTS public.troncons_unpublish_trek_d() CASCADE;
DROP FUNCTION IF EXISTS public.create_relationships_iu() CASCADE;
DROP FUNCTION IF EXISTS public.cleanup_relationships_d() CASCADE;
