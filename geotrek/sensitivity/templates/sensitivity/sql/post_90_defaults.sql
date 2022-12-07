-- SportPractice
----------------
-- name
ALTER TABLE sensitivity_sportpractice ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE sensitivity_sportpractice ALTER COLUMN date_update SET DEFAULT now();

-- Species
----------
-- name
ALTER TABLE sensitivity_species ALTER COLUMN period01 SET DEFAULT FALSE;
ALTER TABLE sensitivity_species ALTER COLUMN period02 SET DEFAULT FALSE;
ALTER TABLE sensitivity_species ALTER COLUMN period03 SET DEFAULT FALSE;
ALTER TABLE sensitivity_species ALTER COLUMN period04 SET DEFAULT FALSE;
ALTER TABLE sensitivity_species ALTER COLUMN period05 SET DEFAULT FALSE;
ALTER TABLE sensitivity_species ALTER COLUMN period06 SET DEFAULT FALSE;
ALTER TABLE sensitivity_species ALTER COLUMN period07 SET DEFAULT FALSE;
ALTER TABLE sensitivity_species ALTER COLUMN period08 SET DEFAULT FALSE;
ALTER TABLE sensitivity_species ALTER COLUMN period09 SET DEFAULT FALSE;
ALTER TABLE sensitivity_species ALTER COLUMN period10 SET DEFAULT FALSE;
ALTER TABLE sensitivity_species ALTER COLUMN period11 SET DEFAULT FALSE;
ALTER TABLE sensitivity_species ALTER COLUMN period12 SET DEFAULT FALSE;
-- practices
ALTER TABLE sensitivity_species ALTER COLUMN url SET DEFAULT '';
-- radius
ALTER TABLE sensitivity_species ALTER COLUMN category SET DEFAULT 1;
-- eid
-- pictogram
ALTER TABLE sensitivity_species ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE sensitivity_species ALTER COLUMN date_update SET DEFAULT now();

-- SensitiveArea
----------------
-- geom
-- species
ALTER TABLE sensitivity_sensitivearea ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date
ALTER TABLE sensitivity_sensitivearea ALTER COLUMN description SET DEFAULT '';
ALTER TABLE sensitivity_sensitivearea ALTER COLUMN contact SET DEFAULT '';
-- eid
-- structure
ALTER TABLE maintenance_project ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE maintenance_project ALTER COLUMN date_update SET DEFAULT now();
ALTER TABLE sensitivity_sensitivearea ALTER COLUMN provider SET DEFAULT '';
-- deleted
