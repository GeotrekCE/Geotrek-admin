-- Cleanup public schema if installed before release 0.28
DROP VIEW IF EXISTS public.m_v_intervention CASCADE;
DROP VIEW IF EXISTS public.m_v_chantier;
