-------------------------------------------------------------------------------
-- Add spatial index (will boost spatial filters)
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS evenements_geom_idx;
DROP INDEX IF EXISTS e_t_evenement_geom_idx;
CREATE INDEX e_t_evenement_geom_idx ON e_t_evenement USING gist(geom);


ALTER TABLE e_t_evenement ALTER COLUMN longueur SET DEFAULT 0.0;
ALTER TABLE e_t_evenement ALTER COLUMN pente SET DEFAULT 0.0;
ALTER TABLE e_t_evenement ALTER COLUMN altitude_minimum SET DEFAULT 0;
ALTER TABLE e_t_evenement ALTER COLUMN altitude_maximum SET DEFAULT 0;
ALTER TABLE e_t_evenement ALTER COLUMN denivelee_positive SET DEFAULT 0;
ALTER TABLE e_t_evenement ALTER COLUMN denivelee_negative SET DEFAULT 0;


ALTER TABLE e_t_evenement DROP CONSTRAINT IF EXISTS e_t_evenement_geom_not_empty;
ALTER TABLE e_t_evenement ADD CONSTRAINT e_t_evenement_geom_not_empty CHECK (supprime OR (geom IS NOT NULL));


-------------------------------------------------------------------------------
-- Keep dates up-to-date
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS e_t_evenement_date_insert_tgr ON e_t_evenement;
CREATE TRIGGER e_t_evenement_date_insert_tgr
    BEFORE INSERT ON e_t_evenement
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

DROP TRIGGER IF EXISTS e_t_evenement_date_update_tgr ON e_t_evenement;
CREATE TRIGGER e_t_evenement_date_update_tgr
    BEFORE INSERT OR UPDATE ON e_t_evenement
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

---------------------------------------------------------------------
-- Make sure cache key (base on lastest updated) is refresh on DELETE
---------------------------------------------------------------------

DROP TRIGGER IF EXISTS e_t_evenement_latest_updated_d_tgr ON e_t_evenement;

CREATE OR REPLACE FUNCTION geotrek.evenement_latest_updated_d() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
BEGIN
    -- Touch latest path
    UPDATE e_t_evenement SET date_update = NOW()
    WHERE id IN (SELECT id FROM e_t_evenement ORDER BY date_update DESC LIMIT 1);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER e_t_evenement_latest_updated_d_tgr
AFTER DELETE ON e_t_evenement
FOR EACH ROW EXECUTE PROCEDURE evenement_latest_updated_d();


-------------------------------------------------------------------------------
-- Update geometry of an "evenement"
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION geotrek.update_geometry_of_evenement(eid integer) RETURNS void AS $$
DECLARE
    egeom geometry;
    egeom_3d geometry;
    lines_only boolean;
    points_only boolean;
    position_point float;
    elevation elevation_infos;
    t_count integer;
    t_offset float;

    t_start float;
    t_end float;
    t_geom geometry;
    t_geom_3d geometry;
    tomerge geometry[];
    tomerge_3d geometry[];
BEGIN
    -- If Geotrek-light, don't do anything
    IF NOT {{TREKKING_TOPOLOGY_ENABLED}} THEN
        RETURN;
    END IF;

    -- See what kind of topology we have
    SELECT bool_and(et.pk_debut != et.pk_fin), bool_and(et.pk_debut = et.pk_fin), count(*)
        INTO lines_only, points_only, t_count
        FROM e_r_evenement_troncon et
        WHERE et.evenement = eid;

    -- /!\ linear offset (start and end point) are given as a fraction of the
    -- 2D-length in Postgis. Since we are working on 3D geometry, it could lead
    -- to unexpected results.
    -- January 2013 : It does indeed.

    -- RAISE NOTICE 'update_geometry_of_evenement (lines_only:% points_only:% t_count:%)', lines_only, points_only, t_count;

    IF t_count = 0 THEN
        -- No more troncons, close this topology
        UPDATE e_t_evenement SET supprime = true, geom = NULL, longueur = 0 WHERE id = eid;
    ELSIF (NOT lines_only AND t_count = 1) OR points_only THEN
        -- Special case: the topology describe a point on the path
        -- Note: We are faking a M-geometry in order to use LocateAlong.
        -- This is handy because this function includes an offset parameter
        -- which could be otherwise diffcult to handle.
        SELECT geom, decallage INTO egeom, t_offset FROM e_t_evenement e WHERE e.id = eid;
        -- RAISE NOTICE '% % % %', (t_offset = 0), (egeom IS NULL), (ST_IsEmpty(egeom)), (ST_X(egeom) = 0 AND ST_Y(egeom) = 0);
        IF t_offset = 0 OR egeom IS NULL OR ST_IsEmpty(egeom) OR (ST_X(egeom) = 0 AND ST_Y(egeom) = 0) THEN
            -- ST_LocateAlong can give no point when we try to get the startpoint or the endpoint of the line
            SELECT et.pk_debut INTO position_point FROM e_r_evenement_troncon et WHERE et.evenement = eid;
            IF (position_point = 0) THEN
                SELECT ST_StartPoint(t.geom) INTO egeom
                FROM e_t_evenement e, e_r_evenement_troncon et, l_t_troncon t
                WHERE e.id = eid AND et.evenement = e.id AND et.troncon = t.id;
            ELSIF (position_point = 1) THEN
                SELECT ST_EndPoint(t.geom) INTO egeom
                FROM e_t_evenement e, e_r_evenement_troncon et, l_t_troncon t
                WHERE e.id = eid AND et.evenement = e.id AND et.troncon = t.id;
            ELSE
                SELECT ST_GeometryN(ST_LocateAlong(ST_AddMeasure(ST_Force2D(t.geom), 0, 1), et.pk_debut, e.decallage), 1)
                    INTO egeom
                    FROM e_t_evenement e, e_r_evenement_troncon et, l_t_troncon t
                    WHERE e.id = eid AND et.evenement = e.id AND et.troncon = t.id;
            END IF;
        END IF;

        egeom_3d := egeom;
    ELSE
        -- Regular case: the topology describe a line
        -- NOTE: LineMerge and Line_Substring work on X and Y only. If two
        -- points in the line have the same X/Y but a different Z, these
        -- functions will see only on point. --> No problem in mountain path management.
        FOR t_offset, t_geom, t_geom_3d IN SELECT e.decallage, ST_SmartLineSubstring(t.geom, et.pk_debut, et.pk_fin),
                                                               ST_SmartLineSubstring(t.geom_3d, et.pk_debut, et.pk_fin)
               FROM e_t_evenement e, e_r_evenement_troncon et, l_t_troncon t
               WHERE e.id = eid AND et.evenement = e.id AND et.troncon = t.id
                 AND et.pk_debut != et.pk_fin
               ORDER BY et.ordre, et.id  -- /!\ We suppose that evenement_troncons were created in the right order
        LOOP
            tomerge := array_append(tomerge, t_geom);
            tomerge_3d := array_append(tomerge_3d, t_geom_3d);
        END LOOP;

        egeom := ft_Smart_MakeLine(tomerge);
        egeom_3d := ft_Smart_MakeLine(tomerge_3d);
        -- Add some offset if necessary.
        IF t_offset != 0 THEN
            egeom := ST_GeometryN(ST_LocateBetween(ST_AddMeasure(egeom, 0, 1), 0, 1, t_offset), 1);
            egeom_3d := ST_GeometryN(ST_LocateBetween(ST_AddMeasure(egeom_3d, 0, 1), 0, 1, t_offset), 1);
        END IF;
    END IF;

    IF t_count > 0 THEN
        SELECT * FROM ft_elevation_infos_evenement(egeom_3d, {{ALTIMETRIC_PROFILE_STEP}}) INTO elevation;
        UPDATE e_t_evenement SET geom = ST_Force2D(egeom),
                                 geom_3d = elevation.draped,
                                 longueur = ST_3DLength(elevation.draped),
                                 pente = elevation.slope,
                                 altitude_minimum = elevation.min_elevation,
                                 altitude_maximum = elevation.max_elevation,
                                 denivelee_positive = elevation.positive_gain,
                                 denivelee_negative = elevation.negative_gain
                             WHERE id = eid;
    END IF;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- Update geometry when offset change
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS e_t_evenement_offset_u_tgr ON e_t_evenement;

CREATE OR REPLACE FUNCTION geotrek.update_evenement_geom_when_offset_changes() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    -- Note: We are using an "after" trigger here because the function below
    -- takes topology id as an argument and emits its own SQL queries to read
    -- and write data.
    -- Since the evenement to be modified is available in NEW, we could improve
    -- performance with some refactoring.

    PERFORM update_geometry_of_evenement(NEW.id);

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER e_t_evenement_offset_u_tgr
AFTER UPDATE OF decallage ON e_t_evenement
FOR EACH ROW EXECUTE PROCEDURE update_evenement_geom_when_offset_changes();

-------------------------------------------------------------------------------
-- Update altimetry when geom change (Geotrek-light)
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS e_t_evenement_geom_iu_tgr ON e_t_evenement;

CREATE OR REPLACE FUNCTION geotrek.evenement_elevation_iu() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    elevation elevation_infos;
BEGIN
    IF {{TREKKING_TOPOLOGY_ENABLED}} THEN
        RETURN NEW;
    END IF;
    SELECT * FROM ft_elevation_infos_evenement(NEW.geom, {{ALTIMETRIC_PROFILE_STEP}}) INTO elevation;
    -- Update path geometry
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

CREATE TRIGGER e_t_evenement_geom_iu_tgr
BEFORE INSERT OR UPDATE OF geom ON e_t_evenement
FOR EACH ROW EXECUTE PROCEDURE evenement_elevation_iu();
