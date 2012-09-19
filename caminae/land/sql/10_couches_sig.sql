-------------------------------------------------------------------------------
-- Add spatial index (will boost spatial filters)
-------------------------------------------------------------------------------

DROP INDEX IF EXISTS couche_communes_geom_idx;
CREATE INDEX couche_communes_geom_idx ON couche_communes USING gist(geom);

DROP INDEX IF EXISTS couche_secteurs_geom_idx;
CREATE INDEX couche_secteurs_geom_idx ON couche_secteurs USING gist(geom);

DROP INDEX IF EXISTS couche_zonage_reglementaire_geom_idx;
CREATE INDEX couche_zonage_reglementaire_geom_idx ON couche_zonage_reglementaire USING gist(geom);
