SELECT create_schema_if_not_exist('zonage');

-------------------------------------------------------------------------------
-- Add spatial index (will boost spatial filters)
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS couche_communes_geom_idx;
DROP INDEX IF EXISTS l_commune_geom_idx;
CREATE INDEX l_commune_geom_idx ON l_commune USING gist(geom);

DROP INDEX IF EXISTS couche_secteurs_geom_idx;
DROP INDEX IF EXISTS l_secteur_geom_idx;
CREATE INDEX l_secteur_geom_idx ON l_secteur USING gist(geom);

DROP INDEX IF EXISTS couche_zonage_reglementaire_geom_idx;
DROP INDEX IF EXISTS l_zonage_reglementaire_geom_idx;
CREATE INDEX l_zonage_reglementaire_geom_idx ON l_zonage_reglementaire USING gist(geom);


-------------------------------------------------------------------------------
-- Ensure land layers have valid geometries
-------------------------------------------------------------------------------

ALTER TABLE l_commune DROP CONSTRAINT IF EXISTS l_commune_geom_isvalid;
ALTER TABLE l_commune ADD CONSTRAINT l_commune_geom_isvalid CHECK (ST_IsValid(geom));

ALTER TABLE l_secteur DROP CONSTRAINT IF EXISTS l_secteur_geom_isvalid;
ALTER TABLE l_secteur ADD CONSTRAINT l_secteur_geom_isvalid CHECK (ST_IsValid(geom));

ALTER TABLE l_zonage_reglementaire DROP CONSTRAINT IF EXISTS l_zonage_reglementaire_geom_isvalid;
ALTER TABLE l_zonage_reglementaire ADD CONSTRAINT l_zonage_reglementaire_geom_isvalid CHECK (ST_IsValid(geom));

-------------------------------------------------------------------------------
-- Delete Commune/Zonage/Secteur when evenements are deleted
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS troncons_couches_sig_d_tgr ON e_r_evenement_troncon;

CREATE OR REPLACE FUNCTION zonage.lien_auto_troncon_couches_sig_d() RETURNS trigger AS $$
DECLARE
    tab varchar;
    eid integer;
BEGIN
    FOREACH tab IN ARRAY ARRAY[['f_t_commune', 'f_t_secteur', 'f_t_zonage']]
    LOOP
        -- Delete related object in association tables
        -- /!\ This query is executed for any kind of evenement, but it will
        -- return an eid only if the evenement is involved in an association
        -- table with commune, secteur or zonage. It returns NULL otherwise.
        EXECUTE 'DELETE FROM '|| quote_ident(tab) ||' WHERE evenement = $1 RETURNING evenement' INTO eid USING OLD.evenement;

        -- Delete the evenement itself
        IF eid IS NOT NULL THEN
            DELETE FROM e_t_evenement WHERE id = eid;
        END IF;
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER troncons_couches_sig_d_tgr
AFTER DELETE ON e_r_evenement_troncon
FOR EACH ROW EXECUTE PROCEDURE lien_auto_troncon_couches_sig_d();


-------------------------------------------------------------------------------
-- Delete evenements when Commune/Zonage/Secteur are deleted
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS commune_troncons_d_tgr ON f_t_commune;
DROP TRIGGER IF EXISTS secteur_troncons_d_tgr ON f_t_secteur;
DROP TRIGGER IF EXISTS zonage_troncons_d_tgr ON f_t_zonage;

CREATE OR REPLACE FUNCTION zonage.nettoyage_auto_couches_sig_d() RETURNS trigger AS $$
BEGIN
    DELETE FROM e_r_evenement_troncon WHERE evenement = OLD.evenement;
    DELETE FROM e_t_evenement WHERE id = OLD.evenement;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER commune_troncons_d_tgr
AFTER DELETE ON f_t_commune
FOR EACH ROW EXECUTE PROCEDURE nettoyage_auto_couches_sig_d();

CREATE TRIGGER secteur_troncons_d_tgr
AFTER DELETE ON f_t_secteur
FOR EACH ROW EXECUTE PROCEDURE nettoyage_auto_couches_sig_d();

CREATE TRIGGER zonage_troncons_d_tgr
AFTER DELETE ON f_t_zonage
FOR EACH ROW EXECUTE PROCEDURE nettoyage_auto_couches_sig_d();



-------------------------------------------------------------------------------
-- Sync when Troncon modified
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS l_t_troncon_couches_sig_iu_tgr ON l_t_troncon;

CREATE OR REPLACE FUNCTION lien_auto_troncon_couches_sig_iu() RETURNS trigger AS $$
DECLARE
    rec record;
    tab varchar;
    eid integer;
BEGIN
    -- Remove obsolete evenement
    IF TG_OP = 'UPDATE' THEN
        -- Related evenement/zonage/secteur/commune will be cleared by another trigger
        DELETE FROM e_r_evenement_troncon et USING f_t_zonage z WHERE et.troncon = OLD.id AND et.evenement = z.evenement;
        DELETE FROM e_r_evenement_troncon et USING f_t_secteur s WHERE et.troncon = OLD.id AND et.evenement = s.evenement;
        DELETE FROM e_r_evenement_troncon et USING f_t_commune c WHERE et.troncon = OLD.id AND et.evenement = c.evenement;
    END IF;

    -- Add new evenement
    -- Note: Column names differ between commune, secteur and zonage, we can not use an elegant loop.

    -- Commune
    FOR rec IN EXECUTE 'SELECT id, ST_Line_Locate_Point($1, COALESCE(ST_StartPoint(geom), geom)) as pk_a, ST_Line_Locate_Point($1, COALESCE(ST_EndPoint(geom), geom)) as pk_b FROM (SELECT insee AS id, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS geom FROM l_commune WHERE ST_Intersects(geom, $1)) AS sub' USING NEW.geom
    LOOP
        INSERT INTO e_t_evenement (date_insert, date_update, kind, decallage, longueur, geom, supprime) VALUES (now(), now(), 'CITYEDGE', 0, 0, NEW.geom, FALSE) RETURNING id INTO eid;
        INSERT INTO e_r_evenement_troncon (troncon, evenement, pk_debut, pk_fin) VALUES (NEW.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
        INSERT INTO f_t_commune (evenement, commune) VALUES (eid, rec.id);
    END LOOP;

    -- Secteur
    FOR rec IN EXECUTE 'SELECT id, ST_Line_Locate_Point($1,COALESCE(ST_StartPoint(geom), geom)) as pk_a, ST_Line_Locate_Point($1, COALESCE(ST_EndPoint(geom), geom)) as pk_b FROM (SELECT id, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS geom FROM l_secteur WHERE ST_Intersects(geom, $1)) AS sub' USING NEW.geom
    LOOP
        INSERT INTO e_t_evenement (date_insert, date_update, kind, decallage, longueur, geom, supprime) VALUES (now(), now(), 'DISTRICTEDGE', 0, 0, NEW.geom, FALSE) RETURNING id INTO eid;
        INSERT INTO e_r_evenement_troncon (troncon, evenement, pk_debut, pk_fin) VALUES (NEW.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
        INSERT INTO f_t_secteur (evenement, secteur) VALUES (eid, rec.id);
    END LOOP;

    -- Zonage
    FOR rec IN EXECUTE 'SELECT id, ST_Line_Locate_Point($1, COALESCE(ST_StartPoint(geom), geom)) as pk_a, ST_Line_Locate_Point($1, COALESCE(ST_EndPoint(geom), geom)) as pk_b FROM (SELECT id, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS geom FROM l_zonage_reglementaire WHERE ST_Intersects(geom, $1)) AS sub' USING NEW.geom
    LOOP
        INSERT INTO e_t_evenement (date_insert, date_update, kind, decallage, longueur, geom, supprime) VALUES (now(), now(), 'RESTRICTEDAREAEDGE', 0, 0, NEW.geom, FALSE) RETURNING id INTO eid;
        INSERT INTO e_r_evenement_troncon (troncon, evenement, pk_debut, pk_fin) VALUES (NEW.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
        INSERT INTO f_t_zonage (evenement, zone) VALUES (eid, rec.id);
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l_t_troncon_couches_sig_iu_tgr
AFTER INSERT OR UPDATE OF geom ON l_t_troncon
FOR EACH ROW EXECUTE PROCEDURE lien_auto_troncon_couches_sig_iu();



-------------------------------------------------------------------------------
-- Sync when Commune/Zonage/Secteur modified
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS commune_troncons_iu_tgr ON l_commune;
DROP TRIGGER IF EXISTS secteur_troncons_iu_tgr ON l_secteur;
DROP TRIGGER IF EXISTS zonage_troncons_iu_tgr ON l_zonage_reglementaire;

CREATE OR REPLACE FUNCTION lien_auto_couches_sig_troncon_iu() RETURNS trigger AS $$
DECLARE
    table_name varchar := TG_ARGV[0];
    id_name varchar := TG_ARGV[1];
    fk_name varchar := TG_ARGV[2];
    kind_name varchar := TG_ARGV[3];
    obj record;
    rec record;
    eid integer;
BEGIN
    -- Harmonize ID name
    BEGIN
        SELECT NEW.insee AS id INTO obj;
    EXCEPTION
        WHEN undefined_column THEN
            SELECT NEW.id AS id INTO obj;
    END;

    -- Remove obsolete evenement
    IF TG_OP = 'UPDATE' THEN
        EXECUTE 'DELETE FROM '|| quote_ident(table_name) ||' WHERE '|| quote_ident(fk_name) ||' = $1' USING obj.id;
    END IF;

    -- Add new evenement
    FOR rec IN EXECUTE 'SELECT id, egeom AS geom, ST_Line_Locate_Point(tgeom, ST_StartPoint(egeom)) AS pk_a, ST_Line_Locate_Point(tgeom, ST_EndPoint(egeom)) AS pk_b FROM (SELECT id, geom AS tgeom, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS egeom FROM l_t_troncon WHERE ST_Intersects(geom, $1)) AS sub' USING NEW.geom
    LOOP
        INSERT INTO e_t_evenement (date_insert, date_update, kind, decallage, longueur, geom, supprime) VALUES (now(), now(), kind_name, 0, 0, rec.geom, FALSE) RETURNING id INTO eid;
        INSERT INTO e_r_evenement_troncon (troncon, evenement, pk_debut, pk_fin) VALUES (rec.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
        EXECUTE 'INSERT INTO '|| quote_ident(table_name) ||' (evenement, '|| quote_ident(fk_name) ||') VALUES ($1, $2)' USING eid, obj.id;
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER commune_troncons_iu_tgr
AFTER INSERT OR UPDATE OF geom ON l_commune
FOR EACH ROW EXECUTE PROCEDURE lien_auto_couches_sig_troncon_iu('f_t_commune', 'insee', 'commune', 'CITYEDGE');

CREATE TRIGGER secteur_troncons_iu_tgr
AFTER INSERT OR UPDATE OF geom ON l_secteur
FOR EACH ROW EXECUTE PROCEDURE lien_auto_couches_sig_troncon_iu('f_t_secteur', 'id', 'secteur', 'DISTRICTEDGE');

CREATE TRIGGER zonage_troncons_iu_tgr
AFTER INSERT OR UPDATE OF geom ON l_zonage_reglementaire
FOR EACH ROW EXECUTE PROCEDURE lien_auto_couches_sig_troncon_iu('f_t_zonage', 'id', 'zone', 'RESTRICTEDAREAEDGE');
