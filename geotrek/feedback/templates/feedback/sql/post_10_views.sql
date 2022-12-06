-- Report

CREATE VIEW {{ schema_geotrek }}.v_reports AS
SELECT a.id,
       f.zoning_city AS "City",
       g.zoning_district AS "District",
       email AS "Email",
       {% for lang in MODELTRANSLATION_LANGUAGES %}
       b.label_{{ lang }} AS "Activity {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
       c.label_{{ lang }} AS "Category {{ lang }}",
       {% endfor %}
       {% for lang in MODELTRANSLATION_LANGUAGES %}
       d.label_{{ lang }} AS "Status {{ lang }}",
       {% endfor %}
       a.date_insert AS "Insertion date",
       a.date_update AS "Update date",
       a.comment AS "Comment",
       a.geom
FROM public.feedback_report a
LEFT JOIN public.feedback_reportactivity b ON a.activity_id = b.id
LEFT JOIN public.feedback_reportcategory c ON a.category_id = c.id
LEFT JOIN public.feedback_reportstatus d ON a.status_id = d.id
LEFT JOIN public.feedback_reportproblemmagnitude e ON a.problem_magnitude_id = e.id
LEFT JOIN (SELECT array_to_string(ARRAY_AGG (b.name ORDER BY b.name), ', ', '_') zoning_city,
            a.id
     FROM       feedback_report a
     JOIN zoning_city b ON ST_INTERSECTS (a.geom, b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN (SELECT array_to_string(ARRAY_AGG (b.name ORDER BY b.name), ', ', '_') zoning_district,
            a.id
     FROM            feedback_report a
     JOIN zoning_district b ON ST_INTERSECTS (a.geom, b.geom)
     GROUP BY a.id) g ON a.id = g.id
WHERE deleted IS FALSE 
;
