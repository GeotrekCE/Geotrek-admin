-- Cleanup public schema if installed before release 0.28
DROP FUNCTION IF EXISTS public.ft_drape_line(geometry, integer) CASCADE;
DROP FUNCTION IF EXISTS public.add_point_elevation(geometry) CASCADE;
DROP FUNCTION IF EXISTS public.ft_elevation_infos(geometry) CASCADE;
DROP FUNCTION IF EXISTS public.ft_elevation_infos_with_3d(geometry) CASCADE;