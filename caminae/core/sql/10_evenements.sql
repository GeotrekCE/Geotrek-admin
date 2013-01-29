-------------------------------------------------------------------------------
-- Add spatial index (will boost spatial filters)
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS evenements_geom_idx;
DROP INDEX IF EXISTS e_t_evenement_geom_idx;
CREATE INDEX e_t_evenement_geom_idx ON e_t_evenement USING gist(geom);


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


-------------------------------------------------------------------------------
-- Update geometry of an "evenement"
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_geometry_of_evenement(eid integer) RETURNS void AS $$
DECLARE
    egeom geometry;
    lines_only boolean;
    points_only boolean;
    t_count integer;
    t_offset float;

    t_start float;
    t_end float;
    t_geom geometry;
    tomerge geometry[];
BEGIN
    -- See what kind of topology we have
    SELECT bool_and(et.pk_debut != et.pk_fin), bool_and(et.pk_debut = et.pk_fin), count(*)
        INTO lines_only, points_only, t_count
        FROM e_r_evenement_troncon et
        WHERE et.evenement = eid;

    -- /!\ linear offset (start and end point) are given as a fraction of the
    -- 2D-length in Postgis. Since we are working on 3D geometry, it could lead
    -- to unexpected results.
    -- January 2013 : It does indeed.

    RAISE NOTICE 'update_geometry_of_evenement (lines_only:% points_only:% t_count:%)', lines_only, points_only, t_count;

    IF t_count = 0 THEN
        -- No more troncons, close this topology
        UPDATE e_t_evenement SET geom = NULL, longueur = 0 WHERE id = eid;
    ELSIF (NOT lines_only AND t_count = 1) OR points_only THEN
        -- Special case: the topology describe a point on the path
        -- Note: We are faking a M-geometry in order to use LocateAlong.
        -- This is handy because this function includes an offset parameter
        -- which could be otherwise diffcult to handle.
        SELECT geom, decallage INTO egeom, t_offset FROM e_t_evenement e WHERE e.id = eid;

        IF t_offset = 0 OR egeom IS NULL OR ST_IsEmpty(egeom) THEN
            SELECT ST_GeometryN(ST_LocateAlong(ST_AddMeasure(ST_Force_2D(t.geom), 0, 1), et.pk_debut, e.decallage), 1)
                INTO egeom
                FROM e_t_evenement e, e_r_evenement_troncon et, l_t_troncon t
                WHERE e.id = eid AND et.evenement = e.id AND et.troncon = t.id;
        END IF;
        UPDATE e_t_evenement SET geom = add_point_elevation(egeom), longueur = 0 WHERE id = eid;
    ELSE

        -- Regular case: the topology describe a line

        -- NOTE: LineMerge and Line_Substring work on X and Y only. If two
        -- points in the line have the same X/Y but a different Z, these
        -- functions will see only on point. --> No problem in mountain path management.
        FOR t_offset, t_start, t_end, t_geom IN SELECT e.decallage, et.pk_debut, et.pk_fin, t.geom
               FROM e_t_evenement e, e_r_evenement_troncon et, l_t_troncon t
               WHERE e.id = eid AND et.evenement = e.id AND et.troncon = t.id
                 AND et.pk_debut != et.pk_fin
               ORDER BY et.ordre  -- /!\ We suppose that evenement_troncons were created in the right order
        LOOP
            tomerge := array_append(tomerge, ST_Smart_Line_Substring(t_geom, t_start, t_end));
        END LOOP;
        -- egeom := ft_Smart_MakeLine(tomerge);
        egeom := ST_Union(tomerge);
        -- Add some offset if necessary.
        IF t_offset > 0 THEN
            egeom := ST_GeometryN(ST_LocateBetween(ST_AddMeasure(egeom, 0, 1), 0, 1, t_offset), 1);
        END IF;
        UPDATE e_t_evenement SET geom = ST_Force_3DZ(egeom), longueur = ST_3DLength(egeom) WHERE id = eid;
    END IF;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- Update geometry when offset change
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS e_t_evenement_offset_u_tgr ON e_t_evenement;

CREATE OR REPLACE FUNCTION update_evenement_geom_when_offset_changes() RETURNS trigger AS $$
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
