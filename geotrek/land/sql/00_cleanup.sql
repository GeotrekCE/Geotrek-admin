-- Cleanup public schema if installed before release 0.28
DROP VIEW IF EXISTS public.f_v_nature;
DROP VIEW IF EXISTS foncier.f_v_nature;
DROP VIEW IF EXISTS foncier.v_physicals;
DROP VIEW IF EXISTS public.f_v_foncier;
DROP VIEW IF EXISTS foncier.f_v_foncier;
DROP VIEW IF EXISTS foncier.v_lands;
DROP VIEW IF EXISTS public.f_v_competence;
DROP VIEW IF EXISTS foncier.f_v_competence;
DROP VIEW IF EXISTS foncier.v_competences;
DROP VIEW IF EXISTS public.f_v_gestion_signaletique;
DROP VIEW IF EXISTS foncier.f_v_gestion_signaletique;
DROP VIEW IF EXISTS foncier.v_signagemanagements;
DROP VIEW IF EXISTS public.f_v_gestion_travaux;
DROP VIEW IF EXISTS foncier.f_v_gestion_travaux;
DROP VIEW IF EXISTS foncier.v_workmanagements;