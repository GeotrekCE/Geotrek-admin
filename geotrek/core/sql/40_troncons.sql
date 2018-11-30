-------------------------------------------------------------------------------
-- Force Path default values
-- Django does not translate model default value to
-- database default column values.
-------------------------------------------------------------------------------

ALTER TABLE l_t_troncon ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE l_t_troncon ALTER COLUMN date_update SET DEFAULT now();
ALTER TABLE l_t_troncon ALTER COLUMN depart SET DEFAULT '';
ALTER TABLE l_t_troncon ALTER COLUMN arrivee SET DEFAULT '';
ALTER TABLE l_t_troncon ALTER COLUMN valide SET DEFAULT false;
ALTER TABLE l_t_troncon ALTER COLUMN visible SET DEFAULT true;



-------------------------------------------------------------------------------
-- Add spatial index (will boost spatial filters)
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS troncons_geom_idx;
DROP INDEX IF EXISTS l_t_troncon_geom_idx;
CREATE INDEX l_t_troncon_geom_idx ON l_t_troncon USING gist(geom);

DROP INDEX IF EXISTS troncons_start_point_idx;
DROP INDEX IF EXISTS l_t_troncon_start_point_idx;
CREATE INDEX l_t_troncon_start_point_idx ON l_t_troncon USING gist(ST_StartPoint(geom));

DROP INDEX IF EXISTS troncons_end_point_idx;
DROP INDEX IF EXISTS l_t_troncon_end_point_idx;
CREATE INDEX l_t_troncon_end_point_idx ON l_t_troncon USING gist(ST_EndPoint(geom));

DROP INDEX IF EXISTS troncons_geom_cadastre_idx;
DROP INDEX IF EXISTS l_t_troncon_geom_cadastre_idx;
CREATE INDEX l_t_troncon_geom_cadastre_idx ON l_t_troncon USING gist(geom_cadastre);

DROP INDEX IF EXISTS l_t_troncon_geom_3d_idx;
CREATE INDEX l_t_troncon_geom_3d_idx ON l_t_troncon USING gist(geom_3d);

-------------------------------------------------------------------------------
-- Keep dates up-to-date
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS l_t_troncon_date_insert_tgr ON l_t_troncon;
CREATE TRIGGER l_t_troncon_date_insert_tgr
    BEFORE INSERT ON l_t_troncon
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

DROP TRIGGER IF EXISTS l_t_troncon_date_update_tgr ON l_t_troncon;
CREATE TRIGGER l_t_troncon_date_update_tgr
    BEFORE INSERT OR UPDATE ON l_t_troncon
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();


-------------------------------------------------------------------------------
-- Check overlapping paths
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION geotrek.check_path_not_overlap(pid integer, line geometry) RETURNS BOOL AS $$
DECLARE
    t_count integer;
    tolerance float;
BEGIN
    -- Note: I gave up with the idea of checking almost overlap/touch.

    -- tolerance := 1.0;
    -- Crossing and extremity touching is OK.
    -- Overlapping and --almost overlapping-- is KO.
    SELECT COUNT(*) INTO t_count
    FROM l_t_troncon
    WHERE pid != id
      AND ST_GeometryType(ST_intersection(geom, line)) IN ('ST_LineString', 'ST_MultiLineString');
      -- not extremity touching
      -- AND ST_Touches(geom, line) = false
      -- not crossing
      -- AND ST_GeometryType(ST_intersection(geom, line)) NOT IN ('ST_Point', 'ST_MultiPoint')
      -- overlap is a line
      -- AND ST_GeometryType(ST_intersection(geom, ST_buffer(line, tolerance))) IN ('ST_LineString', 'ST_MultiLineString')
      -- not almost touching, at most twice
      -- AND       ST_Length(ST_intersection(geom, ST_buffer(line, tolerance))) > (4 * tolerance);
    RETURN t_count = 0;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- Update geometry of related topologies
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS l_t_troncon_evenements_geom_u_tgr ON l_t_troncon;
DROP TRIGGER IF EXISTS l_t_troncon_90_evenements_geom_u_tgr ON l_t_troncon;


CREATE OR REPLACE FUNCTION geotrek.update_evenement_geom_when_troncon_changes_nt() RETURNS void AS $$
DECLARE
    tgeom geometry;
    tgeom3d geometry;
    tid integer;
    elevation elevation_infos;
BEGIN
    FOR tgeom, tgeom3d, tid IN SELECT t.geom, t.geom_3d, t.id FROM l_t_troncon t
    LOOP
        SELECT * FROM ft_elevation_infos(tgeom, {{ALTIMETRIC_PROFILE_STEP}}) INTO elevation;
        UPDATE l_t_troncon AS t SET geom_3d = elevation.draped, longueur = ST_3DLength(elevation.draped), pente = elevation.slope, altitude_minimum = elevation.min_elevation, altitude_maximum = elevation.max_elevation, denivelee_positive = elevation.positive_gain, denivelee_negative = elevation.negative_gain WHERE t.id = tid;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION geotrek.update_evenement_geom_when_troncon_changes() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    eid integer;
    egeom geometry;
    linear_offset float;
    side_offset float;
BEGIN
    -- Geometry of linear topologies are always updated
    -- Geometry of point topologies are updated if offset = 0
    FOR eid IN SELECT e.id
               FROM e_r_evenement_troncon et, e_t_evenement e
               WHERE et.troncon = NEW.id AND et.evenement = e.id
               GROUP BY e.id, e.decallage
               HAVING BOOL_OR(et.pk_debut != et.pk_fin) OR e.decallage = 0.0
    LOOP
        PERFORM update_geometry_of_evenement(eid);
    END LOOP;

    -- Special case of point geometries with offset != 0
    FOR eid, egeom IN SELECT e.id, e.geom
               FROM e_r_evenement_troncon et, e_t_evenement e
               WHERE et.troncon = NEW.id AND et.evenement = e.id
               GROUP BY e.id, e.geom, e.decallage
               HAVING COUNT(et.id) = 1 AND BOOL_OR(et.pk_debut = et.pk_fin) AND e.decallage != 0.0
    LOOP
        SELECT * INTO linear_offset, side_offset FROM ST_InterpolateAlong(NEW.geom, egeom) AS (position float, distance float);
        UPDATE e_t_evenement SET decallage = side_offset WHERE id = eid;
        UPDATE e_r_evenement_troncon SET pk_debut = linear_offset, pk_fin = linear_offset WHERE evenement = eid AND troncon = NEW.id;
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l_t_troncon_90_evenements_geom_u_tgr
AFTER UPDATE OF geom ON l_t_troncon
FOR EACH ROW
WHEN (NOT (ST_Contains(ST_Buffer(NEW.geom,0.0001),OLD.geom) AND ST_Contains(ST_Buffer(OLD.geom,0.0001),New.geom)
AND ST_Contains(ST_Buffer(ST_StartPoint(NEW.geom), 0.0001),ST_StartPoint(OLD.geom)) AND NEW.id != OLD.id))
EXECUTE PROCEDURE update_evenement_geom_when_troncon_changes();
-- We check that geometry is not the same as before (we can't use ST_equals because it's not exactly the same with round)
-- We check also that geometry as not been reverse : If yes we do like usual
-- Finally we check if the ID changed : if the id changed it means we did a split.
-- Then we update all topologies

-------------------------------------------------------------------------------
-- Ensure paths have valid geometries
-------------------------------------------------------------------------------

ALTER TABLE l_t_troncon DROP CONSTRAINT IF EXISTS troncons_geom_issimple;

ALTER TABLE l_t_troncon DROP CONSTRAINT IF EXISTS l_t_troncon_geom_isvalid;
ALTER TABLE l_t_troncon ADD CONSTRAINT l_t_troncon_geom_isvalid CHECK (ST_IsValid(geom));

ALTER TABLE l_t_troncon DROP CONSTRAINT IF EXISTS l_t_troncon_geom_issimple;
ALTER TABLE l_t_troncon ADD CONSTRAINT l_t_troncon_geom_issimple CHECK (ST_IsSimple(geom));


-------------------------------------------------------------------------------
-- Compute elevation and elevation-based indicators
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS l_t_troncon_elevation_iu_tgr ON l_t_troncon;
DROP TRIGGER IF EXISTS l_t_troncon_10_elevation_iu_tgr ON l_t_troncon;
DROP TRIGGER IF EXISTS l_t_troncon_10_elevation_iu_tgr_update ON l_t_troncon;
DROP TRIGGER IF EXISTS l_t_troncon_10_elevation_iu_tgr_insert ON l_t_troncon;


CREATE OR REPLACE FUNCTION geotrek.elevation_troncon_iu() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    elevation elevation_infos;
BEGIN
    IF ST_IsEmpty(NEW.geom_3d) OR NEW.geom_3d IS NULL
    OR (NOT ST_Contains(ST_Buffer(ST_FORCE_2D(NEW.geom_3d),0.0001), NEW.geom)
    OR NOT ST_Contains(ST_Buffer(NEW.geom,0.0001), ST_FORCE_2D(NEW.geom_3d))
    OR NOT ST_Contains(ST_BUFFER(ST_STARTPOINT(NEW.geom), 0.0001), ST_STARTPOINT(NEW.geom_3d))) THEN
    -- We check that we have a 3d generated in troncon_split (generated with intersection_on_current only)
    -- We check also that geometry_3d is the same as geometry.
    -- If the condition IS TRUE : It means that the geom and geom_3d didn't change and geom was not reversed.
        SELECT * FROM ft_elevation_infos(NEW.geom, {{ALTIMETRIC_PROFILE_STEP}}) INTO elevation;
        RAISE NOTICE 'Add path geometry without 3d';
        -- Update path geometry
        NEW.geom_3d := elevation.draped;
        NEW.longueur := ST_3DLength(elevation.draped);
        NEW.pente := elevation.slope;
        NEW.altitude_minimum := elevation.min_elevation;
        NEW.altitude_maximum := elevation.max_elevation;
        NEW.denivelee_positive := elevation.positive_gain;
        NEW.denivelee_negative := elevation.negative_gain;
        RETURN NEW;
    END IF;
    SELECT * FROM ft_elevation_infos_with_3d(NEW.geom_3d, {{ALTIMETRIC_PROFILE_STEP}}) INTO elevation;
    -- Update path geometry
    RAISE NOTICE 'Update path geometry without 3d';
    NEW.geom_3d := elevation.draped;
    NEW.longueur := ST_3DLength(elevation.draped);
    NEW.pente := elevation.slope;
    NEW.altitude_minimum := elevation.min_elevation;
    NEW.altitude_maximum := elevation.max_elevation;
    NEW.denivelee_positive := elevation.positive_gain;
    NEW.denivelee_negative := elevation.negative_gain;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l_t_troncon_10_elevation_iu_tgr_update
BEFORE UPDATE OF geom ON l_t_troncon
FOR EACH ROW
WHEN (NOT (ST_Contains(ST_Buffer(NEW.geom,0.0001),OLD.geom) AND ST_Contains(ST_Buffer(OLD.geom,0.0001),NEW.geom)
AND ST_Contains(ST_Buffer(ST_STARTPOINT(NEW.geom), 0.0001), ST_ENDPOINT(OLD.geom))))
EXECUTE PROCEDURE elevation_troncon_iu();
-- We check that geometry is not the same as before (we can't use ST_equals because it's not exactly the same with round)
-- We check also that geometry as not been reverse
-- Then we get the elevation.

CREATE TRIGGER l_t_troncon_10_elevation_iu_tgr_insert
BEFORE INSERT ON l_t_troncon
FOR EACH ROW
EXECUTE PROCEDURE elevation_troncon_iu();

-------------------------------------------------------------------------------
-- Change status of related objects when paths are deleted
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS l_t_troncon_related_objects_d_tgr ON l_t_troncon;

CREATE OR REPLACE FUNCTION geotrek.troncons_related_objects_d() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
BEGIN
    -- Mark empty topologies as deleted
    UPDATE e_t_evenement e
        SET supprime = TRUE
        FROM e_r_evenement_troncon et
        WHERE et.evenement = e.id AND et.troncon = OLD.id AND NOT EXISTS(
            SELECT * FROM e_r_evenement_troncon
            WHERE evenement = e.id AND troncon != OLD.id
        );

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l_t_troncon_related_objects_d_tgr
BEFORE DELETE ON l_t_troncon
FOR EACH ROW EXECUTE PROCEDURE troncons_related_objects_d();


---------------------------------------------------------------------
-- Make sure cache key (base on lastest updated) is refresh on DELETE
---------------------------------------------------------------------

DROP TRIGGER IF EXISTS l_t_troncon_latest_updated_d_tgr ON l_t_troncon;

CREATE OR REPLACE FUNCTION geotrek.troncon_latest_updated_d() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
BEGIN
    -- Touch latest path
    UPDATE l_t_troncon SET date_update = NOW()
    WHERE id IN (SELECT id FROM l_t_troncon ORDER BY date_update DESC LIMIT 1);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l_t_troncon_latest_updated_d_tgr
AFTER DELETE ON l_t_troncon
FOR EACH ROW EXECUTE PROCEDURE troncon_latest_updated_d();
