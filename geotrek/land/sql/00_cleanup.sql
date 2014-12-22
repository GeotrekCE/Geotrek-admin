-- Cleanup public schema if installed before release 0.28
DROP VIEW IF EXISTS public.f_v_nature;
DROP VIEW IF EXISTS public.f_v_foncier;
DROP VIEW IF EXISTS public.f_v_competence;
DROP VIEW IF EXISTS public.f_v_gestion_signaletique;
DROP VIEW IF EXISTS public.f_v_gestion_travaux;
