-- Communes

CREATE VIEW {{ schema_geotrek }}.v_cities AS
SELECT code AS "Code",
       name AS "Name",
       CASE
           WHEN published IS FALSE THEN 'No'
           WHEN published IS TRUE THEN 'Yes'
       END AS "Published",
       geom
FROM public.zoning_city
;

-- Zones

CREATE VIEW {{ schema_geotrek }}.v_districts AS
SELECT id,
       name AS "Name",
       CASE
           WHEN published IS FALSE THEN 'No'
           WHEN published IS TRUE THEN 'Yes'
       END AS "Published",
       geom
FROM public.zoning_district
;