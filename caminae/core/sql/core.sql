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

