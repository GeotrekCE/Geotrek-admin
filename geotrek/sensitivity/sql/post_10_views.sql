-- Zones sensibles

CREATE VIEW {# geotrek.sensitivity #}.v_sensitivearea_qgis AS
SELECT a.id,
       d.name AS "Structure liée",
       f.zoning_city AS "Commune",
       g.zoning_district AS "Zone",
       b.name AS "Nom",
       CASE
           WHEN h.category = 2 THEN 'Règlementaire'
           WHEN h.category = 1 THEN 'Espèce'
       END AS "Catégorie",
       CONCAT(CASE
                  WHEN h.period01 IS TRUE THEN CONCAT('Janvier', ', ')
                  ELSE NULL
              END, CASE
                       WHEN h.period02 IS TRUE THEN CONCAT('Février', ', ')
                       ELSE NULL
                   END, CASE
                            WHEN h.period03 IS TRUE THEN CONCAT('Mars', ', ')
                            ELSE NULL
                        END, CASE
                                 WHEN h.period04 IS TRUE THEN CONCAT('Avril', ', ')
                                 ELSE NULL
                             END, CASE
                                      WHEN h.period05 IS TRUE THEN CONCAT('Mai', ', ')
                                      ELSE NULL
                                  END, CASE
                                           WHEN h.period06 IS TRUE THEN CONCAT('Juin', ', ')
                                           ELSE NULL
                                       END, CASE
                                                WHEN h.period07 IS TRUE THEN CONCAT('Juillet', ', ')
                                                ELSE NULL
                                            END, CASE
                                                     WHEN h.period08 IS TRUE THEN CONCAT('Août', ', ')
                                                     ELSE NULL
                                                 END, CASE
                                                          WHEN h.period09 IS TRUE THEN CONCAT('Septembre', ', ')
                                                          ELSE NULL
                                                      END, CASE
                                                               WHEN h.period10 IS TRUE THEN CONCAT('Octobre', ', ')
                                                               ELSE NULL
                                                           END, CASE
                                                                    WHEN h.period11 IS TRUE THEN CONCAT('Novembre', ', ')
                                                                    ELSE NULL
                                                                END, CASE
                                                                         WHEN h.period12 IS TRUE THEN 'Décembre'
                                                                     END) AS "Période",
       c.pratiques_sportives AS "Pratiques sportives",
       b.url_fr AS "URL",
       a.description AS "Description",
       a.contact AS "Contact",
       CASE
           WHEN a.published IS FALSE THEN 'Non'
           WHEN a.published IS TRUE THEN 'Oui'
       END AS "Publié",
       a.date_insert AS "Date d'insertion",
       a.date_update AS "Date de modification",
       a.publication_date AS "Date de publication",
       a.geom
FROM sensitivity_sensitivearea a
LEFT JOIN sensitivity_species b ON a.species_id = b.id
LEFT JOIN
    (SELECT species_id,
            array_to_string(ARRAY_AGG (b.name), ', ', '*') pratiques_sportives,
            c.name AS "Nom"
     FROM sensitivity_species_practices a
     JOIN sensitivity_sportpractice b ON a.sportpractice_id = b.id
     JOIN sensitivity_species c ON a.species_id = c.id
     GROUP BY species_id,
              c.name) c ON a.species_id = c.species_id
LEFT JOIN sensitivity_species h ON a.species_id = h.id
LEFT JOIN authent_structure d ON a.structure_id = d.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_city,
            a.id
     FROM sensitivity_sensitivearea a
     JOIN zoning_city b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) f ON a.id = f.id
LEFT JOIN
    (SELECT array_to_string(ARRAY_AGG (b.name), ', ', '*') zoning_district,
            a.id
     FROM sensitivity_sensitivearea a
     JOIN zoning_district b ON ST_INTERSECTS (st_pointonsurface(a.geom), b.geom)
     GROUP BY a.id) g ON a.id = g.id
WHERE deleted IS FALSE 
;

