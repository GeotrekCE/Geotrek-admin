-- Cleanup public schema if installed before release 0.28
DROP VIEW IF EXISTS public.a_v_amenagement;
DROP VIEW IF EXISTS public.a_v_equipement;
DROP VIEW IF EXISTS public.a_v_signaletique;
