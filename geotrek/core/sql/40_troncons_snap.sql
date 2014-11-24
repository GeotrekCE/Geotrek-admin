DROP TRIGGER IF EXISTS l_t_troncon_00_snap_geom_iu_tgr ON l_t_troncon;

CREATE OR REPLACE FUNCTION troncons_snap_extremities() RETURNS trigger AS $$
DECLARE
    linestart geometry;
    lineend geometry;
    other geometry;
    result geometry;
    newline geometry[];
    d float8;

    DISTANCE float8;
BEGIN
    DISTANCE := {{PATH_SNAPPING_DISTANCE}};

    linestart := ST_StartPoint(NEW.geom);
    lineend := ST_EndPoint(NEW.geom);

    result := NULL;
    SELECT ST_ClosestPoint(geom, linestart), geom INTO result, other
      FROM l_t_troncon
      WHERE geom && ST_Buffer(NEW.geom, DISTANCE * 2)
        AND id != NEW.id
        AND ST_Distance(geom, linestart) < DISTANCE
      ORDER BY ST_Distance(geom, linestart)
      LIMIT 1;

    IF result IS NULL THEN
        result := linestart;
    ELSE
        d := DISTANCE;
        FOR i IN 1..ST_NPoints(other) LOOP
            IF ST_Distance(result, ST_PointN(other, i)) < DISTANCE AND ST_Distance(result, ST_PointN(other, i)) < d THEN
                d := ST_Distance(result, ST_PointN(other, i));
                result := ST_PointN(other, i);
            END IF;
        END LOOP;
        IF NOT ST_Equals(linestart, result) THEN
            RAISE NOTICE 'Snapped start % to %, from %', ST_AsText(linestart), ST_AsText(result), ST_AsText(other);
        END IF;
    END IF;
    newline := array_append(newline, result);

    FOR i IN 2..ST_NPoints(NEW.geom)-1 LOOP
        newline := array_append(newline, ST_PointN(NEW.geom, i));
    END LOOP;

    result := NULL;
    SELECT ST_ClosestPoint(geom, lineend), geom INTO result, other

      FROM l_t_troncon
      WHERE geom && ST_Buffer(NEW.geom, DISTANCE * 2)
        AND id != NEW.id
        AND ST_Distance(geom, lineend) < DISTANCE
      ORDER BY ST_Distance(geom, lineend)
      LIMIT 1;
    IF result IS NULL THEN
        result := lineend;
    ELSE
        d := DISTANCE;
        FOR i IN 1..ST_NPoints(other) LOOP
            IF ST_Distance(result, ST_PointN(other, i)) < DISTANCE AND ST_Distance(result, ST_PointN(other, i)) < d THEN
                d := ST_Distance(result, ST_PointN(other, i));
                result := ST_PointN(other, i);
            END IF;
        END LOOP;
        IF NOT ST_Equals(lineend, result) THEN
            RAISE NOTICE 'Snapped end % to %, from %', ST_AsText(lineend), ST_AsText(result), ST_AsText(other);
        END IF;
    END IF;
    newline := array_append(newline, result);

    RAISE NOTICE 'New geom %', ST_AsText(ST_MakeLine(newline));
    NEW.geom := ST_MakeLine(newline);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l_t_troncon_00_snap_geom_iu_tgr
BEFORE INSERT OR UPDATE OF geom ON l_t_troncon
FOR EACH ROW EXECUTE PROCEDURE troncons_snap_extremities();
