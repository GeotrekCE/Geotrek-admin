-- FlatPage
-----------
-- title
-- external_url
-- content
-- target
-- source
-- portal
-- order
ALTER TABLE flatpages_flatpage ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE flatpages_flatpage ALTER COLUMN date_update SET DEFAULT now();
ALTER TABLE flatpages_flatpage ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date
