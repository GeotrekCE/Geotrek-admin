
-- Contenus touristiques


CREATE VIEW {# geotrek.tourism #}.v_touristiccontent_qgis AS
SELECT a.id,
       c.name AS "Structure liée",
       f.zoning_city AS "Commune",
       g.zoning_district AS "Zone",
       a.name AS "Nom",
       b.label AS "Catégorie",
       CASE
           WHEN k.type1_label = 'Type d''usage' THEN k.labels
       END AS "Type d''usage",
       CASE
           WHEN k.type1_label = 'Label' THEN k.labels
       END AS "Label",
       CASE
           WHEN k.type1_label = 'Thématique' THEN k.labels
       END AS "Thématique",
       CASE
           WHEN m.type2_label = 'Label' THEN m.labels
       END AS "Label 2",
       CASE
           WHEN m.type2_label = 'Service' THEN m.labels
       END AS "Service",
       CASE
           WHEN m.type2_label IS NULL THEN m.labels
       END AS "Type 2",
       a.description AS "Description",
       p.labels AS "Thèmes",
       a.description_teaser AS "Chapeau",
       a.contact AS "Contact",
       a.email AS "Courriel",
       a.website AS "Site web",
       a.practical_info AS "Informations pratiques",
       CASE
           WHEN a.approved IS TRUE THEN 'oui'
           ELSE 'non'
       END AS "Labellisé",
       o.name AS "Source",
       CASE
           WHEN a.published IS FALSE THEN 'Non'
           WHEN a.published IS TRUE THEN 'Oui'
       END AS "Publié",
       a.eid AS "ID externe",
       d.name AS "Système de réservation",
       date_insert AS "Date d'insertion",
       date_update AS "Date de modification",
       a.geom
FROM tourism_touristiccontent a
LEFT JOIN tourism_touristiccontentcategory b ON a.category_id = b.id
LEFT JOIN
    (SELECT DISTINCT ON (a.id) a.id,
                        a.labels,
                        b.type1_label,
                        b.type2_label
     FROM
         (WITH labels AS
              (SELECT a.label,
                      c.id,
                      b.type1_label,
                      b.type2_label
               FROM tourism_touristiccontenttype a
               JOIN tourism_touristiccontentcategory b ON a.category_id = b.id
               JOIN tourism_touristiccontent c ON b.id = c.category_id
               AND b.id = c.category_id
               JOIN tourism_touristiccontent_type1 d ON d.touristiccontent_id = c.id
               AND d.touristiccontenttype1_id = a.id) SELECT array_to_string(ARRAY_AGG (label), ', ', '*') labels,
                                                             id
          FROM labels
          GROUP BY id) a
     INNER JOIN
         (SELECT a.label,
                 c.id,
                 b.type1_label,
                 b.type2_label
          FROM tourism_touristiccontenttype a
          JOIN tourism_touristiccontentcategory b ON a.category_id = b.id
          JOIN tourism_touristiccontent c ON b.id = c.category_id
          AND b.id = c.category_id
          JOIN tourism_touristiccontent_type1 d ON d.touristiccontent_id = c.id
          AND d.touristiccontenttype1_id = a.id) b ON a.id = b.id) k ON a.id = k.id
LEFT JOIN
    (SELECT DISTINCT ON (a.id) a.id,
                        a.labels,
                        b.type1_label,
                        b.type2_label
     FROM
         (WITH labels AS
              (SELECT a.label,
                      c.id,
                      b.type1_label,
                      b.type2_label
               FROM tourism_touristiccontenttype a
               JOIN tourism_touristiccontentcategory b ON a.category_id = b.id
               JOIN tourism_touristiccontent c ON b.id = c.category_id
               AND b.id = c.category_id
               JOIN tourism_touristiccontent_type2 e ON e.touristiccontent_id = c.id
               AND e.touristiccontenttype2_id = a.id) SELECT array_to_string(ARRAY_AGG (label), ', ', '*') labels,
                                                             id
          FROM labels
          GROUP BY id) a
     INNER JOIN
         (SELECT a.label,
                 c.id,
                 b.type1_label,
                 b.type2_label
          FROM tourism_touristiccontenttype a
          JOIN tourism_touristiccontentcategory b ON a.category_id = b.id
          JOIN tourism_touristiccontent c ON b.id = c.category_id
          AND b.id = c.category_id
          JOIN tourism_touristiccontent_type2 e ON e.touristiccontent_id = c.id
          AND e.touristiccontenttype2_id = a.id) b ON a.id = b.id) m ON a.id = m.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (label), ', ', '*') pratiques_sportives,
            c.id
     FROM common_theme a
     JOIN tourism_touristiccontent_themes b ON a.id = b.theme_id
     JOIN tourism_touristiccontent c ON c.id = b.touristiccontent_id
     GROUP BY c.id) n ON a.id = n.id
LEFT JOIN
    (SELECT a.name,
            c.id
     FROM common_recordsource a
     JOIN tourism_touristiccontent_source b ON a.id = b.recordsource_id
     JOIN tourism_touristiccontent c ON b.touristiccontent_id = c.id) o ON a.id = o.id
LEFT JOIN
    (SELECT c.id,
            array_to_string(ARRAY_AGG (a.label), ', ', '*') labels
     FROM common_theme a
     JOIN tourism_touristiccontent_themes b ON a.id = b.theme_id
     JOIN tourism_touristiccontent c ON b.touristiccontent_id = c.id
     GROUP BY c.id) p ON a.id = p.id
LEFT JOIN authent_structure c ON a.structure_id = c.id
LEFT JOIN common_reservationsystem d ON a.reservation_system_id = d.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_city,
            a.id
     FROM tourism_touristiccontent a
     JOIN zoning_city b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_district,
            a.id
     FROM tourism_touristiccontent a
     JOIN zoning_district b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) g ON a.id = g.id
WHERE deleted IS FALSE 
--AND g.name != 'Pyrénées'
;


-- Évènements touristiques


DROP VIEW IF EXISTS v_touristicevent_qgis;


CREATE OR REPLACE VIEW v_touristicevent_qgis AS
SELECT a.id,
       c.name AS "Structure liée",
       f.zoning_city AS "Commune",
       g.zoning_district AS "Zone",
       a.name AS "Nom",
       b.type AS "Type",
       a.contact AS "Contact",
       a.email AS "Courriel",
       a.website AS "Site web",
       a.practical_info AS "Informations pratiques",
       a.description AS "Description",
       h.labels AS "Thèmes",
       a.begin_date AS "Date de début",
       a.end_date AS "Date de fin",
       concat(a.duration, ' jours') AS "Durée",
       a.booking AS "Réservation",
       CASE
           WHEN a.published IS FALSE THEN 'Non'
           WHEN a.published IS TRUE THEN 'Oui'
       END AS "Publié",
       a.meeting_point AS "Lieu",
       a.organizer AS "Organisateur",
       a.accessibility AS "Accessibilité",
       a.participant_number AS "Nombre de participants",
       a.date_insert AS "Date d'insertion",
       a.date_update AS "Date de modification",
       a.geom
FROM public.tourism_touristicevent a
LEFT JOIN public.tourism_touristiceventtype b ON a.type_id = b.id
LEFT JOIN public.authent_structure c ON a.structure_id = c.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_city,
            a.id
     FROM tourism_touristicevent a
     JOIN zoning_city b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_district,
            a.id
     FROM tourism_touristicevent a
     JOIN zoning_district b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) g ON a.id = g.id
LEFT JOIN
    (SELECT c.id,
            array_to_string(ARRAY_AGG (a.label), ', ', '*') labels
     FROM common_theme a
     JOIN tourism_touristicevent_themes b ON a.id = b.theme_id
     JOIN tourism_touristicevent c ON b.touristicevent_id = c.id
     GROUP BY c.id) h ON a.id = h.id
WHERE deleted IS FALSE 
-- AND g.name != 'Pyrénées'
;

