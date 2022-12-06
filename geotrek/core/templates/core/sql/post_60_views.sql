-- Sentiers

CREATE VIEW {{ schema_geotrek }}.v_trails
AS WITH v_trails AS
    (SELECT core_topology.geom,
            core_topology.id,
            core_trail.structure_id,
            core_trail.name,
            core_trail.departure,
            core_trail.arrival,
            core_trail.comments,
            CONCAT (core_topology.min_elevation, 'm') AS min_elevation,
            CONCAT (core_topology.max_elevation, 'm') AS max_elevation,
            core_trail.topo_object_id,
            core_trail.eid
     FROM core_trail,
          core_topology
     WHERE core_trail.topo_object_id = core_topology.id
         AND core_topology.deleted = FALSE)
SELECT a.id,
       d.name AS "Structure",
       f.zoning_city AS "City",
       g.zoning_district AS "District",
       a.name AS "Name",
       a.departure AS "Departure",
       a.arrival AS "Arrival",
       a.comments AS "Comments",
       a.min_elevation AS "Minimum elevation",
       a.max_elevation AS "Maximum elevation",
       a.geom
FROM v_trails a
LEFT JOIN authent_structure d ON a.structure_id = d.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name ORDER BY b.name), ', ', '_') zoning_city,
            a.id
     FROM
         (SELECT core_topology.geom,
                 core_topology.id
          FROM core_trail,
               core_topology
          WHERE core_trail.topo_object_id = core_topology.id
              AND core_topology.deleted = FALSE) a
     JOIN zoning_city b ON ST_INTERSECTS (a.geom, b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name ORDER BY b.name), ', ', '_') zoning_district,
            a.id
     FROM
         (SELECT core_topology.geom,
                 core_topology.id
          FROM core_trail,
               core_topology
          WHERE core_trail.topo_object_id = core_topology.id
              AND core_topology.deleted = FALSE) a
     JOIN zoning_district b ON ST_INTERSECTS (a.geom, b.geom)
     GROUP BY a.id) g ON a.id = g.id
;
