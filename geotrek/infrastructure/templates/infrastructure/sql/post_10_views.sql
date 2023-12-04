-- Infrastructures


CREATE VIEW {{ schema_geotrek }}.v_infrastructures AS WITH v_infra AS
    (SELECT e.geom,
            e.id,
            {% if PUBLISHED_BY_LANG %}
            {% for lang in MODELTRANSLATION_LANGUAGES %}
            t.published_{{ lang }},
            {% endfor %}
            {% else %}
            t.published,
            {% endif %}
            t.publication_date,
            t.topo_object_id,
            {% for lang in MODELTRANSLATION_LANGUAGES %}
            t.name_{{ lang }},
            {% endfor %}
            {% for lang in MODELTRANSLATION_LANGUAGES %}
            t.description_{{ lang }},
            {% endfor %}
            CONCAT (e.min_elevation, 'm') AS altitude,
            t.implantation_year,
            t.condition_id,
            t.access_id,
            t.structure_id,
            t.type_id,
            t.eid,
            t.maintenance_difficulty_id,
            t.usage_difficulty_id,
            e.date_insert,
            e.date_update
     FROM infrastructure_infrastructure t,
          infrastructure_infrastructuretype b,
          core_topology e
     WHERE t.topo_object_id = e.id
         AND t.type_id = b.id
         AND e.deleted = FALSE)
SELECT a.id,
       i.name AS "Structure",
       f.zoning_city AS "City",
       g.zoning_district AS "District",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
       a.name_{{ lang }} AS "Name {{ lang }}",
       {% endfor %}
       b.label AS "Type",
       c.label AS "Condition",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
       a.description_{{ lang }} AS "Description {{ lang }}",
       {% endfor %}
       a.altitude AS "Elevation",
       a.implantation_year AS "Implantation year",
       d.label AS "Usage difficulty",
       e.label AS "Maintenance difficulty",
       j.label AS "Access mean",
       {% if PUBLISHED_BY_LANG %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
       CASE
           WHEN a.published_{{ lang }} IS TRUE THEN 'Yes'
           ELSE 'No'
       END AS "Published {{ lang }}",
       {% endfor %}
       {% else %}
       CASE
           WHEN a.published IS TRUE THEN 'Yes'
           ELSE 'No'
       END AS "Published",
       {% endif %}
       a.date_insert AS "Insertion date",
       a.date_update AS "Update date",
       a.geom
FROM v_infra a
LEFT JOIN infrastructure_infrastructuretype b ON a.type_id = b.id
LEFT JOIN infrastructure_infrastructurecondition c ON a.condition_id = c.id
LEFT JOIN infrastructure_infrastructureusagedifficultylevel d ON a.usage_difficulty_id = d.id
LEFT JOIN infrastructure_infrastructuremaintenancedifficultylevel e ON a.maintenance_difficulty_id = e.id
LEFT JOIN infrastructure_infrastructureaccessmean j ON a.access_id = j.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name ORDER BY b.name), ', ', '_') zoning_city,
            a.id
     FROM
         (SELECT e.geom,
                 e.id
          FROM infrastructure_infrastructure t,
               infrastructure_infrastructuretype b,
               core_topology e
          WHERE t.topo_object_id = e.id
              AND t.type_id = b.id
              AND e.deleted = FALSE) a
     JOIN zoning_city b ON ST_INTERSECTS (a.geom, b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name ORDER BY b.name), ', ', '_') zoning_district,
            a.id
     FROM
         (SELECT e.geom,
                 e.id
          FROM infrastructure_infrastructure t,
               infrastructure_infrastructuretype b,
               core_topology e
          WHERE t.topo_object_id = e.id
              AND t.type_id = b.id
              AND e.deleted = FALSE) a
     JOIN zoning_district b ON ST_INTERSECTS (a.geom, b.geom)
     GROUP BY a.id) g ON a.id = g.id
LEFT JOIN authent_structure i ON a.structure_id = i.id 
;
