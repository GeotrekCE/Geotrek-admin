-------------------------------------------------------------------------------
-- Troncons
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS troncons_geom_idx;
CREATE INDEX troncons_geom_idx ON troncons USING gist(geom);

DROP INDEX IF EXISTS troncons_geom_cadastre_idx;
CREATE INDEX troncons_geom_cadastre_idx ON troncons USING gist(geom_cadastre);

-------------------------------------------------------------------------------
-- Evenements
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS evenements_geom_idx;
CREATE INDEX evenements_geom_idx ON evenements USING gist(geom);

