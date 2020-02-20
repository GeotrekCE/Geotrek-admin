-- Cleanup public schema if installed before release 0.28
DROP VIEW IF EXISTS public.a_v_signaletique;
DROP VIEW IF EXISTS gestion.a_v_signaletique;
DROP VIEW IF EXISTS gestion.v_signage;