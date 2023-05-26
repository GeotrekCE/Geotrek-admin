-- Signalétique

CREATE VIEW {{ schema_geotrek }}.v_signages AS WITH v_signage_tmp AS
    (SELECT e.id,
            {% for lang in MODELTRANSLATION_LANGUAGES %}
                t.published_{{ lang }},
            {% endfor %}
            t.publication_date,
            t.topo_object_id,
            {% for lang in MODELTRANSLATION_LANGUAGES %}
                t.name_{{ lang }},
            {% endfor %}
            {% for lang in MODELTRANSLATION_LANGUAGES %}
                t.description_{{ lang }},
            {% endfor %}
            t.implantation_year,
            t.eid,
            t.code,
            t.printed_elevation,
            t.manager_id,
            t.condition_id,
            t.sealing_id,
            t.structure_id,
            t.type_id,
            CONCAT (e.min_elevation, 'm') AS elevation,
            e.geom
     FROM signage_signage t,
          signage_signagetype b,
          core_topology e
     WHERE t.topo_object_id = e.id
         AND t.type_id = b.id
         AND e.deleted = FALSE )
SELECT a.id,
       e.name AS "Structure",
       f.zoning_city AS "City",
       g.zoning_district AS "District",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.name_{{ lang }} AS "Name {{ lang }}",
       {% endfor %}
       a.code AS "Code",
       b.label AS "Type",
       c.label AS "State",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.description_{{ lang }} AS "Description {{ lang }}",
       {% endfor %}
       a.implantation_year AS "Implantation year",
       a.printed_elevation AS "Printed elevation",
       concat('X : ', st_x(st_transform(a.geom,{{ API_SRID }}))::numeric(9,7),
              ' / Y : ', st_y(st_transform(a.geom,{{ API_SRID }}))::numeric(9,7),
              ' ({{ spatial_reference }})') AS "Coordinates",
       d.label AS "Sealing",
       h.organism AS "Manager",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
           CASE
               WHEN a.published_{{ lang }} IS FALSE THEN 'No'
               WHEN a.published_{{ lang }} IS TRUE THEN 'Yes'
           END AS "Published {{ lang }}",
       {% endfor %}
       a.elevation AS "Elevation",
       a.publication_date AS "Insertion date",
       a.geom
FROM v_signage_tmp a
LEFT JOIN signage_signagetype b ON a.type_id = b.id
LEFT JOIN infrastructure_infrastructurecondition c ON a.condition_id = c.id
LEFT JOIN signage_sealing d ON a.sealing_id = d.id
LEFT JOIN authent_structure e ON a.structure_id = e.id
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
LEFT JOIN
    (SELECT organism,
            b.topo_object_id
     FROM common_organism a
     JOIN signage_signage b ON a.id = b.manager_id) h ON a.topo_object_id = h.topo_object_id
;