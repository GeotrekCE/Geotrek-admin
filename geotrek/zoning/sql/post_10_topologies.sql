-------------------------------------------------------------------------------
-- Add spatial index (will boost spatial filters)
-------------------------------------------------------------------------------

CREATE INDEX zoning_city_geom_idx ON zoning_city USING gist(geom);
CREATE INDEX zoning_district_geom_idx ON zoning_district USING gist(geom);
CREATE INDEX zoning_restrictedarea_geom_idx ON zoning_restrictedarea USING gist(geom);


-------------------------------------------------------------------------------
-- Ensure land layers have valid geometries
-------------------------------------------------------------------------------

ALTER TABLE zoning_city DROP CONSTRAINT IF EXISTS l_commune_geom_isvalid;
ALTER TABLE zoning_city DROP CONSTRAINT IF EXISTS zoning_city_geom_isvalid;
ALTER TABLE zoning_city ADD CONSTRAINT zoning_city_geom_isvalid CHECK (ST_IsValid(geom));

ALTER TABLE zoning_district DROP CONSTRAINT IF EXISTS l_secteur_geom_isvalid;
ALTER TABLE zoning_district DROP CONSTRAINT IF EXISTS zoning_district_geom_isvalid;
ALTER TABLE zoning_district ADD CONSTRAINT zoning_district_geom_isvalid CHECK (ST_IsValid(geom));

ALTER TABLE zoning_restrictedarea DROP CONSTRAINT IF EXISTS l_zonage_reglementaire_geom_isvalid;
ALTER TABLE zoning_restrictedarea DROP CONSTRAINT IF EXISTS zoning_restrictedarea_geom_isvalid;
ALTER TABLE zoning_restrictedarea ADD CONSTRAINT zoning_restrictedarea_geom_isvalid CHECK (ST_IsValid(geom));

-------------------------------------------------------------------------------
-- Delete City/District/Restrictedarea when topologies are deleted
-------------------------------------------------------------------------------

CREATE FUNCTION {# geotrek.zoning #}.auto_link_path_topologies_d() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    tab varchar;
    eid integer;
BEGIN
    FOREACH tab IN ARRAY ARRAY[['zoning_cityedge', 'zoning_districtedge', 'zoning_restrictedareaedge']]
    LOOP
        -- Delete related object in association tables
        -- /!\ This query is executed for any kind of topology, but it will
        -- return an eid only if the topology is involved in an association
        -- table with commune, secteur or zonage. It returns NULL otherwise.
        EXECUTE 'DELETE FROM '|| quote_ident(tab) ||' WHERE topo_object_id = $1 RETURNING topo_object_id' INTO eid USING OLD.topo_object_id;

        -- Delete the topology itself
        IF eid IS NOT NULL THEN
            DELETE FROM core_topology WHERE id = eid;
        END IF;
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER path_topologies_d_tgr
AFTER DELETE ON core_pathaggregation
FOR EACH ROW EXECUTE PROCEDURE auto_link_path_topologies_d();


-------------------------------------------------------------------------------
-- Delete topologies when City/District/Restrictedarea are deleted
-------------------------------------------------------------------------------

CREATE FUNCTION {# geotrek.zoning #}.auto_clean_topologies_sig_d() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    DELETE FROM core_pathaggregation WHERE topo_object_id = OLD.topo_object_id;
    DELETE FROM core_topology WHERE id = OLD.topo_object_id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER city_paths_d_tgr
AFTER DELETE ON zoning_cityedge
FOR EACH ROW EXECUTE PROCEDURE auto_clean_topologies_sig_d();

CREATE TRIGGER district_paths_d_tgr
AFTER DELETE ON zoning_districtedge
FOR EACH ROW EXECUTE PROCEDURE auto_clean_topologies_sig_d();

CREATE TRIGGER restrictedarea_paths_d_tgr
AFTER DELETE ON zoning_restrictedareaedge
FOR EACH ROW EXECUTE PROCEDURE auto_clean_topologies_sig_d();


-------------------------------------------------------------------------------
-- Sync when Troncon modified
-------------------------------------------------------------------------------

CREATE FUNCTION {# geotrek.zoning #}.auto_link_path_topologies_iu() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    rec record;
    tab varchar;
    eid integer;
BEGIN
    -- Remove obsolete topology
    IF TG_OP = 'UPDATE' THEN
        -- Related topology/zonage/secteur/commune will be cleared by another trigger
        DELETE FROM core_pathaggregation et USING zoning_restrictedareaedge z WHERE et.path_id = OLD.id AND et.topo_object_id = z.topo_object_id;
        DELETE FROM core_pathaggregation et USING zoning_districtedge s WHERE et.path_id = OLD.id AND et.topo_object_id = s.topo_object_id;
        DELETE FROM core_pathaggregation et USING zoning_cityedge c WHERE et.path_id = OLD.id AND et.topo_object_id = c.topo_object_id;
    END IF;

    -- Add new topology
    -- Note: Column names differ between commune, secteur and zonage, we can not use an elegant loop.

    -- Commune
    FOR rec IN EXECUTE 'SELECT id, ST_LineLocatePoint($1, COALESCE(ST_StartPoint(geom), geom)) as pk_a, CASE WHEN ST_EQUALS(ST_EndPoint(geom), ST_StartPoint($1)) THEN 1 ELSE ST_LineLocatePoint($1, COALESCE(ST_EndPoint(geom), geom)) END as pk_b FROM (SELECT code AS id, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS geom FROM zoning_city WHERE ST_Intersects(geom, $1)) AS sub WHERE ST_GeometryType(geom)=''ST_LineString''' USING NEW.geom
    LOOP
        INSERT INTO core_topology (date_insert, date_update, kind, "offset", length, geom, deleted) VALUES (now(), now(), 'CITYEDGE', 0, 0, NEW.geom, FALSE) RETURNING id INTO eid;
        INSERT INTO core_pathaggregation (path_id, topo_object_id, start_position, end_position) VALUES (NEW.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
        INSERT INTO zoning_cityedge (topo_object_id, city_id) VALUES (eid, rec.id);
    END LOOP;

    -- Secteur
    FOR rec IN EXECUTE 'SELECT id, ST_LineLocatePoint($1,COALESCE(ST_StartPoint(geom), geom)) as pk_a, CASE WHEN ST_EQUALS(ST_EndPoint(geom), ST_StartPoint($1)) THEN 1 ELSE ST_LineLocatePoint($1, COALESCE(ST_EndPoint(geom), geom)) END as pk_b FROM (SELECT id, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS geom FROM zoning_district WHERE ST_Intersects(geom, $1)) AS sub WHERE ST_GeometryType(geom)=''ST_LineString''' USING NEW.geom
    LOOP
        INSERT INTO core_topology (date_insert, date_update, kind, "offset", length, geom, deleted) VALUES (now(), now(), 'DISTRICTEDGE', 0, 0, NEW.geom, FALSE) RETURNING id INTO eid;
        INSERT INTO core_pathaggregation (path_id, topo_object_id, start_position, end_position) VALUES (NEW.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
        INSERT INTO zoning_districtedge (topo_object_id, district_id) VALUES (eid, rec.id);
    END LOOP;

    -- Zonage
    FOR rec IN EXECUTE 'SELECT id, ST_LineLocatePoint($1, COALESCE(ST_StartPoint(geom), geom)) as pk_a, CASE WHEN ST_EQUALS(ST_EndPoint(geom), ST_StartPoint($1)) THEN 1 ELSE ST_LineLocatePoint($1, COALESCE(ST_EndPoint(geom), geom)) END as pk_b FROM (SELECT id, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS geom FROM zoning_restrictedarea WHERE ST_Intersects(geom, $1)) AS sub WHERE ST_GeometryType(geom)=''ST_LineString''' USING NEW.geom
    LOOP
        INSERT INTO core_topology (date_insert, date_update, kind, "offset", length, geom, deleted) VALUES (now(), now(), 'RESTRICTEDAREAEDGE', 0, 0, NEW.geom, FALSE) RETURNING id INTO eid;
        INSERT INTO core_pathaggregation (path_id, topo_object_id, start_position, end_position) VALUES (NEW.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
        INSERT INTO zoning_restrictedareaedge (topo_object_id, restricted_area_id) VALUES (eid, rec.id);
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER core_path_topologies_iu_tgr
AFTER INSERT OR UPDATE OF geom ON core_path
FOR EACH ROW EXECUTE PROCEDURE auto_link_path_topologies_iu();


-------------------------------------------------------------------------------
-- Sync when Commune/Zonage/Secteur modified
-------------------------------------------------------------------------------

CREATE FUNCTION {# geotrek.zoning #}.auto_link_topologies_path_iu() RETURNS trigger SECURITY DEFINER AS $$
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

    -- Remove obsolete topology
    IF TG_OP = 'UPDATE' THEN
        EXECUTE 'DELETE FROM '|| quote_ident(table_name) ||' WHERE '|| quote_ident(fk_name) ||' = $1' USING obj.id;
    END IF;

    -- Add new topology
    FOR rec IN EXECUTE 'SELECT id, egeom AS geom, ST_LineLocatePoint(tgeom, ST_StartPoint(egeom)) AS pk_a, CASE WHEN ST_EQUALS(ST_EndPoint(tgeom), ST_StartPoint(egeom)) THEN 1 ELSE ST_LineLocatePoint(tgeom, ST_EndPoint(egeom)) END AS pk_b FROM (SELECT id, geom AS tgeom, (ST_Dump(ST_Multi(ST_Intersection(geom, $1)))).geom AS egeom FROM core_path WHERE ST_Intersects(geom, $1)) AS sub WHERE ST_GeometryType(egeom)=''ST_LineString''' USING NEW.geom
    LOOP
        IF rec.pk_a IS NOT NULL AND rec.pk_b IS NOT NULL THEN
            INSERT INTO core_topology (date_insert, date_update, kind, "offset", length, geom, deleted) VALUES (now(), now(), kind_name, 0, 0, rec.geom, FALSE) RETURNING id INTO eid;
            INSERT INTO core_pathaggregation (path_id, topo_object_id, start_position, end_position) VALUES (rec.id, eid, least(rec.pk_a, rec.pk_b), greatest(rec.pk_a, rec.pk_b));
            EXECUTE 'INSERT INTO '|| quote_ident(table_name) ||' (topo_object_id, '|| quote_ident(fk_name) ||') VALUES ($1, $2)' USING eid, obj.id;
        END IF;
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER city_paths_iu_tgr
AFTER INSERT OR UPDATE OF geom ON zoning_city
FOR EACH ROW EXECUTE PROCEDURE auto_link_topologies_path_iu('zoning_cityedge', 'code', 'city_id', 'CITYEDGE');

CREATE TRIGGER district_paths_iu_tgr
AFTER INSERT OR UPDATE OF geom ON zoning_district
FOR EACH ROW EXECUTE PROCEDURE auto_link_topologies_path_iu('zoning_districtedge', 'id', 'district_id', 'DISTRICTEDGE');

CREATE TRIGGER restrictedarea_paths_iu_tgr
AFTER INSERT OR UPDATE OF geom ON zoning_restrictedarea
FOR EACH ROW EXECUTE PROCEDURE auto_link_topologies_path_iu('zoning_restrictedareaedge', 'id', 'restricted_area_id', 'RESTRICTEDAREAEDGE');
