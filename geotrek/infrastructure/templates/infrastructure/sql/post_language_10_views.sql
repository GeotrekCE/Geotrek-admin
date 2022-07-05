CREATE VIEW {{ schema_geotrek }}.v_infrastructures AS (
	SELECT e.geom, e.id, e.uuid, t.*
	FROM infrastructure_infrastructure AS t, infrastructure_infrastructuretype AS b, core_topology AS e
	WHERE t.topo_object_id = e.id AND t.type_id = b.id
	AND e.deleted = FALSE
);

-- Infrastructures


CREATE VIEW {# geotrek.maintenance #}.v_infrastructures_qgis AS WITH v_infra AS
    (SELECT e.geom,
            e.id,
            t.published,
            t.publication_date,
            t.topo_object_id,
            t.name,
            t.description,
            CONCAT ('Min: ', e.min_elevation, 'm') AS altitude,
            t.implantation_year,
            t.condition_id,
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
       i.name AS "Structure liée",
       f.zoning_city AS "Commune",
       g.zoning_district AS "Zone",
       a.name AS "Nom",
       b.label AS "Type",
       c.label AS "État",
       a.description AS "Description",
       a.altitude AS "Altitude",
       a.implantation_year AS "Année d'implantation",
       d.label AS "Niveau des usagers",
       e.label AS "Niveau des interventions",
       CASE
           WHEN a.published IS TRUE THEN 'Oui'
           ELSE 'Non'
       END AS "Publié",
       a.date_insert AS "Date d'insertion",
       a.date_update AS "Date de modification",
       a.geom
FROM v_infra a
LEFT JOIN infrastructure_infrastructuretype b ON a.type_id = b.id
LEFT JOIN infrastructure_infrastructurecondition c ON a.condition_id = c.id
LEFT JOIN infrastructure_infrastructureusagedifficultylevel d ON a.usage_difficulty_id = d.id
LEFT JOIN infrastructure_infrastructuremaintenancedifficultylevel e ON a.maintenance_difficulty_id = e.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_city,
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
     JOIN zoning_city b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_district,
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
     JOIN zoning_district b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) g ON a.id = g.id
LEFT JOIN authent_structure i ON a.structure_id = i.id 
;