-------------------------------------------------------------------------------
-- Add spatial index (will boost spatial filters)
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS troncons_geom_idx;
CREATE INDEX troncons_geom_idx ON troncons USING gist(geom);

DROP INDEX IF EXISTS troncons_start_point_idx;
CREATE INDEX troncons_start_point_idx ON troncons USING gist(ST_StartPoint(geom));

DROP INDEX IF EXISTS troncons_end_point_idx;
CREATE INDEX troncons_end_point_idx ON troncons USING gist(ST_EndPoint(geom));

DROP INDEX IF EXISTS troncons_geom_cadastre_idx;
CREATE INDEX troncons_geom_cadastre_idx ON troncons USING gist(geom_cadastre);


-------------------------------------------------------------------------------
-- Keep dates up-to-date
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS troncons_date_insert_tgr ON troncons;
CREATE TRIGGER troncons_date_insert_tgr
    BEFORE INSERT ON troncons
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

DROP TRIGGER IF EXISTS troncons_date_update_tgr ON troncons;
CREATE TRIGGER troncons_date_update_tgr
    BEFORE INSERT OR UPDATE ON troncons
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();


-------------------------------------------------------------------------------
-- Automatic link between Troncon and Commune/Zonage/Secteur
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS troncons_couches_sig_iu_tgr ON troncons;

CREATE OR REPLACE FUNCTION lien_auto_troncon_couches_sig_iu() RETURNS trigger AS $$
DECLARE
    rec record;
    tab varchar;
    eid integer;
BEGIN
    -- Remove obsolete evenement
    IF TG_OP = 'UPDATE' THEN
        -- Related evenement/zonage/secteur/commune will be cleared by another trigger
        DELETE FROM evenements_troncons et USING zonage z WHERE et.troncon = OLD.id AND et.evenement = z.evenement;
        DELETE FROM evenements_troncons et USING secteur s WHERE et.troncon = OLD.id AND et.evenement = s.evenement;
        DELETE FROM evenements_troncons et USING commune c WHERE et.troncon = OLD.id AND et.evenement = c.evenement;
    END IF;

    -- Add new evenement
    -- Note: Column names differ between commune, secteur and zonage, we can not use an elegant loop.

    -- Commune
    FOR rec IN EXECUTE 'SELECT insee as id, ST_Line_Locate_Point($1, ST_StartPoint(ST_Intersection(geom, $1))) as pk_debut, ST_Line_Locate_Point($1, ST_EndPoint(ST_Intersection(geom, $1))) as pk_fin FROM couche_communes WHERE ST_Intersects(geom, $1)' USING NEW.geom
    LOOP
        INSERT INTO evenements (date_insert, date_update, kind, decallage, longueur, geom) VALUES (now(), now(), 'CITYEDGE', 0, 0, NEW.geom) RETURNING id INTO eid;
        INSERT INTO evenements_troncons (troncon, evenement, pk_debut, pk_fin) VALUES (NEW.id, eid, rec.pk_debut, rec.pk_fin);
        INSERT INTO commune (evenement, city_id) VALUES (eid, rec.id);
    END LOOP;

    -- Secteur
    FOR rec IN EXECUTE 'SELECT id, ST_Line_Locate_Point($1, ST_StartPoint(ST_Intersection(geom, $1))) as pk_debut, ST_Line_Locate_Point($1, ST_EndPoint(ST_Intersection(geom, $1))) as pk_fin FROM couche_secteurs WHERE ST_Intersects(geom, $1)' USING NEW.geom
    LOOP
        INSERT INTO evenements (date_insert, date_update, kind, decallage, longueur, geom) VALUES (now(), now(), 'DISTRICTEDGE', 0, 0, NEW.geom) RETURNING id INTO eid;
        INSERT INTO evenements_troncons (troncon, evenement, pk_debut, pk_fin) VALUES (NEW.id, eid, rec.pk_debut, rec.pk_fin);
        INSERT INTO secteur (evenement, district_id) VALUES (eid, rec.id);
    END LOOP;

    -- Zonage
    FOR rec IN EXECUTE 'SELECT id, ST_Line_Locate_Point($1, ST_StartPoint(ST_Intersection(geom, $1))) as pk_debut, ST_Line_Locate_Point($1, ST_EndPoint(ST_Intersection(geom, $1))) as pk_fin FROM couche_zonage_reglementaire WHERE ST_Intersects(geom, $1)' USING NEW.geom
    LOOP
        INSERT INTO evenements (date_insert, date_update, kind, decallage, longueur, geom) VALUES (now(), now(), 'RESTRICTEDAREAEDGE', 0, 0, NEW.geom) RETURNING id INTO eid;
        INSERT INTO evenements_troncons (troncon, evenement, pk_debut, pk_fin) VALUES (NEW.id, eid, rec.pk_debut, rec.pk_fin);
        INSERT INTO zonage (evenement, restricted_area_id) VALUES (eid, rec.id);
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER troncons_couches_sig_iu_tgr
AFTER INSERT OR UPDATE OF geom ON troncons
FOR EACH ROW EXECUTE PROCEDURE lien_auto_troncon_couches_sig_iu();


-------------------------------------------------------------------------------
-- Update geometry of related topologies
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS troncons_evenements_geom_u_tgr ON troncons;

CREATE OR REPLACE FUNCTION update_evenement_geom_when_troncon_changes() RETURNS trigger AS $$
DECLARE
    eid integer;
    egeom geometry;
    linear_offset float;
    side_offset float;
BEGIN
    -- Geometry of linear topologies are always updated
    -- Geometry of point topologies are updated if offset = 0
    FOR eid IN SELECT DISTINCT e.id
               FROM evenements_troncons et, evenements e
               WHERE et.troncon = NEW.id AND et.evenement = e.id AND (et.pk_debut != et.pk_fin OR e.decallage = 0.0)
    LOOP
        PERFORM update_geometry_of_evenement(eid);
    END LOOP;

    -- Special case of point geometries with offset != 0
    FOR eid, egeom IN SELECT e.id, e.geom
               FROM evenements_troncons et, evenements e
               WHERE et.troncon = NEW.id AND et.evenement = e.id AND et.pk_debut = et.pk_fin AND e.decallage != 0.0
    LOOP
        SELECT * INTO linear_offset, side_offset FROM ST_InterpolateAlong(NEW.geom, egeom) AS (position float, distance float);
        UPDATE evenements SET decallage = side_offset WHERE id = eid;
        UPDATE evenements_troncons SET pk_debut = linear_offset, pk_fin = linear_offset WHERE evenement = eid AND troncon = NEW.id;
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER troncons_evenements_geom_u_tgr
AFTER UPDATE OF geom ON troncons
FOR EACH ROW EXECUTE PROCEDURE update_evenement_geom_when_troncon_changes();


-------------------------------------------------------------------------------
-- Ensure paths have valid geometries
-------------------------------------------------------------------------------

ALTER TABLE troncons DROP CONSTRAINT IF EXISTS troncons_geom_issimple;
ALTER TABLE troncons ADD CONSTRAINT troncons_geom_issimple CHECK (ST_IsSimple(geom));


-------------------------------------------------------------------------------
-- Compute elevation and elevation-based indicators
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS troncons_elevation_iu_tgr ON troncons;

CREATE OR REPLACE FUNCTION troncons_elevation_iu() RETURNS trigger AS $$
DECLARE
    num_points integer;
    current_point geometry;
    points3d geometry[];
    ele integer;
    last_ele integer;
    max_ele integer;
    min_ele integer;
    positive_gain integer := 0;
    negative_gain integer := 0;
BEGIN
    -- Ensure we have a DEM
    PERFORM * FROM raster_columns WHERE r_table_name = 'mnt';
    IF NOT FOUND THEN
        NEW.longueur := ST_Length(NEW.geom);
        -- NOTE: Other indicators have safe default values
        RETURN NEW;
    END IF;

    -- Obtain point number
    num_points := ST_NumPoints(NEW.geom);

    -- Iterate over points (i.e. path vertices)
    FOR i IN 1..num_points LOOP
        -- Obtain current point
        current_point := ST_PointN(NEW.geom, i);

        -- Obtain elevation
        SELECT ST_Value(rast, 1, current_point) INTO ele FROM mnt WHERE ST_Intersects(rast, current_point);
        IF NOT FOUND THEN
            ele := 0;
        END IF;

        -- Store new 3D points
        points3d := array_append(points3d, ST_MakePoint(ST_X(current_point), ST_Y(current_point), ele));

        -- Compute indicators
        min_ele := least(coalesce(min_ele, ele), ele);
        max_ele := greatest(coalesce(max_ele, ele), ele);
        positive_gain := positive_gain + greatest(ele - coalesce(last_ele, ele), 0);
        negative_gain := negative_gain + least(ele - coalesce(last_ele, ele), 0);
        last_ele := ele;
    END LOOP;

    -- Update path geometry
    NEW.geom := ST_SetSRID(ST_MakeLine(points3d), ST_SRID(NEW.geom));

    -- Update path indicators
    NEW.longueur := ST_3DLength(NEW.geom);
    NEW.altitude_minimum := min_ele;
    NEW.altitude_maximum := max_ele;
    NEW.denivelee_positive := positive_gain;
    NEW.denivelee_negative := negative_gain;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER troncons_elevation_iu_tgr
BEFORE INSERT OR UPDATE OF geom ON troncons
FOR EACH ROW EXECUTE PROCEDURE troncons_elevation_iu();
