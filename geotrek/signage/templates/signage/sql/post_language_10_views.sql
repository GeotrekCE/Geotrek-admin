CREATE VIEW {{ schema_geotrek }}.v_signages AS (
	SELECT e.geom, e.id, e.uuid, t.*
	FROM signage_signage AS t, signage_signagetype AS b, core_topology AS e
	WHERE t.topo_object_id = e.id AND t.type_id = b.id
	AND e.deleted = FALSE
);

-- Signalétique

CREATE VIEW {{ schema_geotrek }}.v_signages_qgis AS WITH v_signaletique AS
    (SELECT e.id,
            t.published,
            t.publication_date,
            t.topo_object_id,
            t.name,
            t.description,
            t.implantation_year,
            t.eid,
            t.code,
            t.printed_elevation,
            t.manager_id,
            t.condition_id,
            t.sealing_id,
            t.structure_id,
            t.type_id,
            CONCAT ('Min: ', e.min_elevation, 'm') AS altitude,
            e.geom
     FROM signage_signage t,
          signage_signagetype b,
          core_topology e
     WHERE t.topo_object_id = e.id
         AND t.type_id = b.id
         AND e.deleted = FALSE )
SELECT a.id,
       e.name AS "Structure liée",
       f.zoning_city AS "Commune",
       g.zoning_district AS "Zone",
       a.name AS "Nom",
       a.code AS "Code",
       b.label AS "Type",
       c.label AS "État",
       a.description AS "Description",
       a.implantation_year AS "Année d'implantation",
       a.printed_elevation AS "Altitude affichée",
       concat('X : ', st_x(st_transform(a.geom,32631))::int,' / Y : ',st_y(st_transform(a.geom,32631))::int,' (WGS 84 / UTM zone 31N)')AS "Coordonnées",
       d.label AS "Scellement",
       h.organism AS "Gestionnaire",
       CASE
           WHEN a.published IS FALSE THEN 'Non'
           WHEN a.published IS TRUE THEN 'Oui'
       END AS "Publié",
       a.altitude AS "Altitude",
       a.publication_date AS "Date d'insertion",
       a.geom
FROM v_signaletique a
LEFT JOIN signage_signagetype b ON a.type_id = b.id
LEFT JOIN infrastructure_infrastructurecondition c ON a.condition_id = c.id
LEFT JOIN signage_sealing d ON a.sealing_id = d.id
LEFT JOIN authent_structure e ON a.structure_id = e.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_city,
            a.id
     FROM
         (SELECT e.id,
                 e.geom
          FROM signage_signage t,
               signage_signagetype b,
               core_topology e
          WHERE t.topo_object_id = e.id
              AND t.type_id = b.id
              AND e.deleted = FALSE ) a
     JOIN zoning_city b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_district,
            a.id
     FROM
         (SELECT e.id,
                 e.geom
          FROM signage_signage t,
               signage_signagetype b,
               core_topology e
          WHERE t.topo_object_id = e.id
              AND t.type_id = b.id
              AND e.deleted = FALSE ) a
     JOIN zoning_district b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) g ON a.id = g.id
LEFT JOIN
    (SELECT organism,
            b.topo_object_id
     FROM common_organism a
     JOIN signage_signage b ON a.id = b.manager_id) h ON a.topo_object_id = h.topo_object_id 
;