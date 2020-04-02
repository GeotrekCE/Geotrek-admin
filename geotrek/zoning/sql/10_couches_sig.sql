SELECT create_schema_if_not_exist('zonage');

-------------------------------------------------------------------------------
-- Add spatial index (will boost spatial filters)
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS couche_communes_geom_idx;
DROP INDEX IF EXISTS l_commune_geom_idx;
CREATE INDEX l_commune_geom_idx ON zoning_city USING gist(geom);

DROP INDEX IF EXISTS couche_secteurs_geom_idx;
DROP INDEX IF EXISTS l_secteur_geom_idx;
CREATE INDEX l_secteur_geom_idx ON zoning_district USING gist(geom);

DROP INDEX IF EXISTS couche_zonage_reglementaire_geom_idx;
DROP INDEX IF EXISTS l_zonage_reglementaire_geom_idx;
CREATE INDEX l_zonage_reglementaire_geom_idx ON zoning_restrictedarea USING gist(geom);


-------------------------------------------------------------------------------
-- Ensure land layers have valid geometries
-------------------------------------------------------------------------------

ALTER TABLE zoning_city DROP CONSTRAINT IF EXISTS l_commune_geom_isvalid;
ALTER TABLE zoning_city ADD CONSTRAINT l_commune_geom_isvalid CHECK (ST_IsValid(geom));

ALTER TABLE zoning_district DROP CONSTRAINT IF EXISTS l_secteur_geom_isvalid;
ALTER TABLE zoning_district ADD CONSTRAINT l_secteur_geom_isvalid CHECK (ST_IsValid(geom));

ALTER TABLE zoning_restrictedarea DROP CONSTRAINT IF EXISTS l_zonage_reglementaire_geom_isvalid;
ALTER TABLE zoning_restrictedarea ADD CONSTRAINT l_zonage_reglementaire_geom_isvalid CHECK (ST_IsValid(geom));

-------------------------------------------------------------------------------
-- Delete Commune/Zonage/Secteur when evenements are deleted
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS troncons_couches_sig_d_tgr ON core_pathaggregation;

CREATE OR REPLACE FUNCTION zonage.lien_auto_troncon_couches_sig_d() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    tab varchar;
    eid integer;
BEGIN
    FOREACH tab IN ARRAY ARRAY[['zoning_cityedge', 'zoning_districtedge', 'zoning_restrictedareaedge']]
    LOOP
        -- Delete related object in association tables
        -- /!\ This query is executed for any kind of evenement, but it will
        -- return an eid only if the evenement is involved in an association
        -- table with commune, secteur or zonage. It returns NULL otherwise.
        EXECUTE 'DELETE FROM '|| quote_ident(tab) ||' WHERE topo_object_id = $1 RETURNING topo_object_id' INTO eid USING OLD.topo_object_id;

        -- Delete the evenement itself
        IF eid IS NOT NULL THEN
            DELETE FROM core_topology WHERE id = eid;
        END IF;
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER troncons_couches_sig_d_tgr
AFTER DELETE ON core_pathaggregation
FOR EACH ROW EXECUTE PROCEDURE lien_auto_troncon_couches_sig_d();


-------------------------------------------------------------------------------
-- Delete evenements when Commune/Zonage/Secteur are deleted
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS commune_troncons_d_tgr ON zoning_cityedge;
DROP TRIGGER IF EXISTS secteur_troncons_d_tgr ON zoning_districtedge;
DROP TRIGGER IF EXISTS zonage_troncons_d_tgr ON zoning_restrictedareaedge;

CREATE OR REPLACE FUNCTION zonage.nettoyage_auto_couches_sig_d() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    DELETE FROM core_pathaggregation WHERE topo_object_id = OLD.topo_object_id;
    DELETE FROM core_topology WHERE id = OLD.topo_object_id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER commune_troncons_d_tgr
AFTER DELETE ON zoning_cityedge
FOR EACH ROW EXECUTE PROCEDURE nettoyage_auto_couches_sig_d();

CREATE TRIGGER secteur_troncons_d_tgr
AFTER DELETE ON zoning_districtedge
FOR EACH ROW EXECUTE PROCEDURE nettoyage_auto_couches_sig_d();

CREATE TRIGGER zonage_troncons_d_tgr
AFTER DELETE ON zoning_restrictedareaedge
FOR EACH ROW EXECUTE PROCEDURE nettoyage_auto_couches_sig_d();



-------------------------------------------------------------------------------
-- Sync when Troncon modified
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS l_t_troncon_couches_sig_iu_tgr ON core_path;

CREATE OR REPLACE FUNCTION lien_auto_troncon_couches_sig_iu() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    rec record;
    tab varchar;
    eid integer;
BEGIN
    -- Remove obsolete evenement
    IF TG_OP = 'UPDATE' THEN
        -- Related evenement/zonage/secteur/commune will be cleared by another trigger
        DELETE FROM core_pathaggregation et USING zoning_restrictedareaedge z WHERE et.path_id = OLD.id AND et.topo_object_id = z.topo_object_id;
        DELETE FROM core_pathaggregation et USING zoning_districtedge s WHERE et.path_id = OLD.id AND et.topo_object_id = s.topo_object_id;
        DELETE FROM core_pathaggregation et USING zoning_cityedge c WHERE et.path_id = OLD.id AND et.topo_object_id = c.topo_object_id;
    END IF;

    -- Add new evenement
    -- Note: Column names differ between commune, secteur and zonage, we can not use an elegant loop.

    -- Commune
    FOR rec IN EXECUTE 'SELECT id, ST_LineLocatePoint($1, COALESCE(ST_StartPoint(geom), geom)) as pk_a, ST_LineLocatePoint($1, COALESCE(ST_EndPoint(geom), geom)) as pk_b FROM (SELECT code AS id, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS geom FROM zoning_city WHERE ST_Intersects(geom, $1)) AS sub' USING NEW.geom
    LOOP
        INSERT INTO core_topology (date_insert, date_update, kind, "offset", length, geom, deleted, need_update) VALUES (now(), now(), 'CITYEDGE', 0, 0, NEW.geom, FALSE, FALSE) RETURNING id INTO eid;
        INSERT INTO core_pathaggregation (path_id, topo_object_id, start_position, end_position) VALUES (NEW.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
        INSERT INTO zoning_cityedge (topo_object_id, city_id) VALUES (eid, rec.id);
    END LOOP;

    -- Secteur
    FOR rec IN EXECUTE 'SELECT id, ST_LineLocatePoint($1,COALESCE(ST_StartPoint(geom), geom)) as pk_a, ST_LineLocatePoint($1, COALESCE(ST_EndPoint(geom), geom)) as pk_b FROM (SELECT id, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS geom FROM zoning_district WHERE ST_Intersects(geom, $1)) AS sub' USING NEW.geom
    LOOP
        INSERT INTO core_topology (date_insert, date_update, kind, "offset", length, geom, deleted, need_update) VALUES (now(), now(), 'DISTRICTEDGE', 0, 0, NEW.geom, FALSE, FALSE) RETURNING id INTO eid;
        INSERT INTO core_pathaggregation (path_id, topo_object_id, start_position, end_position) VALUES (NEW.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
        INSERT INTO zoning_districtedge (topo_object_id, district_id) VALUES (eid, rec.id);
    END LOOP;

    -- Zonage
    FOR rec IN EXECUTE 'SELECT id, ST_LineLocatePoint($1, COALESCE(ST_StartPoint(geom), geom)) as pk_a, ST_LineLocatePoint($1, COALESCE(ST_EndPoint(geom), geom)) as pk_b FROM (SELECT id, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS geom FROM zoning_restrictedarea WHERE ST_Intersects(geom, $1)) AS sub' USING NEW.geom
    LOOP
        INSERT INTO core_topology (date_insert, date_update, kind, "offset", length, geom, deleted, need_update) VALUES (now(), now(), 'RESTRICTEDAREAEDGE', 0, 0, NEW.geom, FALSE, FALSE) RETURNING id INTO eid;
        INSERT INTO core_pathaggregation (path_id, topo_object_id, start_position, end_position) VALUES (NEW.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
        INSERT INTO zoning_restrictedareaedge (topo_object_id, restricted_area_id) VALUES (eid, rec.id);
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l_t_troncon_couches_sig_iu_tgr
AFTER INSERT OR UPDATE OF geom ON core_path
FOR EACH ROW EXECUTE PROCEDURE lien_auto_troncon_couches_sig_iu();



-------------------------------------------------------------------------------
-- Sync when Commune/Zonage/Secteur modified
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS commune_troncons_iu_tgr ON zoning_city;
DROP TRIGGER IF EXISTS secteur_troncons_iu_tgr ON zoning_district;
DROP TRIGGER IF EXISTS zonage_troncons_iu_tgr ON zoning_restrictedarea;

CREATE OR REPLACE FUNCTION lien_auto_couches_sig_troncon_iu() RETURNS trigger SECURITY DEFINER AS $$
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
        SELECT NEW.code AS id INTO obj;
    EXCEPTION
        WHEN undefined_column THEN
            SELECT NEW.id AS id INTO obj;
    END;

    -- Remove obsolete evenement
    IF TG_OP = 'UPDATE' THEN
        EXECUTE 'DELETE FROM '|| quote_ident(table_name) ||' WHERE '|| quote_ident(fk_name) ||' = $1' USING obj.id;
    END IF;

    -- Add new evenement
    FOR rec IN EXECUTE 'SELECT id, egeom AS geom, ST_LineLocatePoint(tgeom, ST_StartPoint(egeom)) AS pk_a, ST_LineLocatePoint(tgeom, ST_EndPoint(egeom)) AS pk_b FROM (SELECT id, geom AS tgeom, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS egeom FROM core_path WHERE ST_Intersects(geom, $1)) AS sub' USING NEW.geom
    LOOP
        IF rec.pk_a IS NOT NULL AND rec.pk_b IS NOT NULL THEN
            INSERT INTO core_topology (date_insert, date_update, kind, "offset", length, geom, deleted, need_update) VALUES (now(), now(), kind_name, 0, 0, rec.geom, FALSE, FALSE) RETURNING id INTO eid;
            INSERT INTO core_pathaggregation (path_id, topo_object_id, start_position, end_position) VALUES (rec.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
            EXECUTE 'INSERT INTO '|| quote_ident(table_name) ||' (topo_object_id, '|| quote_ident(fk_name) ||') VALUES ($1, $2)' USING eid, obj.id;
        END IF;
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER commune_troncons_iu_tgr
AFTER INSERT OR UPDATE OF geom ON zoning_city
FOR EACH ROW EXECUTE PROCEDURE lien_auto_couches_sig_troncon_iu('zoning_cityedge', 'code', 'city_id', 'CITYEDGE');

CREATE TRIGGER secteur_troncons_iu_tgr
AFTER INSERT OR UPDATE OF geom ON zoning_district
FOR EACH ROW EXECUTE PROCEDURE lien_auto_couches_sig_troncon_iu('zoning_districtedge', 'id', 'district_id', 'DISTRICTEDGE');

CREATE TRIGGER zonage_troncons_iu_tgr
AFTER INSERT OR UPDATE OF geom ON zoning_restrictedarea
FOR EACH ROW EXECUTE PROCEDURE lien_auto_couches_sig_troncon_iu('zoning_restrictedareaedge', 'id', 'restricted_area_id', 'RESTRICTEDAREAEDGE');
