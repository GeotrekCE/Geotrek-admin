-- Parcours outdoor

CREATE VIEW {{ schema_geotrek }}.v_outdoor_courses AS
WITH outdoor_course_geom AS (
    SELECT  ST_CollectionExtract(geom, 3)  AS geom, id
    FROM public.outdoor_course AS os
    UNION
    SELECT  ST_CollectionExtract(geom, 2)  AS geom, id
    FROM public.outdoor_course AS os
    UNION
    SELECT  ST_CollectionExtract(geom, 1)  AS geom, id
    FROM public.outdoor_course AS os
  )
SELECT a.id,
       b.name AS "Structure",
       c.zoning_city AS "City",
       d.zoning_district AS "District",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.name_{{ lang }} AS "Name {{lang}}",
       {% endfor %}
       g.site AS "Sites",
       i.filieres AS "Sectors",
       h.pratique AS "Practice",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.ratings_description_{{ lang }} AS "Ratings description {{ lang }}",
       {% endfor %}
       e.name AS "Type",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.description_{{ lang }} AS "Description {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.advice_{{ lang }} AS "Advice {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.gear_{{ lang }} AS "Gear {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.equipment_{{ lang }} AS "Equipment {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.accessibility AS "Accessibility {{ lang }}",
       {% endfor %}
       CASE
           WHEN a.height IS NOT NULL THEN concat(a.height, ' m')
           ELSE NULL
       END AS "Height",
       a.duration AS "Duration",
       a.eid AS "External id",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
           CASE
               WHEN a.published_{{ lang }} IS FALSE THEN 'No'
               WHEN a.published_{{ lang }} IS TRUE THEN 'Yes'
           END AS "Published {{ lang }}",
       {% endfor %}
       concat ('→ ', a.length::numeric(10, 1),' m (↝', st_length(a.geom_3d)::numeric(10, 1),' m)') AS "Humanize length",
       a.length AS "Length",
       st_length(a.geom_3d) AS "Length 3d",
       CASE
           WHEN a.ascent > 0 THEN concat (a.descent,'m +',a.ascent,'m (',a.slope::numeric(10, 1),')')
           WHEN a.ascent < 0 THEN concat (a.descent,'m -',a.ascent,'m (',a.slope::numeric(10, 1),')')
       END AS "Slope",
       CONCAT (a.min_elevation, 'm') AS "Minimum elevation",
       CONCAT (a.max_elevation, 'm') AS "Maximum elevation",
       a.date_insert AS "Insertion date",
       a.date_update AS "Update date",
       sg.geom AS geom
FROM outdoor_course a
JOIN outdoor_course_geom sg ON a.id = sg.id AND NOT ST_IsEmpty(sg.geom)
LEFT JOIN authent_structure b ON a.structure_id = b.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name ORDER BY b.name), ', ', '_') zoning_city,
            a.id
     FROM
         outdoor_course a
     JOIN zoning_city b ON ST_INTERSECTS (a.geom, b.geom)
     GROUP BY a.id) c ON a.id = c.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name ORDER BY b.name), ', ', '_') zoning_district,
            a.id
     FROM
         outdoor_course a
     JOIN zoning_district b ON ST_INTERSECTS (a.geom, b.geom)
     GROUP BY a.id) d ON a.id = d.id
LEFT JOIN outdoor_coursetype e ON a.type_id = d.id
LEFT JOIN
    (SELECT b.id,
            array_to_string(ARRAY_AGG (c.name ORDER BY c.id), ', ', '_') site
     FROM outdoor_course_parent_sites a
     JOIN outdoor_course b ON a.course_id = b.id
     JOIN outdoor_site c ON a.site_id = c.id
     GROUP BY b.id) g ON a.id = g.id
LEFT JOIN
    (WITH site_pratique AS
         (SELECT b.id,
                 array_to_string(ARRAY_AGG (c.name ORDER BY c.id), ', ', '_') site
          FROM outdoor_course_parent_sites a
          JOIN outdoor_course b ON a.course_id = b.id
          JOIN outdoor_site c ON a.site_id = c.id
          GROUP BY b.id) SELECT a.id,
                                a.site,
                                b.pratique
     FROM site_pratique a
     JOIN
         (WITH pratique AS
              (SELECT c.id,
                      array_to_string(ARRAY_AGG (c.name ORDER BY c.id), ', ', '_') site
               FROM outdoor_course_parent_sites a
               JOIN outdoor_course b ON a.course_id = b.id
               JOIN outdoor_site c ON a.site_id = c.id
               GROUP BY c.id) SELECT a.id,
                                     a.site,
                                     b.pratique
          FROM pratique a
          JOIN
              (SELECT a.id,
                      array_to_string(ARRAY_AGG (b.name ORDER BY b.id), ', ', '_') pratique
               FROM outdoor_site a
               JOIN outdoor_practice b ON a.practice_id = b.id
               GROUP BY a.id) b ON a.id = b.id) b ON a.site= b.site) h ON a.id = h.id
LEFT JOIN
    (WITH site_filieres AS
         (SELECT b.id,
                 array_to_string(ARRAY_AGG (c.name ORDER BY c.id), ', ', '_') site
          FROM outdoor_course_parent_sites a
          JOIN outdoor_course b ON a.course_id = b.id
          JOIN outdoor_site c ON a.site_id = c.id
          GROUP BY b.id) SELECT a.id,
                                a.site,
                                b.filieres
     FROM site_filieres a
     JOIN
         (WITH filieres AS
              (SELECT c.id,
                      array_to_string(ARRAY_AGG (c.name ORDER BY c.id), ', ', '_') site
               FROM outdoor_course_parent_sites a
               JOIN outdoor_course b ON a.course_id = b.id
               JOIN outdoor_site c ON a.site_id = c.id
               GROUP BY c.id) SELECT a.id,
                                     a.site,
                                     b.filieres
          FROM filieres a
          JOIN
              (SELECT a.id,
                      array_to_string(ARRAY_AGG (c.name ORDER BY c.id), ', ', '_') filieres
               FROM outdoor_site a
               JOIN outdoor_practice b ON a.practice_id = b.id
               JOIN outdoor_sector c ON b.sector_id = c.id
               GROUP BY a.id) b ON a.id = b.id) b ON a.site = b.site) i ON a.id = i.id;


-- Sites outdoor

CREATE VIEW {{ schema_geotrek }}.v_outdoor_sites AS
WITH outdoor_site_geom AS (
    SELECT  ST_CollectionExtract(geom, 3)  AS geom, id
    FROM public.outdoor_site AS os
    UNION
    SELECT  ST_CollectionExtract(geom, 2)  AS geom, id
    FROM public.outdoor_site AS os
    UNION
    SELECT  ST_CollectionExtract(geom, 1)  AS geom, id
    FROM public.outdoor_site AS os
  )
SELECT a.id,
       b.name AS "Structure",
       c.zoning_city AS "City",
       d.zoning_district AS "District",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.name_{{ lang }} AS "Name {{ lang }}",
       {% endfor %}
       n.enfants AS "Children",
       o.parents AS "Parents",
       p.filieres AS "Sectors",
       f.name AS "Practice",
       m."Ratings",
       e.name AS "Type",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        description_teaser_{{ lang }} AS "Description teaser {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.ambiance_{{ lang }} AS "Ambiance {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.description_{{ lang }} AS "Description {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.advice_{{ lang }} AS "Advice {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.accessibility_{{ lang }} AS "Accessibility {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
        a.period_{{ lang }} AS "Period {{ lang }}",
       {% endfor %}
       a.orientation AS "Orientation",
       a.wind AS "Wind",
       k.etiquettes AS "Label",
       g.lieux_renseignement AS "Information desk",
       i.url AS "Web link",
       j.portail AS "Portal",
       h.name AS "Source",
       l.gestionnaire AS "Manager",
       a.eid AS "External ID",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
           CASE
               WHEN a.published_{{ lang }} IS FALSE THEN 'No'
               WHEN a.published_{{ lang }} IS TRUE THEN 'Yes'
           END AS "Published {{ lang }}",
       {% endfor %}
       CONCAT (a.min_elevation, 'm') AS "Minimum elevation",
       CONCAT (a.max_elevation, 'm') AS "Maximum elevation",
       a.date_insert AS "Insertion date",
       a.date_update AS "Update date",
       sg.geom AS geom
FROM public.outdoor_site a
JOIN outdoor_site_geom sg ON a.id = sg.id AND NOT ST_IsEmpty(sg.geom)
LEFT JOIN authent_structure b ON a.structure_id = b.id
LEFT JOIN LATERAL (
     SELECT array_to_string(array_agg(b_1.name ORDER BY b_1.name), ', '::text, '_'::text) AS zoning_city
           FROM   zoning_city b_1
            WHERE st_intersects(a.geom, b_1.geom)
          GROUP BY a.id
    ) c ON true
LEFT JOIN LATERAL (
        SELECT array_to_string(array_agg(b_1.name ORDER BY b_1.name), ', '::text, '_'::text) AS zoning_district
           FROM  zoning_district b_1
            WHERE st_intersects(a.geom, b_1.geom)
          GROUP BY a.id
    ) d ON true
LEFT JOIN outdoor_sitetype e ON a.type_id = e.id
LEFT JOIN outdoor_practice f ON a.practice_id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name ORDER BY b.id), ', ', '_') lieux_renseignement,
            c.id
     FROM outdoor_site_information_desks a
     JOIN tourism_informationdesk b ON a.informationdesk_id =b.id
     JOIN outdoor_site c ON a.site_id = c.id
     GROUP BY c.id) g ON a.id = g.id
LEFT JOIN
    (SELECT a.name,
            c.id
     FROM common_recordsource a
     JOIN outdoor_site_source b ON a.id = b.recordsource_id
     JOIN outdoor_site c ON b.site_id = c.id) h ON a.id = h.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.url ORDER BY b.id), ', ', '_') url,
            d.id
     FROM outdoor_site_web_links a
     JOIN trekking_weblink b ON a.weblink_id = b.id
     JOIN trekking_weblinkcategory c ON b.category_id = c.id
     JOIN outdoor_site d ON d.id = a.site_id
     GROUP BY d.id) i ON a.id = i.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name ORDER BY b.id), ', ', '_') portail,
            c.id
     FROM outdoor_site_portal a
     JOIN common_targetportal b ON a.targetportal_id =b.id
     JOIN outdoor_site c ON a.site_id = c.id
     GROUP BY c.id) j ON a.id = j.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (c.name ORDER BY c.id), ', ', '_') etiquettes,
            d.id
     FROM outdoor_site_labels a
     JOIN trekking_trek_labels b ON a.label_id = b.id
     JOIN common_label c ON b.label_id = c.id
     JOIN outdoor_site d ON a.site_id = d.id
     GROUP BY d.id) k ON a.id = k.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.organism ORDER BY b.id), ', ', '_') gestionnaire,
            c.id
     FROM outdoor_site_managers a
     JOIN common_organism b ON a.organism_id =b.id
     JOIN outdoor_site c ON a.site_id = c.id
     GROUP BY c.id) l ON a.id = l.id
LEFT JOIN
    (WITH ratings AS
         (SELECT d.id,
                 b.name as "Name ratingscale",
                 a.name as "Name"
          FROM outdoor_rating a
          JOIN outdoor_ratingscale b ON a.scale_id = b.id
          JOIN outdoor_site_ratings c ON a.id= c.rating_id
          JOIN outdoor_site d ON c.site_id = d.id),
         by_rating_scales AS
         (SELECT id, "Name ratingscale", array_to_string(array_agg("Name"), ', ', NULL) AS "Name as string" From ratings group by "Name ratingscale", id)
    SELECT id, array_to_string(array_agg(array["Name ratingscale", "Name as string"]), ' : ', NULL) AS "Ratings" FROM by_rating_scales group by id) m ON a.id = m.id
LEFT JOIN
    (SELECT parent_id,
            array_to_string(ARRAY_AGG (name ORDER BY id), ', ', '_') enfants
     FROM public.outdoor_site
     WHERE parent_id IS NOT NULL
     GROUP BY parent_id) n ON a.id = n.parent_id
LEFT JOIN
    (SELECT b.id,
            array_to_string(ARRAY_AGG (a.name ORDER BY a.id), ', ', '_') parents
     FROM outdoor_site a
     JOIN outdoor_site b ON a.id = b.parent_id
     GROUP BY b.id) o ON a.id = o.id
LEFT JOIN
    (SELECT a.id,
            array_to_string(ARRAY_AGG (c.name ORDER BY c.id), ', ', '_') filieres
     FROM outdoor_site a
     JOIN outdoor_practice b ON a.practice_id = b.id
     JOIN outdoor_sector c ON b.sector_id = c.id
     GROUP BY a.id) p ON a.id = p.id;
