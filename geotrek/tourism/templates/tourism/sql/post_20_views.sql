
-- Contenus touristiques


CREATE VIEW {{ schema_geotrek }}.v_touristiccontents AS
SELECT a.id,
       c.name AS "Structure",
       f.zoning_city AS "City",
       g.zoning_district AS "District",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.name_{{ lang }} AS "Name {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        b.label_{{ lang }} AS "Category {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
           k.type1_label_{{ lang }} AS "Label's name type1 {{ lang }}",
           k.labels_{{ lang }} AS "Labels type1 {{ lang }}",
           m.type2_label_{{ lang }} AS "Label's name type2 {{ lang }}",
           m.labels_{{ lang }} AS "Labels type2 {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.description_{{ lang }} AS "Description {{ lang }}",
       {% endfor %}
       p.labels AS "Themes",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.description_teaser_{{ lang }} AS "Description teaser {{ lang }}",
       {% endfor %}
       a.contact AS "Contact",
       a.email AS "Email",
       a.website AS "Website",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.practical_info_{{ lang }} AS "Practical info {{ lang }}",
       {% endfor %}
       CASE
           WHEN a.approved IS TRUE THEN 'Yes'
           ELSE 'No'
       END AS "Approved",
       o.name AS "Source",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
           CASE
               WHEN a.published_{{ lang }} IS FALSE THEN 'No'
               WHEN a.published_{{ lang }} IS TRUE THEN 'Yes'
           END AS "Published {{ lang }}",
       {% endfor %}
       a.eid AS "External ID",
       d.name AS "Reservation system",
       a.date_insert AS "Insertion date",
       a.date_update AS "Update date",
       a.geom
FROM tourism_touristiccontent a
LEFT JOIN tourism_touristiccontentcategory b ON a.category_id = b.id
LEFT JOIN
    (SELECT DISTINCT ON (a.id) a.id,
                        {% for lang in MODELTRANSLATION_LANGUAGES %}
                            b.type1_label_{{ lang }},
                            a.labels_{{ lang }}{% if not forloop.last %},{% endif %}
                        {% endfor %}
     FROM
         (WITH labels AS
              (SELECT
                      {% for lang in MODELTRANSLATION_LANGUAGES %}
                        b.type1_label_{{ lang }},
                        a.label_{{ lang }},
                      {% endfor %}
                      c.id
               FROM tourism_touristiccontenttype a
               JOIN tourism_touristiccontentcategory b ON a.category_id = b.id
               JOIN tourism_touristiccontent c ON b.id = c.category_id
               AND b.id = c.category_id
               JOIN tourism_touristiccontent_type1 d ON d.touristiccontent_id = c.id
               AND d.touristiccontenttype1_id = a.id) SELECT {% for lang in MODELTRANSLATION_LANGUAGES %}array_to_string(ARRAY_AGG (label_{{ lang }} ORDER BY id), ', ', '_') labels_{{ lang }},{% endfor %}
                                                             id
          FROM labels
          GROUP BY id) a
     INNER JOIN
         (SELECT
                 {% for lang in MODELTRANSLATION_LANGUAGES %}
                    a.label_{{ lang }},
                    b.type1_label_{{ lang }},
                 {% endfor %}
                 c.id
          FROM tourism_touristiccontenttype a
          JOIN tourism_touristiccontentcategory b ON a.category_id = b.id
          JOIN tourism_touristiccontent c ON b.id = c.category_id
          AND b.id = c.category_id
          JOIN tourism_touristiccontent_type1 d ON d.touristiccontent_id = c.id
          AND d.touristiccontenttype1_id = a.id) b ON a.id = b.id) k ON a.id = k.id
LEFT JOIN
    (SELECT DISTINCT ON (a.id) a.id,
                        {% for lang in MODELTRANSLATION_LANGUAGES %}
                            b.type2_label_{{ lang }},
                            a.labels_{{ lang }}{% if not forloop.last %},{% endif %}
                        {% endfor %}
     FROM
         (WITH labels AS
              (SELECT
                      {% for lang in MODELTRANSLATION_LANGUAGES %}
                            b.type2_label_{{ lang }},
                            a.label_{{ lang }},
                      {% endfor %}
                      c.id
               FROM tourism_touristiccontenttype a
               JOIN tourism_touristiccontentcategory b ON a.category_id = b.id
               JOIN tourism_touristiccontent c ON b.id = c.category_id
               AND b.id = c.category_id
               JOIN tourism_touristiccontent_type2 e ON e.touristiccontent_id = c.id
               AND e.touristiccontenttype2_id = a.id) SELECT {% for lang in MODELTRANSLATION_LANGUAGES %}array_to_string(ARRAY_AGG (label_{{ lang }} ORDER BY id), ', ', '_') labels_{{ lang }},{% endfor %}
                                                             id
          FROM labels
          GROUP BY id) a
     INNER JOIN
         (SELECT
                 {% for lang in MODELTRANSLATION_LANGUAGES %}
                     b.type2_label_{{ lang }},
                     a.label_{{ lang }},
                 {% endfor %}
                 c.id
          FROM tourism_touristiccontenttype a
          JOIN tourism_touristiccontentcategory b ON a.category_id = b.id
          JOIN tourism_touristiccontent c ON b.id = c.category_id
          AND b.id = c.category_id
          JOIN tourism_touristiccontent_type2 e ON e.touristiccontent_id = c.id
          AND e.touristiccontenttype2_id = a.id) b ON a.id = b.id) m ON a.id = m.id
LEFT JOIN
    (SELECT a.name,
            c.id
     FROM common_recordsource a
     JOIN tourism_touristiccontent_source b ON a.id = b.recordsource_id
     JOIN tourism_touristiccontent c ON b.touristiccontent_id = c.id) o ON a.id = o.id
LEFT JOIN
    (SELECT c.id,
            array_to_string(ARRAY_AGG (a.label ORDER BY a.id), ', ', '_') labels
     FROM common_theme a
     JOIN tourism_touristiccontent_themes b ON a.id = b.theme_id
     JOIN tourism_touristiccontent c ON b.touristiccontent_id = c.id
     GROUP BY c.id) p ON a.id = p.id
LEFT JOIN authent_structure c ON a.structure_id = c.id
LEFT JOIN common_reservationsystem d ON a.reservation_system_id = d.id
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


-- Évènements touristiques


CREATE OR REPLACE VIEW v_touristicevents AS
SELECT a.id,
       c.name AS "Structure",
       f.zoning_city AS "City",
       g.zoning_district AS "District",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.name_{{ lang }} AS "Name {{ lang }}",
       {% endfor %}
       b.type AS "Type",
       p.name as "Place",
       a.contact AS "Contact",
       a.email AS "Email",
       a.website AS "Website",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.practical_info_{{ lang }} AS "Practical info {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.description_{{ lang }} AS "Description {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.description_teaser_{{ lang }} AS "Description teaser {{ lang }}",
       {% endfor %}
       h.labels AS "Themes",
       a.begin_date AS "Begin date",
       a.end_date AS "End date",
       a.start_time AS "Start time",
       a.end_time AS "End time",
       concat(a.duration, ' days') AS "Duration",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.booking_{{ lang }} AS "Booking {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
           CASE
               WHEN a.published_{{ lang }} IS FALSE THEN 'No'
               WHEN a.published_{{ lang }} IS TRUE THEN 'Yes'
           END AS "Published {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.meeting_point_{{ lang }} AS "Meeting point {{ lang }}",
       {% endfor %}
       d.label AS "Organizer",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.accessibility_{{ lang }} AS "Accessibility {{ lang }}",
       {% endfor %}
       a.capacity AS "Capacity",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.target_audience_{{ lang }} AS "Target audience {{ lang }}",
       {% endfor %}
        CASE
            WHEN a.bookable IS FALSE THEN 'No'
            WHEN a.bookable IS TRUE THEN 'Yes'
        END AS "Bookable {{ lang }}",
       a.cancelled AS "Canceled", 
       a.price AS "Price",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        cr.label_{{ lang }} AS "Cancellation reason {{ lang }}",
       {% endfor %}
       a.date_insert AS "Insertion date",
       a.date_update AS "Update date",
       a.geom
FROM public.tourism_touristicevent a
LEFT JOIN public.tourism_touristiceventtype b ON a.type_id = b.id
LEFT JOIN public.authent_structure c ON a.structure_id = c.id
LEFT JOIN public.tourism_touristiceventorganizer d ON a.organizer_id = d.id
LEFT JOIN public.tourism_cancellationreason cr ON a.cancellation_reason_id = cr.id
LEFT JOIN public.tourism_touristiceventplace p ON a.place_id = p.id
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
    (SELECT c.id,
            array_to_string(ARRAY_AGG (a.label ORDER BY a.id), ', ', '_') labels
     FROM common_theme a
     JOIN tourism_touristicevent_themes b ON a.id = b.theme_id
     JOIN tourism_touristicevent c ON b.touristicevent_id = c.id
     GROUP BY c.id) h ON a.id = h.id
WHERE deleted IS FALSE 
;

