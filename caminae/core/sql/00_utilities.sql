-------------------------------------------------------------------------------
-- Date trigger functions
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ft_date_insert() RETURNS trigger AS $$
BEGIN
    NEW.date_insert := statement_timestamp() AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION ft_date_update() RETURNS trigger AS $$
BEGIN
    NEW.date_update := statement_timestamp() AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-------------------------------------------------------------------------------
-- Length trigger function
-------------------------------------------------------------------------------

DROP FUNCTION IF EXISTS ft_longueur() CASCADE;


-------------------------------------------------------------------------------
-- Interpolate along : the opposite of ST_LocateAlong
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ST_InterpolateAlong(line geometry, point geometry) RETURNS RECORD AS $$
DECLARE 
  tuple RECORD;
BEGIN
    SELECT ST_Line_Locate_Point(line, point) AS position, 
           ST_Distance(point, ST_Line_Interpolate_Point(line, ST_Line_Locate_Point(line, point))) AS offset
    INTO tuple;
    RETURN tuple;
END;
$$ LANGUAGE plpgsql;
