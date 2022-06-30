-- Communes

DROP VIEW IF EXISTS v_zoning_city_qgis;


CREATE OR REPLACE VIEW v_zoning_city_qgis AS
SELECT code AS "Code",
       name AS "Nom",
       CASE
           WHEN published IS FALSE THEN 'Non'
           WHEN published IS TRUE THEN 'Oui'
       END AS "Publié",
       geom
FROM public.zoning_city;

-- Zones

DROP VIEW IF EXISTS v_zoning_district_qgis;


CREATE OR REPLACE VIEW v_zoning_district_qgis AS
SELECT id,
       name AS "Nom",
       CASE
           WHEN published IS FALSE THEN 'Non'
           WHEN published IS TRUE THEN 'Oui'
       END AS "Publié",
       geom
FROM public.zoning_district;