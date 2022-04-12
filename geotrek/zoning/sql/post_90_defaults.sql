-- RestrictedAreaType
---------------------
-- name


-- RestrictedArea
-----------------
-- name
-- geom
-- area_type
ALTER TABLE zoning_restrictedarea ALTER COLUMN published SET DEFAULT TRUE;
-- pictogram


-- City
-------
-- name
-- geom
-- area_type
ALTER TABLE zoning_city ALTER COLUMN published SET DEFAULT TRUE;


-- District
-----------
-- name
-- geom
ALTER TABLE zoning_district ALTER COLUMN published SET DEFAULT TRUE;


-- District
-----------
-- name
-- geom
ALTER TABLE zoning_district ALTER COLUMN published SET DEFAULT TRUE;
