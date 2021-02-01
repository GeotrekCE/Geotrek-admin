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
