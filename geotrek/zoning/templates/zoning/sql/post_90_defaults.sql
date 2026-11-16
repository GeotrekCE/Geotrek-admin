-- RestrictedArea
-----------------
ALTER TABLE zoning_restrictedarea ALTER COLUMN published SET DEFAULT TRUE;


-- City
-------
ALTER TABLE zoning_city ALTER COLUMN published SET DEFAULT TRUE;


-- District
-----------
ALTER TABLE zoning_district ALTER COLUMN published SET DEFAULT TRUE;


-- Vigilance area
-----------------
ALTER TABLE zoning_vigilancearea ALTER COLUMN published SET DEFAULT TRUE;