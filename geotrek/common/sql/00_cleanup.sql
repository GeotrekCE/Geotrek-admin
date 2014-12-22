-- Cleanup public schema if installed before release 0.28
DROP FUNCTION IF EXISTS public.ft_date_insert() CASCADE;
DROP FUNCTION IF EXISTS public.ft_date_update() CASCADE;
