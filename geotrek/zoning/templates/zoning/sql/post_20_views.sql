-- City

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

-- District

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

-- Restricted area

CREATE VIEW {{ schema_geotrek }}.v_restrictedareas AS
SELECT ra.id,
       ra.name AS "Name",
       CASE
           WHEN ra.published IS FALSE THEN 'No'
           WHEN ra.published IS TRUE THEN 'Yes'
       END AS "Published",
       rat.name AS "Type",
       ra.geom
FROM public.zoning_restrictedarea ra
JOIN public.zoning_restrictedareatype rat ON ra.area_type_id = rat.id
;

-- Vigilance area

CREATE VIEW {{ schema_geotrek }}.v_vigilanceareas AS
SELECT va.id,
       va.name AS "Name",
       CASE
           WHEN va.published IS FALSE THEN 'No'
           WHEN va.published IS TRUE THEN 'Yes'
       END AS "Published",
       vz.name AS "Type",
       va.geom
FROM public.zoning_vigilancearea va
JOIN public.zoning_vigilanceareatype vz ON va.vigilance_area_type_id = vz.id
;