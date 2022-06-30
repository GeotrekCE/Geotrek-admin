CREATE VIEW {{ schema_geotrek }}.v_trails AS (
    SELECT core_topology.geom, core_topology.id, core_topology.uuid, core_trail.*
    FROM core_trail, core_topology
    WHERE core_trail.topo_object_id = core_topology.id
    AND core_topology.deleted = FALSE
);

-- Sentiers

CREATE VIEW {# geotrek.core #}.v_trail_qgis 
AS WITH v_trails AS
    (SELECT core_topology.geom,
            core_topology.id,
            core_trail.structure_id,
            core_trail.name,
            core_trail.departure,
            core_trail.arrival,
            core_trail.comments,
            CONCAT ('MIN: ', core_topology.min_elevation, 'm, MAX: ', core_topology.max_elevation, 'm') AS altitude,
            core_trail.topo_object_id,
            core_trail.eid
     FROM core_trail,
          core_topology
     WHERE core_trail.topo_object_id = core_topology.id
         AND core_topology.deleted = FALSE)
SELECT a.id,
       d.name AS "Structure liée",
       f.zoning_city AS "Commune",
       g.zoning_district AS "Zone",
       a.name AS "Nom",
       a.departure AS "Départ",
       a.arrival AS "Arrivée",
       a.comments AS "Commentaires",
       a.altitude AS "Altitude",
       a.geom
FROM v_trails a
LEFT JOIN authent_structure d ON a.structure_id = d.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_city,
            a.id
     FROM
         (SELECT core_topology.geom,
                 core_topology.id
          FROM core_trail,
               core_topology
          WHERE core_trail.topo_object_id = core_topology.id
              AND core_topology.deleted = FALSE) a
     JOIN zoning_city b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_district,
            a.id
     FROM
         (SELECT core_topology.geom,
                 core_topology.id
          FROM core_trail,
               core_topology
          WHERE core_trail.topo_object_id = core_topology.id
              AND core_topology.deleted = FALSE) a
     JOIN zoning_district b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) g ON a.id = g.id 
--WHERE g.name != 'Pyrénées'
;