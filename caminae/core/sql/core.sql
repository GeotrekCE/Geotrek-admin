-------------------------------------------------------------------------------
-- Date functions (wiil be used for many tables)
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
-- Troncons
-------------------------------------------------------------------------------

-- Add spatial index (will boost spatial filters)

DROP INDEX IF EXISTS troncons_geom_idx;
CREATE INDEX troncons_geom_idx ON troncons USING gist(geom);

DROP INDEX IF EXISTS troncons_geom_cadastre_idx;
CREATE INDEX troncons_geom_cadastre_idx ON troncons USING gist(geom_cadastre);

-- Keep dates up-to-date

DROP TRIGGER IF EXISTS troncons_date_insert_tgr ON troncons;
CREATE TRIGGER troncons_date_insert_tgr
    BEFORE INSERT ON troncons
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

DROP TRIGGER IF EXISTS troncons_date_update_tgr ON troncons;
CREATE TRIGGER troncons_date_update_tgr
    BEFORE INSERT OR UPDATE ON troncons
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

-- Automatic link between Troncon and Commune/Zonage/Secteur

DROP TRIGGER IF EXISTS troncons_couches_sig_tgr ON troncons;

CREATE OR REPLACE FUNCTION lien_auto_troncon_couches_sig() RETURNS trigger AS $$
DECLARE
    rec record;
    tab varchar;
    eid integer;
BEGIN
    -- Remove obsolete evenement
    IF TG_OP IN ('DELETE', 'UPDATE') THEN
        FOREACH tab IN ARRAY ARRAY[['commune', 'secteur', 'zonage']]
        LOOP
            FOR rec IN EXECUTE 'DELETE FROM '|| quote_ident(tab) ||' t USING evenements_troncons e WHERE t.evenement = e.evenement AND e.troncon = $1 RETURNING e.evenement AS id' USING OLD.id
            LOOP
                DELETE FROM evenements_troncons WHERE evenement = rec.id;
                DELETE FROM evenements WHERE id = rec.id;
            END LOOP;
        END LOOP;
    END IF;
    -- Add new evenement
    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        -- Note: Column names differ between commune, secteur and zonage, we can not use an elegant loop as above.

        -- Commune
        FOR rec IN EXECUTE 'SELECT insee as id, ST_Line_Locate_Point($1, ST_StartPoint(ST_Intersection(geom, $1))) as pk_debut, ST_Line_Locate_Point($1, ST_EndPoint(ST_Intersection(geom, $1))) as pk_fin FROM couche_communes WHERE ST_Intersects(geom, $1)' USING NEW.geom
        LOOP
            INSERT INTO evenements (date_insert, date_update, kind_id, decallage, longueur, geom) VALUES (now(), now(), 2, 0, 0, NEW.geom) RETURNING id INTO eid;
            INSERT INTO evenements_troncons (troncon, evenement, pk_debut, pk_fin) VALUES (NEW.id, eid, rec.pk_debut, rec.pk_fin);
            INSERT INTO commune (evenement, city_id) VALUES (eid, rec.id);
        END LOOP;

        -- Secteur
        FOR rec IN EXECUTE 'SELECT code_secteur as id, ST_Line_Locate_Point($1, ST_StartPoint(ST_Intersection(geom, $1))) as pk_debut, ST_Line_Locate_Point($1, ST_EndPoint(ST_Intersection(geom, $1))) as pk_fin FROM couche_secteurs WHERE ST_Intersects(geom, $1)' USING NEW.geom
        LOOP
            INSERT INTO evenements (date_insert, date_update, kind_id, decallage, longueur, geom) VALUES (now(), now(), 3, 0, 0, NEW.geom) RETURNING id INTO eid;
            INSERT INTO evenements_troncons (troncon, evenement, pk_debut, pk_fin) VALUES (NEW.id, eid, rec.pk_debut, rec.pk_fin);
            INSERT INTO secteur (evenement, district_id) VALUES (eid, rec.id);
        END LOOP;

        -- Zonage
        FOR rec IN EXECUTE 'SELECT code_zonage as id, ST_Line_Locate_Point($1, ST_StartPoint(ST_Intersection(geom, $1))) as pk_debut, ST_Line_Locate_Point($1, ST_EndPoint(ST_Intersection(geom, $1))) as pk_fin FROM couche_zonage_reglementaire WHERE ST_Intersects(geom, $1)' USING NEW.geom
        LOOP
            INSERT INTO evenements (date_insert, date_update, kind_id, decallage, longueur, geom) VALUES (now(), now(), 4, 0, 0, NEW.geom) RETURNING id INTO eid;
            INSERT INTO evenements_troncons (troncon, evenement, pk_debut, pk_fin) VALUES (NEW.id, eid, rec.pk_debut, rec.pk_fin);
            INSERT INTO zonage (evenement, restricted_area_id) VALUES (eid, rec.id);
        END LOOP;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER troncons_couches_sig_tgr
AFTER INSERT OR UPDATE OR DELETE ON troncons
FOR EACH ROW EXECUTE PROCEDURE lien_auto_troncon_couches_sig();

-------------------------------------------------------------------------------
-- Evenements
-------------------------------------------------------------------------------

-- Add spatial index (will boost spatial filters)

DROP INDEX IF EXISTS evenements_geom_idx;
CREATE INDEX evenements_geom_idx ON evenements USING gist(geom);

-- Keep dates up-to-date

DROP TRIGGER IF EXISTS evenements_date_insert_tgr ON evenements;
CREATE TRIGGER evenements_date_insert_tgr
    BEFORE INSERT ON evenements
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

DROP TRIGGER IF EXISTS evenements_date_update_tgr ON evenements;
CREATE TRIGGER evenements_date_update_tgr
    BEFORE INSERT OR UPDATE ON evenements
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

