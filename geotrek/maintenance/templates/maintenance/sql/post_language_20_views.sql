CREATE VIEW {{ schema_geotrek }}.v_interventions AS (

	SELECT e.geom, e.uuid, i.*
	FROM maintenance_intervention AS i, core_topology AS e,  signage_blade as b
	WHERE (i.target_id = e.id AND i.target_type_id NOT IN (SELECT id FROM django_content_type  AS ct WHERE ct.model = 'blade')) OR
	(i.target_id = b.id AND i.target_type_id IN (SELECT id FROM django_content_type  AS ct WHERE ct.model = 'blade') AND e.id=b.signage_id)
	AND i.deleted = FALSE
);

CREATE VIEW {{ schema_geotrek }}.v_projects AS (
	SELECT ST_Union(t.geom) AS geom, s.*
	FROM v_interventions AS t, maintenance_project AS s
	WHERE t.project_id = s.id
	GROUP BY t.project_id, s.id
);

-- Interventions


CREATE VIEW {# geotrek.maintenance #}.v_intervention_qgis AS
SELECT a.id,
       e.name AS "Structure liée",
       f.zoning_city AS "Commune",
       g.zoning_district AS "Zone",
       a.name AS "Nom",
       a.date AS "Date",
       d.stake AS "Enjeu",
       c.status AS "Statut",
       b.type AS "Type",
       CASE
           WHEN a.subcontracting IS FALSE THEN 'Non'
           WHEN a.subcontracting IS TRUE THEN 'Oui'
       END AS "Sous-traitance",
       i.disorder AS "Désordres",
       a.material_cost AS "Coût matériel",
       a.heliport_cost AS "Coût héliportage",
       a.subcontract_cost AS "Coût sous-traitance",
       j.job AS "Fonction",
       j.cost AS "Jours-Hommes",
       j.nb_days AS "Coût",
       (a.material_cost+a.heliport_cost+a.subcontract_cost)::float AS "Coût total",
       h.name AS "Chantier",
       CASE
           WHEN k.app_label = 'core' THEN 'Tronçons'
           WHEN k.app_label = 'infrastructure' THEN 'Aménagements'
       END AS "Objet lié",
       CONCAT ('Min: ', a.min_elevation, ' m, Max: ', a.max_elevation, ' m') AS "Altitude",
       CONCAT ('h: ',height::numeric(10, 2), 'm , L: ', a.LENGTH::numeric(10, 2),'m , l: ', width::numeric(10, 2),'m : ', area::numeric(10, 1), 'm²') AS "Dimensions",
       a.description AS "Description",
       a.date_insert AS "Date d'insertion",
       a.date_update AS "Date de modification",
       a.geom_3d
FROM maintenance_intervention a
LEFT JOIN maintenance_interventiontype b ON a.type_id = b.id
LEFT JOIN maintenance_interventionstatus c ON a.status_id = c.id
LEFT JOIN core_stake d ON a.stake_id = d.id
LEFT JOIN authent_structure e ON a.structure_id = e.id
LEFT JOIN maintenance_project h ON a.project_id = h.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_city,
            a.id
     FROM maintenance_intervention a
     JOIN zoning_city b ON ST_INTERSECTS (st_pointonsurface(a.geom_3d), b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_district,
            a.id
     FROM maintenance_intervention a
     JOIN zoning_district b ON ST_INTERSECTS (st_pointonsurface(a.geom_3d), b.geom)
     GROUP BY a.id) g ON a.id = g.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (disorder), ', ', '*') disorder,
            c.id
     FROM maintenance_interventiondisorder a
     JOIN maintenance_intervention_disorders b ON a.id = b.interventiondisorder_id
     JOIN maintenance_intervention c ON b.intervention_id = c.id
     GROUP BY c.id) i ON a.id = i.id
LEFT JOIN
    (SELECT a.id,
            sum(b.nb_days)nb_days,
            max(c.job) job,
            sum(c.cost) "cost"
     FROM maintenance_intervention a
     JOIN maintenance_manday b ON a.id = b.intervention_id
     JOIN maintenance_interventionjob c ON c.id= b.job_id
     GROUP BY a.id) j ON a.id = j.id
LEFT JOIN
    (SELECT target_type_id,
            b.app_label
     FROM public.maintenance_intervention a
     JOIN django_content_type b ON a.target_type_id = b.id
     GROUP BY target_type_id,
              app_label) k ON a.target_type_id = k.target_type_id
JOIN core_topology l ON a.target_id = l.id
WHERE a.deleted = FALSE 
 ;

-- Chantiers

CREATE VIEW {# geotrek.maintenance #}.v_project_qgis AS
SELECT a.id,
       c.name AS "Structure liée",
       a.name AS "Nom",
       COALESCE(a.begin_year::varchar || ' - ' || a.end_year::varchar, a.begin_year::varchar, a.end_year::varchar) AS "Période",
       b.type AS "Type",
       e.domain AS "Domaine",
       a.begin_year AS "Année de début",
       a.end_year AS "Année de fin",
       a.global_cost AS "Coût global",
       a."constraint" AS "Contraintes",
       h.organism AS "Maître d'ouvrage",
       j.organism AS "Maître d'oeuvre",
       k.contractor AS "Prestataires",
       i.financement AS "Financements",
       a.comments AS "Commentaires",
       a.date_insert AS "Date d'insertion",
       a.date_update AS "Date de modification"
FROM maintenance_project a
LEFT JOIN maintenance_projecttype b ON a.type_id = b.id
LEFT JOIN authent_structure c ON a.structure_id = c.id
LEFT JOIN maintenance_projectdomain e ON a.domain_id = e.id
LEFT JOIN common_organism h ON a.project_owner_id = h.id
LEFT JOIN common_organism j ON a.project_manager_id = j.id
LEFT JOIN
    (WITH financements AS
         (SELECT a.id,
                 amount,
                 project_id,
                 organism_id,
                 c.organism,
                 CASE
                     WHEN amount IS NOT NULL THEN concat(amount::numeric(10, 1), '€ de ', c.organism)
                     ELSE NULL
                 END AS financement
          FROM maintenance_funding a
          JOIN maintenance_project b ON a.project_id = b.id
          JOIN common_organism c ON a.organism_id = c.id) SELECT project_id,
                                                                 array_to_string(ARRAY_AGG (financement), ', ', '*') financement
     FROM financements
     GROUP BY project_id) i ON a.id = i.project_id
LEFT JOIN
    (SELECT a.contractor,
            b.contractor_id,
            project_id
     FROM maintenance_contractor a
     JOIN maintenance_project_contractors b ON a.id = b.contractor_id
     JOIN maintenance_project c ON b.project_id = c.id) k ON a.id = k.project_id
WHERE a.deleted IS FALSE 
;
