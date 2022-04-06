-- FlatPage
-----------
-- title
ALTER TABLE flatpages_flatpage ALTER COLUMN external_url SET DEFAULT '';
-- content
ALTER TABLE flatpages_flatpage ALTER COLUMN target SET DEFAULT 'all';
-- source
-- portal
-- order
ALTER TABLE flatpages_flatpage ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE flatpages_flatpage ALTER COLUMN date_update SET DEFAULT now();
ALTER TABLE flatpages_flatpage ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date
