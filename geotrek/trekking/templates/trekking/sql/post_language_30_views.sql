CREATE OR REPLACE VIEW {{ schema_geotrek }}.v_treks AS (
	SELECT e.geom, e.id, e.uuid, i.*
	FROM trekking_trek AS i, core_topology AS e
	WHERE i.topo_object_id = e.id
	AND e.deleted = FALSE
);

CREATE OR REPLACE VIEW {{ schema_geotrek }}.v_pois AS (
	SELECT e.geom, e.id, e.uuid, i.*
	FROM trekking_poi AS i, core_topology AS e
	WHERE i.topo_object_id = e.id
	AND e.deleted = FALSE
);

-- Itinéraires


CREATE VIEW {# geotrek.trekking #}.v_treks_qgis AS WITH v_trek AS
    (SELECT e.geom,
            e.geom_3d,
            e.id,
            e.length,
            e.slope,
            e.ascent,
            e.descent,
            i.topo_object_id,
            i.name,
            i.departure,
            i.arrival,
            i.published,
            i.description_teaser,
            i.description,
            i.ambiance,
            i.access, 
            --  i.disabled_infrastructure,
 i.duration,
 i.advised_parking,
 i.parking_location,
 i.public_transport,
 i.advice,
 i.route_id,
 i.difficulty_id,
 i.publication_date,
 i.points_reference,
 i.practice_id,
 i.structure_id,
 i.review,
 i.eid,
 i.eid2,
 CONCAT ('MIN: ', e.min_elevation, 'm, MAX: ', e.max_elevation, 'm') AS altitude,
 i.reservation_id,
 i.reservation_system_id
     FROM trekking_trek i,
          core_topology e
     WHERE i.topo_object_id = e.id
         AND e.deleted = FALSE)
SELECT a.id,
       e.name AS "Structure liée",
       a.name AS "Nom",
       TRUNC(a.duration) || ' jours' AS "Durée",
       CASE
           WHEN ascent > 0 THEN concat (descent,'m +',ascent,'m (',slope::numeric(10, 1),')')
           WHEN ascent < 0 THEN concat (descent,'m -',ascent,'m (',slope::numeric(10, 1),')')
       END AS "Pente",
       concat ('↝ ', a.length::numeric(10, 1),' m (→', st_length(geom_3d)::numeric(10, 1),' m)') AS "Longueur",
       f.route AS "Parcours",
       b.difficulty AS "Difficulté",
       CASE
           WHEN h.name_label IS NOT NULL THEN 'oui'
       END AS "Itinéraire inscrit au Plan Départemental des Itinéraires",
       a.departure AS "Départ",
       a.arrival AS "Arrivée",
       a.altitude AS "Altitude",
       a.ambiance AS "Ambiance",
       a.description AS "Description",
       a.description_teaser AS "Chapeau",
       a.access AS "Accès routiers",
       a.advice AS "Recommandations",
       a.advised_parking AS "Parking conseillé",
       a.public_transport AS "Transport en commun", 
       -- a.disabled_infrastructure AS "Aménagement handicapés",
 g.labels AS "Thèmes",
 d.name AS "Pratique",
 m.accessibilite AS "Accessibilité",
 l.network AS "Balisages",
 n.itinerance AS "Itinérance",
 j.url AS "Liens web",
 k.lieux_renseignement AS "Lieux de renseignement",
 i.name AS "Source",
 a.eid AS "ID externe",
 a.eid2 AS "Deuxième id externe",
 c.name AS "Système de réservation",
 a.reservation_id AS "ID de réservation",
 CASE
     WHEN a.published IS FALSE THEN 'Non'
     WHEN a.published IS TRUE THEN 'Oui'
 END AS "Publié",
 a.geom
FROM v_trek a
LEFT JOIN trekking_difficultylevel b ON a.difficulty_id = b.id
LEFT JOIN common_reservationsystem c ON a.reservation_system_id = c.id
LEFT JOIN trekking_practice d ON a.practice_id = d.id
LEFT JOIN authent_structure e ON a.structure_id = e.id
LEFT JOIN trekking_route f ON a.route_id = f.id
LEFT JOIN
    (SELECT b.id,
            array_to_string(ARRAY_AGG (d.label), ',
                                  ', '*') labels
     FROM trekking_trek a
     JOIN core_topology b ON a.topo_object_id = b.id
     AND b.deleted = FALSE
     JOIN trekking_trek_themes c ON b.id = c.trek_id
     JOIN common_theme d ON d.id = c.theme_id
     GROUP BY b.id) g ON a.id = g.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (a.name), ',
                                  ', '*') name_label,
            c.topo_object_id
     FROM common_label a
     JOIN trekking_trek_labels b ON a.id = b.label_id
     JOIN trekking_trek c ON c.topo_object_id = b.trek_id
     GROUP BY topo_object_id) h ON a.topo_object_id = h.topo_object_id
LEFT JOIN
    (SELECT a.name,
            topo_object_id
     FROM common_recordsource a
     JOIN trekking_trek_source b ON a.id = b.recordsource_id
     JOIN trekking_trek c ON b.trek_id = c.topo_object_id) i ON a.topo_object_id = i.topo_object_id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (a.url), ',
                                  ', '*') url,
            d.topo_object_id
     FROM trekking_weblink a
     JOIN trekking_weblinkcategory b ON a.category_id = b.id
     JOIN trekking_trek_web_links c ON a.id = c.weblink_id
     JOIN trekking_trek d ON d.topo_object_id = c.trek_id
     GROUP BY topo_object_id) j ON a.topo_object_id = j.topo_object_id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (a.name), ',
                                  ', '*') lieux_renseignement,
            topo_object_id
     FROM tourism_informationdesk a
     JOIN trekking_trek_information_desks b ON a.id = b.informationdesk_id
     JOIN trekking_trek c ON b.trek_id = c.topo_object_id
     GROUP BY topo_object_id) k ON a.topo_object_id = k.topo_object_id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (a.network), ',
                                  ', '*') network,
            c.topo_object_id
     FROM trekking_treknetwork a
     JOIN trekking_trek_networks b ON a.id = b.treknetwork_id
     JOIN trekking_trek c ON b.trek_id = c.topo_object_id
     GROUP BY topo_object_id) l ON a.topo_object_id = l.topo_object_id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (a.name), ',
                                  ', '*') accessibilite,
            c.topo_object_id
     FROM trekking_accessibility a
     JOIN trekking_trek_accessibilities b ON a.id = b.accessibility_id
     JOIN trekking_trek c ON b.trek_id = c.topo_object_id
     GROUP BY topo_object_id) m ON a.topo_object_id = m.topo_object_id
LEFT JOIN
    (SELECT b.topo_object_id,
            array_to_string(ARRAY_AGG (b.name), ',
                                  ', '*') itinerance
     FROM trekking_orderedtrekchild a
     JOIN trekking_trek b ON a.parent_id = b.topo_object_id
     GROUP BY topo_object_id) n ON a.topo_object_id = n.topo_object_id ;
-- POI

CREATE VIEW {# geotrek.trekking #}.v_pois_qgis AS WITH v_poi AS
    (SELECT e.geom,
            e.id,
            i.topo_object_id,
            i.name,
            i.description,
            i.type_id,
            i.published,
            i.publication_date,
            i.structure_id,
            i.review,
            i.eid,
            CONCAT ('Min: ', e.min_elevation, ' m') AS altitude
     FROM trekking_poi i,
          core_topology e
     WHERE i.topo_object_id = e.id
         AND e.deleted = FALSE)
SELECT a.id,
       c.name AS "Structure liée",
       f.zoning_city AS "Commune",
       g.zoning_district AS "Zone",
       a.name AS "Nom",
       b.label AS "Type",
       a.description AS "Description",
       a.eid AS "ID externe",
       a.altitude AS "Altitude",
       CASE
           WHEN a.published IS FALSE THEN 'Non'
           WHEN a.published IS TRUE THEN 'Oui'
       END AS "Publié",
       a.publication_date AS "Date d'insertion",
       a.geom
FROM v_poi a
LEFT JOIN trekking_poitype b ON a.type_id = b.id
LEFT JOIN authent_structure c ON a.structure_id = c.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_city,
            a.id
     FROM
         (SELECT e.geom,
                 e.id,
                 CONCAT ('Min: ', e.min_elevation, ' m') AS altitude
          FROM trekking_poi i,
               core_topology e
          WHERE i.topo_object_id = e.id
              AND e.deleted = FALSE) a
     JOIN zoning_city b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_district,
            a.id
     FROM
         (SELECT e.geom,
                 e.id,
                 CONCAT ('Min: ', e.min_elevation, ' m') AS altitude
          FROM trekking_poi i,
               core_topology e
          WHERE i.topo_object_id = e.id
              AND e.deleted = FALSE) a
     JOIN zoning_district b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) g ON a.id = g.id 
  --AND g.name != 'Pyrénées'
;

--Services

DROP VIEW IF EXISTS v_services_qgis;


CREATE OR REPLACE VIEW v_services_qgis AS WITH v_services AS
    (SELECT e.geom,
            e.id,
            i.topo_object_id,
            i.type_id,
            i.structure_id,
            i.eid,
            CONCAT ('Min: ', e.min_elevation, ' m') AS altitude,
            e.date_insert,
            e.date_update
     FROM trekking_service i,
          core_topology e
     WHERE i.topo_object_id = e.id
         AND e.deleted = FALSE)
SELECT a.id,
       c.name AS "Structure liée",
       f.zoning_city AS "Commune",
       g.zoning_district AS "Zone",
       b.name AS "Type",
       a.eid AS "ID externe",
       a.altitude AS "Altitude",
       CASE
           WHEN b.published IS FALSE THEN 'Non'
           WHEN b.published IS TRUE THEN 'Oui'
       END AS "Publié",
       a.date_insert AS "Date d'insertion",
       a.date_update AS "Date de modification",
       a.geom
FROM v_services a
LEFT JOIN trekking_servicetype b ON a.type_id = b.id
LEFT JOIN authent_structure c ON a.structure_id = c.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_city,
            a.id
     FROM
         (SELECT e.geom,
                 e.id
          FROM trekking_service i,
               core_topology e
          WHERE i.topo_object_id = e.id
              AND e.deleted = FALSE) a
     JOIN zoning_city b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_district,
            a.id
     FROM
         (SELECT e.geom,
                 e.id
          FROM trekking_service i,
               core_topology e
          WHERE i.topo_object_id = e.id
              AND e.deleted = FALSE) a
     JOIN zoning_district b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) g ON a.id = g.id 
--AND g.name != 'Pyrénées'
;