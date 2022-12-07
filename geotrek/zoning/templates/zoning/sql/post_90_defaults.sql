-- RestrictedAreaType
---------------------
-- name


-- RestrictedArea
-----------------
-- name
-- geom
-- area_type
ALTER TABLE zoning_restrictedarea ALTER COLUMN published SET DEFAULT TRUE;
ALTER TABLE zoning_restrictedarea ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE zoning_restrictedarea ALTER COLUMN date_update SET DEFAULT now();
-- pictogram


-- City
-------
-- name
-- geom
-- area_type
ALTER TABLE zoning_city ALTER COLUMN published SET DEFAULT TRUE;
ALTER TABLE zoning_city ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE zoning_city ALTER COLUMN date_update SET DEFAULT now();


-- District
-----------
-- name
-- geom
ALTER TABLE zoning_district ALTER COLUMN published SET DEFAULT TRUE;
ALTER TABLE zoning_district ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE zoning_district ALTER COLUMN date_update SET DEFAULT now();
