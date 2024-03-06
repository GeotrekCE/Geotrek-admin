-- Itinéraires


CREATE VIEW {{ schema_geotrek }}.v_treks AS WITH v_treks AS
    (SELECT e.geom,
            e.geom_3d,
            e.id,
            e.length,
            e.slope,
            e.ascent,
            e.descent,
            i.topo_object_id,
            {% for lang in MODELTRANSLATION_LANGUAGES %}
              i.name_{{ lang }},
              i.arrival_{{ lang }},
              i.departure_{{ lang }},
              i.published_{{ lang }},
              i.description_teaser_{{ lang }},
              i.description_{{ lang }},
              i.ambiance_{{ lang }},
              i.access_{{ lang }},
              i.advised_parking_{{ lang }},
              i.public_transport_{{ lang }},
              i.advice_{{ lang }},
              i.accessibility_advice_{{ lang }},
              i.accessibility_infrastructure_{{ lang }},
              i.accessibility_signage_{{ lang }},
              i.accessibility_slope_{{ lang }},
              i.accessibility_covering_{{ lang }},
              i.accessibility_exposure_{{ lang }},
              i.accessibility_width_{{ lang }},
              i.gear_{{ lang }},
            {% endfor %}
            i.duration,
            i.parking_location,
            i.route_id,
            i.difficulty_id,
            i.publication_date,
            i.points_reference,
            i.practice_id,
            i.structure_id,
            i.review,
            i.eid,
            i.eid2,
            CONCAT (e.min_elevation, 'm') AS min_elevation,
            CONCAT (e.max_elevation, 'm') AS max_elevation,
            i.reservation_id,
            i.reservation_system_id,
            e.date_insert,
            e.date_update
     FROM trekking_trek i,
          core_topology e
     WHERE i.topo_object_id = e.id
         AND e.deleted = FALSE)
SELECT a.id,
       e.name AS "Structure",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.name_{{ lang }} AS "Name {{ lang }}",
       {% endfor %}
       a.duration AS "Duration",
       CASE
           WHEN ascent > 0 THEN concat (descent,'m +',ascent,'m (',slope::numeric(10, 1),')')
           WHEN ascent < 0 THEN concat (descent,'m -',ascent,'m (',slope::numeric(10, 1),')')
       END AS "Slope",
       concat ('↝ ', a.length::numeric(10, 1),' m (→', st_length(geom_3d)::numeric(10, 1),' m)') AS "Humanize length",
       a.length AS "Length",
       st_length(geom_3d) AS "Length 3d",
       f.route AS "Route",
       b.difficulty AS "Difficulty",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        h_{{lang}}.name_label_{{ lang }} AS "Labels {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.departure_{{ lang }} AS "Departure {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.arrival_{{ lang }} AS "Arrival {{ lang }}",
       {% endfor %}
       a.min_elevation AS "Minimum elevation",
       a.max_elevation AS "Maximum elevation",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.ambiance_{{ lang }} AS "Ambiance {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.description_{{ lang }} AS "Description {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.description_teaser_{{ lang }} AS "Description teaser {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.access_{{ lang }} AS "Access {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.advice_{{ lang }} AS "Advice {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.advised_parking_{{ lang }} AS "Advised parking {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.public_transport_{{ lang }} AS "Public transport {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.gear_{{ lang }} AS "Gear {{ lang }}",
       {% endfor %}

       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.accessibility_infrastructure_{{ lang }} AS "Accessibility infrastructure {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.accessibility_signage_{{ lang }} AS "Accessibility signage {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.accessibility_exposure_{{ lang }} AS "Accessibility exposure {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.accessibility_slope_{{ lang }} AS "Accessibility slope {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.accessibility_covering_{{ lang }} AS "Accessibility covering {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.accessibility_width_{{ lang }} AS "Accessibility width {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.accessibility_advice_{{ lang }} AS "Accessibility advice {{ lang }}",
       {% endfor %}
       g.labels AS "Themes",
       d.name AS "Practice",
       m.accessibility AS "Accessibility",
       l.network AS "Network",
       n.itinerancy AS "Itinerancy",
       j.url AS "URL",
       k.information_desks AS "Information desks",
       i.name AS "Source",
       a.eid AS "External ID",
       a.eid2 AS "Second external id",
       c.name AS "Reservation system",
       a.reservation_id AS "Reservation ID",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
           CASE
            WHEN a.published_{{ lang }} IS FALSE THEN 'No'
            WHEN a.published_{{ lang }} IS TRUE THEN 'Yes'
           END AS "Published {{ lang }}",
       {% endfor %}
       a.date_insert AS "Insertion date",
       a.date_update AS "Update date",
       a.geom
FROM v_treks a
LEFT JOIN trekking_difficultylevel b ON a.difficulty_id = b.id
LEFT JOIN common_reservationsystem c ON a.reservation_system_id = c.id
LEFT JOIN trekking_practice d ON a.practice_id = d.id
LEFT JOIN authent_structure e ON a.structure_id = e.id
LEFT JOIN trekking_route f ON a.route_id = f.id
LEFT JOIN
    (SELECT b.id,
            array_to_string(ARRAY_AGG (d.label ORDER BY d.id), ',') labels
     FROM trekking_trek a
     JOIN core_topology b ON a.topo_object_id = b.id
     AND b.deleted = FALSE
     JOIN trekking_trek_themes c ON b.id = c.trek_id
     JOIN common_theme d ON d.id = c.theme_id
     GROUP BY b.id) g ON a.id = g.id
{% for lang in MODELTRANSLATION_LANGUAGES %}
    LEFT JOIN
        (SELECT array_to_string(ARRAY_AGG (a.name_{{ lang }} ORDER BY a.id), ',', '_') name_label_{{ lang }},
                c.topo_object_id
         FROM common_label a
         JOIN trekking_trek_labels b ON a.id = b.label_id
         JOIN trekking_trek c ON c.topo_object_id = b.trek_id
         GROUP BY topo_object_id) h_{{lang}} ON a.topo_object_id = h_{{lang}}.topo_object_id
{% endfor %}
LEFT JOIN
    (SELECT a.name,
            topo_object_id
     FROM common_recordsource a
     JOIN trekking_trek_source b ON a.id = b.recordsource_id
     JOIN trekking_trek c ON b.trek_id = c.topo_object_id) i ON a.topo_object_id = i.topo_object_id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (a.url ORDER BY a.id), ',', '_') url,
            d.topo_object_id
     FROM trekking_weblink a
     JOIN trekking_weblinkcategory b ON a.category_id = b.id
     JOIN trekking_trek_web_links c ON a.id = c.weblink_id
     JOIN trekking_trek d ON d.topo_object_id = c.trek_id
     GROUP BY topo_object_id) j ON a.topo_object_id = j.topo_object_id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (a.name ORDER BY a.id), ',', '_') information_desks,
            topo_object_id
     FROM tourism_informationdesk a
     JOIN trekking_trek_information_desks b ON a.id = b.informationdesk_id
     JOIN trekking_trek c ON b.trek_id = c.topo_object_id
     GROUP BY topo_object_id) k ON a.topo_object_id = k.topo_object_id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (a.network ORDER BY a.id), ',', '_') network,
            c.topo_object_id
     FROM trekking_treknetwork a
     JOIN trekking_trek_networks b ON a.id = b.treknetwork_id
     JOIN trekking_trek c ON b.trek_id = c.topo_object_id
     GROUP BY topo_object_id) l ON a.topo_object_id = l.topo_object_id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (a.name ORDER BY a.id), ',', '_') accessibility,
            c.topo_object_id
     FROM trekking_accessibility a
     JOIN trekking_trek_accessibilities b ON a.id = b.accessibility_id
     JOIN trekking_trek c ON b.trek_id = c.topo_object_id
     GROUP BY topo_object_id) m ON a.topo_object_id = m.topo_object_id
LEFT JOIN
    (SELECT b.topo_object_id,
            array_to_string(ARRAY_AGG (b.name ORDER BY a.id), ',', '_') itinerancy
     FROM trekking_orderedtrekchild a
     JOIN trekking_trek b ON a.parent_id = b.topo_object_id
     GROUP BY topo_object_id) n ON a.topo_object_id = n.topo_object_id ;
-- POI

CREATE VIEW {{ schema_geotrek }}.v_pois AS WITH v_poi AS
    (SELECT e.geom,
            e.id,
            i.topo_object_id,
            {% for lang in MODELTRANSLATION_LANGUAGES %}
                i.name_{{ lang }},
                i.description_{{ lang }},
                i.published_{{ lang }},
            {% endfor %}
            i.type_id,
            i.publication_date,
            i.structure_id,
            i.review,
            i.eid,
            CONCAT (e.min_elevation, ' m') AS elevation,
            e.date_insert,
            e.date_update
     FROM trekking_poi i,
          core_topology e
     WHERE i.topo_object_id = e.id
         AND e.deleted = FALSE)
SELECT a.id,
       c.name AS "Structure",
       f.zoning_city AS "City",
       g.zoning_district AS "District",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.name_{{ lang }} AS "Name {{ lang }}",
       {% endfor %}
       b.label AS "Type",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.description_{{ lang }} AS "Description {{ lang }}",
       {% endfor %}
       a.eid AS "External ID",
       a.elevation AS "Elevation",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
           CASE
               WHEN a.published_{{ lang }} IS FALSE THEN 'No'
               WHEN a.published_{{ lang }} IS TRUE THEN 'Yes'
           END AS "Published {{ lang }}",
       {% endfor %}
       a.publication_date AS "Publication date",
       a.date_insert AS "Insertion date",
       a.date_update AS "Update date",
       a.geom
FROM v_poi a
LEFT JOIN trekking_poitype b ON a.type_id = b.id
LEFT JOIN authent_structure c ON a.structure_id = c.id
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
;

--Services

CREATE OR REPLACE VIEW v_services AS WITH v_services AS
    (SELECT e.geom,
            e.id,
            i.topo_object_id,
            i.type_id,
            i.structure_id,
            i.eid,
            CONCAT (e.min_elevation, ' m') AS elevation,
            e.date_insert,
            e.date_update
     FROM trekking_service i,
          core_topology e
     WHERE i.topo_object_id = e.id
         AND e.deleted = FALSE)
SELECT a.id,
       c.name AS "Structure",
       f.zoning_city AS "City",
       g.zoning_district AS "District",
       b.name AS "Type",
       a.eid AS "External ID",
       a.elevation AS "Elevation",
       CASE
           WHEN b.published IS FALSE THEN 'No'
           WHEN b.published IS TRUE THEN 'Yes'
       END AS "Published",
       a.date_insert AS "Insertion date",
       a.date_update AS "Update date",
       a.geom
FROM v_services a
LEFT JOIN trekking_servicetype b ON a.type_id = b.id
LEFT JOIN authent_structure c ON a.structure_id = c.id
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
;