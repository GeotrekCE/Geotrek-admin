-- Report

CREATE VIEW {{ schema_geotrek }}.v_reports AS
SELECT a.id,
       g.zoning_city AS "City",
       h.zoning_district AS "District",
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
       f.name AS "Provider",
       a.geom
FROM public.feedback_report a
LEFT JOIN public.feedback_reportactivity b ON a.activity_id = b.id
LEFT JOIN public.feedback_reportcategory c ON a.category_id = c.id
LEFT JOIN public.feedback_reportstatus d ON a.status_id = d.id
LEFT JOIN public.feedback_reportproblemmagnitude e ON a.problem_magnitude_id = e.id
LEFT JOIN public.common_provider f ON a.provider_id = f.id
LEFT JOIN LATERAL (
     SELECT array_to_string(array_agg(b_1.name ORDER BY b_1.name), ', '::text, '_'::text) AS zoning_city
           FROM   zoning_city b_1
            WHERE st_intersects(a.geom, b_1.geom)
          GROUP BY a.id
    ) g ON true
LEFT JOIN LATERAL (
        SELECT array_to_string(array_agg(b_1.name ORDER BY b_1.name), ', '::text, '_'::text) AS zoning_district
           FROM  zoning_district b_1
            WHERE st_intersects(a.geom, b_1.geom)
          GROUP BY a.id
    ) h ON true
WHERE deleted IS FALSE 
;
