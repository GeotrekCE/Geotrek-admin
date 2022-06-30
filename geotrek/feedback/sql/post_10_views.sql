
-- Signalement

CREATE VIEW {# geotrek.feedback #}.v_report_qgis AS
SELECT a.id,
       f.zoning_city AS "Commune",
       g.zoning_district AS "Zone",
       email AS "Courriel",
       b.label AS "Activité",
       c.label AS "Catégorie",
       d.label AS "Statut",
       d.label AS "Nature du problème",
       a.date_insert AS "Date d'insertion",
       a.date_update AS "Date de modification",
       a.comment AS "Commentaire",
       a.geom
FROM public.feedback_report a
LEFT JOIN public.feedback_reportactivity b ON a.activity_id = b.id
LEFT JOIN public.feedback_reportcategory c ON a.category_id = c.id
LEFT JOIN public.feedback_reportstatus d ON a.status_id = d.id
LEFT JOIN public.feedback_reportproblemmagnitude e ON a.problem_magnitude_id = e.id
LEFT JOIN (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_city,
            a.id
     FROM       feedback_report a
     JOIN zoning_city b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_district,
            a.id
     FROM            feedback_report a
     JOIN zoning_district b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) g ON a.id = g.id
WHERE deleted IS FALSE 
--AND g.name != 'Pyrénées'
;
