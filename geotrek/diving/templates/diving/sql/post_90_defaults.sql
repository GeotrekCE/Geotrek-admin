-- Practice
-----------
-- name
-- order
ALTER TABLE diving_practice ALTER COLUMN color SET DEFAULT '#444444';
ALTER TABLE diving_practice ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE diving_practice ALTER COLUMN date_update SET DEFAULT now();


-- Difficulty
-------------
-- name
-- pictogram


-- Level
--------
-- name
ALTER TABLE diving_level ALTER COLUMN description SET DEFAULT '';
-- pictogram


-- Dive
-------
ALTER TABLE diving_dive ALTER COLUMN description_teaser SET DEFAULT '';
ALTER TABLE diving_dive ALTER COLUMN description SET DEFAULT '';
ALTER TABLE diving_dive ALTER COLUMN owner SET DEFAULT '';
-- practice
ALTER TABLE diving_dive ALTER COLUMN departure SET DEFAULT '';
ALTER TABLE diving_dive ALTER COLUMN disabled_sport SET DEFAULT '';
ALTER TABLE diving_dive ALTER COLUMN facilities SET DEFAULT '';
-- difficulty
-- levels
-- depth
ALTER TABLE diving_dive ALTER COLUMN advice SET DEFAULT '';
-- themes
-- geom
-- source
-- portal
ALTER TABLE diving_dive ALTER COLUMN deleted SET DEFAULT FALSE;
ALTER TABLE diving_dive ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date
-- name
ALTER TABLE diving_dive ALTER COLUMN review SET DEFAULT FALSE;
-- structure
