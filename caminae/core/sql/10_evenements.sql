-------------------------------------------------------------------------------
-- Add spatial index (will boost spatial filters)
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS evenements_geom_idx;
CREATE INDEX evenements_geom_idx ON evenements USING gist(geom);


-------------------------------------------------------------------------------
-- Keep dates up-to-date
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS evenements_date_insert_tgr ON evenements;
CREATE TRIGGER evenements_date_insert_tgr
    BEFORE INSERT ON evenements
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

DROP TRIGGER IF EXISTS evenements_date_update_tgr ON evenements;
CREATE TRIGGER evenements_date_update_tgr
    BEFORE INSERT OR UPDATE ON evenements
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();


-------------------------------------------------------------------------------
-- Compute attributes from geom fields
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS evenements_longueur_tgr ON evenements;
CREATE TRIGGER evenements_longueur_tgr
    BEFORE INSERT ON evenements
    FOR EACH ROW EXECUTE PROCEDURE ft_longueur();
