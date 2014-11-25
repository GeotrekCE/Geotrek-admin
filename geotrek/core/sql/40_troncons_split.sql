-------------------------------------------------------------------------------
-- Split paths when crossing each other
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS l_t_troncon_split_geom_iu_tgr ON l_t_troncon;
DROP TRIGGER IF EXISTS l_t_troncon_10_split_geom_iu_tgr ON l_t_troncon;

CREATE OR REPLACE FUNCTION troncons_evenement_intersect_split() RETURNS trigger AS $$
DECLARE
    troncon l_t_troncon;
    t_count integer;
    tid_clone integer;
    existing_et integer[];
    t_geom geometry;

    fraction float8;
    a float8;
    b float8;
    segment geometry;
    newgeom geometry;

    intersections_on_new float8[];
    intersections_on_current float8[];
BEGIN

    -- Copy original geometry
    newgeom := NEW.geom;
    intersections_on_new := ARRAY[0::float];

    -- Iterate paths intersecting, excluding those touching by extremities
    FOR troncon IN SELECT *
                   FROM l_t_troncon t
                   WHERE id != NEW.id
                         AND ST_Intersects(geom, NEW.geom)
                         AND NOT ST_Relate(geom, NEW.geom, 'FF*F*****')
                         AND GeometryType(ST_Intersection(geom, NEW.geom)) IN ('POINT', 'MULTIPOINT')
    LOOP

        RAISE NOTICE '%-% (%) intersects %-% (%) : %', NEW.id, NEW.nom, ST_AsText(NEW.geom), troncon.id, troncon.nom, ST_AsText(troncon.geom), ST_AsText(ST_Intersection(troncon.geom, NEW.geom));

        -- Locate intersecting point(s) on NEW, for later use
        FOR fraction IN SELECT ST_Line_Locate_Point(NEW.geom, (ST_Dump(ST_Intersection(troncon.geom, NEW.geom))).geom)
        LOOP
            intersections_on_new := array_append(intersections_on_new, fraction);
        END LOOP;
        intersections_on_new := array_append(intersections_on_new, 1::float);

        -- Sort intersection points and remove duplicates (0 and 1 can appear twice)
        SELECT array_agg(sub.fraction) INTO intersections_on_new
            FROM (SELECT DISTINCT unnest(intersections_on_new) AS fraction ORDER BY fraction) AS sub;

        -- Locate intersecting point(s) on current path (array of  : {0, 0.32, 0.89, 1})
        intersections_on_current := ARRAY[0::float];
        FOR fraction IN SELECT ST_Line_Locate_Point(troncon.geom, (ST_Dump(ST_Intersection(troncon.geom, NEW.geom))).geom)
        LOOP
            intersections_on_current := array_append(intersections_on_current, fraction);
        END LOOP;
        intersections_on_current := array_append(intersections_on_current, 1::float);

        -- Sort intersection points and remove duplicates (0 and 1 can appear twice)
        SELECT array_agg(sub.fraction) INTO intersections_on_current
            FROM (SELECT DISTINCT unnest(intersections_on_current) AS fraction ORDER BY fraction) AS sub;

        IF array_length(intersections_on_new, 1) > 2 AND array_length(intersections_on_current, 1) > 2 THEN
            -- If both intersects, one is enough, since split trigger will be applied recursively.
            intersections_on_new := ARRAY[]::float[];
        END IF;

    --------------------------------------------------------------------
    -- 1. Handle NEW intersecting with existing paths
    --------------------------------------------------------------------

        -- Skip if intersections are 0,1 (means not crossing)
        IF array_length(intersections_on_new, 1) > 2 THEN
            RAISE NOTICE 'New: % % intersecting on NEW % % : %', NEW.id, NEW.nom, troncon.id, troncon.nom, intersections_on_new;

            FOR i IN 1..(array_length(intersections_on_new, 1) - 1)
            LOOP
                a := intersections_on_new[i];
                b := intersections_on_new[i+1];

                segment := ST_Line_Substring(newgeom, a, b);

                IF coalesce(ST_Length(segment), 0) < 1 THEN
                     intersections_on_new[i+1] := a;
                     CONTINUE;
                END IF;

                IF i = 1 THEN
                    -- First segment : shrink it !
                    SELECT COUNT(*) INTO t_count FROM l_t_troncon WHERE nom = NEW.nom AND ST_Equals(geom, segment);
                    IF t_count = 0 THEN
                        RAISE NOTICE 'New: Skrink %-% (%) to %', NEW.id, NEW.nom, ST_AsText(NEW.geom), ST_AsText(segment);
                        UPDATE l_t_troncon SET geom = segment WHERE id = NEW.id;
                    END IF;
                ELSE
                    -- Next ones : create clones !
                    PERFORM ft_clone_path(NEW, segment);
                END IF;
            END LOOP;

            -- Recursive triggers did all the work. Stop here.
            RETURN NULL;
        END IF;


    --------------------------------------------------------------------
    -- 2. Handle paths intersecting with NEW
    --------------------------------------------------------------------

        -- Skip if intersections are 0,1 (means not crossing)
        IF array_length(intersections_on_current, 1) > 2 THEN
            RAISE NOTICE 'Current: % % intersecting on current % % : %', NEW.id, NEW.nom, troncon.id, troncon.nom, intersections_on_current;

            SELECT array_agg(id) INTO existing_et FROM e_r_evenement_troncon et WHERE et.troncon = troncon.id;
             IF existing_et IS NOT NULL THEN
                 RAISE NOTICE 'Existing topologies id for %-% (%): %', troncon.id, troncon.nom, ST_AsText(troncon.geom), existing_et;
             END IF;

            FOR i IN 1..(array_length(intersections_on_current, 1) - 1)
            LOOP
                a := intersections_on_current[i];
                b := intersections_on_current[i+1];

                segment := ST_Line_Substring(troncon.geom, a, b);

                IF coalesce(ST_Length(segment), 0) < 1 THEN
                     intersections_on_new[i+1] := a;
                     CONTINUE;
                END IF;

                IF i = 1 THEN
                    -- First segment : shrink it !
                    SELECT geom INTO t_geom FROM l_t_troncon WHERE id = troncon.id;
                    IF NOT ST_Equals(t_geom, segment) THEN
                        RAISE NOTICE 'Current: Skrink %-% (%) to %', troncon.id, troncon.nom, ST_AsText(troncon.geom), ST_AsText(segment);

                        -- Disable e_r_troncon_evenement update while shrinking
                        -- Since there is no way to set global variables in pl/pgsql
                        -- we use a trick using the field ``remarques``
                        UPDATE l_t_troncon SET remarques = remarques || '~' WHERE id = troncon.id;
                        -- Shrink! Snap, compute, drape, ...
                        UPDATE l_t_troncon SET geom = segment WHERE id = troncon.id;
                        -- Restore remarques.
                        UPDATE l_t_troncon SET remarques = trim(leading '~' from remarques) WHERE id = troncon.id;

                    END IF;
                ELSE
                    -- Next ones : create clones !
                    -- (if necessary, recursive triggers)
                    SELECT ft_clone_path(troncon, segment) INTO tid_clone;

                    IF tid_clone > 0 THEN
                        -- Copy topologies overlapping start/end
                        INSERT INTO e_r_evenement_troncon (troncon, evenement, pk_debut, pk_fin, ordre)
                            SELECT
                                tid_clone,
                                et.evenement,
                                CASE WHEN pk_debut <= pk_fin THEN
                                    (greatest(a, pk_debut) - a) / (b - a)
                                ELSE
                                    (least(b, pk_debut) - a) / (b - a)
                                END,
                                CASE WHEN pk_debut <= pk_fin THEN
                                    (least(b, pk_fin) - a) / (b - a)
                                ELSE
                                    (greatest(a, pk_fin) - a) / (b - a)
                                END,
                                et.ordre
                            FROM e_r_evenement_troncon et
                            JOIN e_t_evenement e ON (et.evenement = e.id)
                            WHERE et.troncon = troncon.id
                                  AND ((least(pk_debut, pk_fin) < b AND greatest(pk_debut, pk_fin) > a) OR       -- Overlapping
                                       (pk_debut = pk_fin AND pk_debut = a AND decallage = 0)); -- Point
                        GET DIAGNOSTICS t_count = ROW_COUNT;
                        IF t_count > 0 THEN
                            RAISE NOTICE 'Duplicated % topologies of %-% (%) on [% ; %] for %-% (%)', t_count, troncon.id, troncon.nom, ST_AsText(troncon.geom), a, b, tid_clone, troncon.nom, ST_AsText(segment);
                        END IF;
                        -- Special case : point topology at the end of path
                        IF b = 1 THEN
                            SELECT geom INTO t_geom FROM l_t_troncon WHERE id = troncon.id;
                            fraction := ST_Line_Locate_Point(segment, ST_EndPoint(troncon.geom));
                            INSERT INTO e_r_evenement_troncon (troncon, evenement, pk_debut, pk_fin)
                                SELECT tid_clone, evenement, pk_debut, pk_fin
                                FROM e_r_evenement_troncon et
                                JOIN e_t_evenement e ON (et.evenement = e.id)
                                WHERE et.troncon = troncon.id AND
                                      pk_debut = pk_fin AND
                                      pk_debut = 1 AND
                                      decallage = 0;
                            GET DIAGNOSTICS t_count = ROW_COUNT;
                            IF t_count > 0 THEN
                                RAISE NOTICE 'Duplicated % point topologies of %-% (%) on intersection at the end of %-% (%) at [%]', t_count, troncon.id, troncon.nom, ST_AsText(t_geom), tid_clone, troncon.nom, ST_AsText(segment), fraction;
                            END IF;
                        END IF;
                        -- Special case : point topology exactly where NEW path intersects
                        IF a > 0 THEN
                            fraction := ST_Line_Locate_Point(NEW.geom, ST_Line_Interpolate_Point(troncon.geom, a));
                            INSERT INTO e_r_evenement_troncon (troncon, evenement, pk_debut, pk_fin, ordre)
                                SELECT NEW.id, et.evenement, fraction, fraction, ordre
                                FROM e_r_evenement_troncon et
                                JOIN e_t_evenement e ON (et.evenement = e.id)
                                WHERE et.troncon = troncon.id
                                  AND pk_debut = pk_fin AND pk_debut = a
                                  AND decallage = 0;
                            GET DIAGNOSTICS t_count = ROW_COUNT;
                            IF t_count > 0 THEN
                                RAISE NOTICE 'Duplicated % point topologies of %-% (%) on intersection by %-% (%) at [%]', t_count, troncon.id, troncon.nom, ST_AsText(troncon.geom), NEW.id, NEW.nom, ST_AsText(NEW.geom), a;
                            END IF;
                        END IF;
                    END IF;
                END IF;
            END LOOP;


            -- For each existing point topology with offset, re-attach it
            -- to the closest path, among those splitted.
            PERFORM ft_reattach_point_topologies(troncon, existing_et);

            -- Update point topologies at intersection
            -- Trigger e_r_evenement_troncon_junction_point_iu_tgr
            UPDATE e_r_evenement_troncon et SET pk_debut = pk_debut
             WHERE et.troncon = NEW.id
               AND pk_debut = pk_fin;

            -- Now handle first path topologies
            -- Delete topologies outside its shorter geom
            -- and recompute start/end of overlapping aggregations.
            a := intersections_on_current[1];
            b := intersections_on_current[2];
            PERFORM ft_recompute_start_end_aggregations(troncon, a, b, existing_et);

        END IF;


    END LOOP;

    IF array_length(intersections_on_new, 1) > 0 OR array_length(intersections_on_current, 1) > 0 THEN
        RAISE NOTICE 'Done %-% (%).', NEW.id, NEW.nom, ST_AsText(NEW.geom);
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER l_t_troncon_10_split_geom_iu_tgr
AFTER INSERT OR UPDATE OF geom ON l_t_troncon
FOR EACH ROW EXECUTE PROCEDURE troncons_evenement_intersect_split();


-------------------------------------------------------------------------------
-- Clone path record
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ft_clone_path(troncon l_t_troncon, geom geometry) RETURNS integer AS $$
DECLARE
    tid_clone integer;
    t_count integer;
BEGIN
    SELECT COUNT(*) INTO t_count FROM l_t_troncon t WHERE nom = troncon.nom AND ST_Equals(troncon.geom, t.geom);
    IF t_count > 0 THEN
        RETURN -1;
    END IF;

    RAISE NOTICE 'Create clone of %-% with geom %', troncon.id, troncon.nom, ST_AsText(geom);
    INSERT INTO l_t_troncon (structure,
                             visible,
                             valide,
                             nom,
                             remarques,
                             source,
                             enjeu,
                             geom_cadastre,
                             depart,
                             arrivee,
                             confort,
                             geom)
        VALUES (troncon.structure,
                troncon.visible,
                troncon.valide,
                troncon.nom,
                troncon.remarques,
                troncon.source,
                troncon.enjeu,
                troncon.geom_cadastre,
                troncon.depart,
                troncon.arrivee,
                troncon.confort,
                geom)
        RETURNING id INTO tid_clone;

    -- Copy N-N relations
    INSERT INTO l_r_troncon_reseau (path_id, network_id)
        SELECT tid_clone, tr.network_id
        FROM l_r_troncon_reseau tr
        WHERE tr.path_id = troncon.id;
    INSERT INTO l_r_troncon_usage (path_id, usage_id)
        SELECT tid_clone, tr.usage_id
        FROM l_r_troncon_usage tr
        WHERE tr.path_id = troncon.id;

    RETURN tid_clone;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- Re-attach point topologies to closest paths
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ft_reattach_point_topologies(troncon l_t_troncon, existing_et integer[]) RETURNS void AS $$
DECLARE
    t_count integer;
BEGIN
    -- For each existing point topology with offset, re-attach it
    -- to the closest path, among those splitted.
    WITH existing_rec AS (SELECT et.id, e.decallage, e.geom
                            FROM e_r_evenement_troncon et
                            JOIN e_t_evenement e ON (et.evenement = e.id)
                           WHERE et.pk_debut = et.pk_debut
                             AND e.decallage > 0
                             AND et.troncon = troncon.id
                             AND et.id = ANY(existing_et)),
         closest_path AS (SELECT er.id AS et_id, t.id AS closest_id
                            FROM l_t_troncon t, existing_rec er
                           WHERE t.id != troncon.id
                             AND ST_Distance(er.geom, t.geom) < er.decallage
                        ORDER BY ST_Distance(er.geom, t.geom)
                           LIMIT 1)
        UPDATE e_r_evenement_troncon SET troncon = closest_id
          FROM closest_path
         WHERE id = et_id;
    GET DIAGNOSTICS t_count = ROW_COUNT;
    IF t_count > 0 THEN
        -- Update geom of affected paths to trigger update_evenement_geom_when_troncon_changes()
        UPDATE l_t_troncon t SET geom = geom
          FROM e_r_evenement_troncon et
         WHERE t.id = et.troncon
           AND et.pk_debut = et.pk_debut
           AND et.id = ANY(existing_et);
    END IF;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- When path is shrinked : delete topologies outside the specified path geometry
-- that now belong to clones.
-- And recompute start/end for the overlapping part.
-------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION ft_recompute_start_end_aggregations(troncon l_t_troncon, a float8, b float8, existing_et integer[]) RETURNS void AS $$
DECLARE
    t_count integer;
BEGIN
    DELETE FROM e_r_evenement_troncon et WHERE et.troncon = troncon.id
                                         AND id = ANY(existing_et)
                                         AND (least(pk_debut, pk_fin) > b OR greatest(pk_debut, pk_fin) < a);
    GET DIAGNOSTICS t_count = ROW_COUNT;
    IF t_count > 0 THEN
        RAISE NOTICE 'Removed % topologies of %-% on [% ; %]', t_count, troncon.id,  troncon.nom, a, b;
    END IF;

    -- Update topologies overlapping
    UPDATE e_r_evenement_troncon et SET
        pk_debut = CASE WHEN pk_debut / (b - a) > 1 THEN 1 ELSE pk_debut / (b - a) END,
        pk_fin = CASE WHEN pk_fin / (b - a) > 1 THEN 1 ELSE pk_fin / (b - a) END
        WHERE et.troncon = troncon.id
        AND least(pk_debut, pk_fin) <= b AND greatest(pk_debut, pk_fin) >= a;
    GET DIAGNOSTICS t_count = ROW_COUNT;
    IF t_count > 0 THEN
        RAISE NOTICE 'Updated % topologies of %-% on [% ; %]', t_count, troncon.id,  troncon.nom, a, b;
    END IF;
END;
$$ LANGUAGE plpgsql;
