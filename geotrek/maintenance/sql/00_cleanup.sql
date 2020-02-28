-- Cleanup public schema if installed before release 0.28
DROP VIEW IF EXISTS public.m_v_intervention CASCADE;
DROP VIEW IF EXISTS gestion.m_v_intervention CASCADE;
DROP VIEW IF EXISTS gestion.v_interventions CASCADE;
DROP VIEW IF EXISTS public.m_v_chantier;
DROP VIEW IF EXISTS gestion.m_v_chantier;
DROP VIEW IF EXISTS gestion.v_projects;