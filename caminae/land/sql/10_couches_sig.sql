-------------------------------------------------------------------------------
-- Add spatial index (will boost spatial filters)
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS couche_communes_geom_idx;
CREATE INDEX couche_communes_geom_idx ON couche_communes USING gist(geom);

DROP INDEX IF EXISTS couche_secteurs_geom_idx;
CREATE INDEX couche_secteurs_geom_idx ON couche_secteurs USING gist(geom);

DROP INDEX IF EXISTS couche_zonage_reglementaire_geom_idx;
CREATE INDEX couche_zonage_reglementaire_geom_idx ON couche_zonage_reglementaire USING gist(geom);


-------------------------------------------------------------------------------
-- Ensure Evenement is cleared when removing link between Troncon and
-- Commune/Zonage/Secteur
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS commune_troncons_d_tgr ON commune;
DROP TRIGGER IF EXISTS secteur_troncons_d_tgr ON secteur;
DROP TRIGGER IF EXISTS zonage_troncons_d_tgr ON zonage;

CREATE OR REPLACE FUNCTION nettoyage_auto_couches_sig_d() RETURNS trigger AS $$
BEGIN
    DELETE FROM evenements_troncons WHERE evenement = OLD.evenement;
    DELETE FROM evenements WHERE id = OLD.evenement;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER commune_troncons_d_tgr
AFTER DELETE ON commune
FOR EACH ROW EXECUTE PROCEDURE nettoyage_auto_couches_sig_d();

CREATE TRIGGER secteur_troncons_d_tgr
AFTER DELETE ON secteur
FOR EACH ROW EXECUTE PROCEDURE nettoyage_auto_couches_sig_d();

CREATE TRIGGER zonage_troncons_d_tgr
AFTER DELETE ON zonage
FOR EACH ROW EXECUTE PROCEDURE nettoyage_auto_couches_sig_d();


-------------------------------------------------------------------------------
-- Automatic link between Troncon and Commune/Zonage/Secteur
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS commune_troncons_iu_tgr ON couche_communes;
DROP TRIGGER IF EXISTS secteur_troncons_iu_tgr ON couche_secteurs;
DROP TRIGGER IF EXISTS zonage_troncons_iu_tgr ON couche_zonage_reglementaire;

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
    FOR rec IN EXECUTE 'SELECT id, ST_Line_Locate_Point(geom, ST_StartPoint(ST_Intersection(geom, $1))) as pk_debut, ST_Line_Locate_Point(geom, ST_EndPoint(ST_Intersection(geom, $1))) as pk_fin, geom FROM troncons WHERE ST_Intersects(geom, $1)' USING NEW.geom
    LOOP
        INSERT INTO evenements (date_insert, date_update, kind, decallage, longueur, geom) VALUES (now(), now(), kind_name, 0, 0, rec.geom) RETURNING id INTO eid;
        INSERT INTO evenements_troncons (troncon, evenement, pk_debut, pk_fin) VALUES (rec.id, eid, rec.pk_debut, rec.pk_fin);
        EXECUTE 'INSERT INTO '|| quote_ident(table_name) ||' (evenement, '|| quote_ident(fk_name) ||') VALUES ($1, $2)' USING eid, obj.id;
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER commune_troncons_iu_tgr
AFTER INSERT OR UPDATE OF geom ON couche_communes
FOR EACH ROW EXECUTE PROCEDURE lien_auto_couches_sig_troncon_iu('commune', 'insee', 'city_id', 'CITYEDGE');

CREATE TRIGGER secteur_troncons_iu_tgr
AFTER INSERT OR UPDATE OF geom ON couche_secteurs
FOR EACH ROW EXECUTE PROCEDURE lien_auto_couches_sig_troncon_iu('secteur', 'id', 'district_id', 'DISTRICTEDGE');

CREATE TRIGGER zonage_troncons_iu_tgr
AFTER INSERT OR UPDATE OF geom ON couche_zonage_reglementaire
FOR EACH ROW EXECUTE PROCEDURE lien_auto_couches_sig_troncon_iu('zonage', 'id', 'restricted_area_id', 'RESTRICTEDAREAEDGE');
