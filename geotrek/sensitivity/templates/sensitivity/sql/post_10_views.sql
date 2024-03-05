-- Zones sensibles

CREATE VIEW {{ schema_geotrek }}.v_sensitivearea AS
SELECT a.id,
       d.name AS "Structure",
       f.zoning_city AS "City",
       g.zoning_district AS "District",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        b.name_{{ lang }} AS "Name {{ lang }}",
       {% endfor %}
       CASE
           WHEN h.category = 2 THEN 'Regulatory'
           WHEN h.category = 1 THEN 'Specie'
       END AS "Category",
       CONCAT(CASE
                  WHEN h.period01 IS TRUE THEN CONCAT('January', ', ')
                  ELSE NULL
              END,
              CASE
                  WHEN h.period02 IS TRUE THEN CONCAT('February', ', ')
                  ELSE NULL
              END,
              CASE
                  WHEN h.period03 IS TRUE THEN CONCAT('March', ', ')
                  ELSE NULL
              END,
              CASE
                  WHEN h.period04 IS TRUE THEN CONCAT('April', ', ')
                  ELSE NULL
              END,
              CASE
                  WHEN h.period05 IS TRUE THEN CONCAT('May', ', ')
                  ELSE NULL
              END,
              CASE
                  WHEN h.period06 IS TRUE THEN CONCAT('June', ', ')
                  ELSE NULL
              END,
              CASE
                  WHEN h.period07 IS TRUE THEN CONCAT('July', ', ')
                  ELSE NULL
              END,
              CASE
                  WHEN h.period08 IS TRUE THEN CONCAT('August', ', ')
                  ELSE NULL
              END,
              CASE
                  WHEN h.period09 IS TRUE THEN CONCAT('September', ', ')
                  ELSE NULL
              END,
              CASE
                  WHEN h.period10 IS TRUE THEN CONCAT('October', ', ')
                  ELSE NULL
              END,
              CASE
                  WHEN h.period11 IS TRUE THEN CONCAT('November', ', ')
                  ELSE NULL
              END,
              CASE
                  WHEN h.period12 IS TRUE THEN 'December'
                  END
              ) AS "Period",
       c.pratiques_sportives AS "Sport practices",
       r.rules  AS "Rules",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        b.url_{{ lang }} AS "URL {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.description_{{ lang }} AS "Description {{ lang }}",
       {% endfor %}
       a.contact AS "Contact",
       CASE
           WHEN a.published IS FALSE THEN 'No'
           WHEN a.published IS TRUE THEN 'Yes'
       END AS "Published",
       a.date_insert AS "Insertion date",
       a.date_update AS "Modifiation date",
       a.publication_date AS "Publication date",
       a.geom
FROM sensitivity_sensitivearea a
LEFT JOIN sensitivity_species b ON a.species_id = b.id
LEFT JOIN
    (SELECT species_id,
            array_to_string(ARRAY_AGG (b.name ORDER BY b.id), ', ', '_') pratiques_sportives,
            c.name AS "Nom"
     FROM sensitivity_species_practices a
     JOIN sensitivity_sportpractice b ON a.sportpractice_id = b.id
     JOIN sensitivity_species c ON a.species_id = c.id
     GROUP BY species_id,
              c.name) c ON a.species_id = c.species_id
LEFT JOIN (
    SELECT
        ssr.sensitivearea_id,
        array_to_string(array_agg(sr.name ORDER BY sr.id), ', '::text, '_'::text) AS rules
    FROM sensitivity_sensitivearea_rules AS ssr
    JOIN sensitivity_rule AS sr
    ON ssr.rule_id = sr.id
    GROUP BY ssr.sensitivearea_id
) r ON r.sensitivearea_id = a.id
LEFT JOIN sensitivity_species h ON a.species_id = h.id
LEFT JOIN authent_structure d ON a.structure_id = d.id
LEFT JOIN LATERAL (
     SELECT array_to_string(array_agg(b_1.name ORDER BY b_1.name), ', '::text, '_'::text) AS zoning_city
           FROM   zoning_city b_1
            WHERE st_intersects(a.geom, b_1.geom)
          GROUP BY a.id
    ) f ON true
LEFT JOIN LATERAL (
        SELECT array_to_string(array_agg(b_1.name ORDER BY b_1.name), ', '::text, '_'::text) AS zoning_district
           FROM  zoning_district b_1
            WHERE st_intersects(a.geom, b_1.geom)
          GROUP BY a.id
    ) g ON true
WHERE deleted IS FALSE
;

