-------------------------------------------------------------------------------
-- Split paths when crossing each other
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS l_t_troncon_split_geom_iu_tgr ON l_t_troncon;
DROP TRIGGER IF EXISTS l_t_troncon_00_split_geom_iu_tgr ON l_t_troncon;

CREATE OR REPLACE FUNCTION troncons_evenement_intersect_split() RETURNS trigger AS $$
DECLARE
    troncon record;
    tid_clone integer;
    t_count integer;
    existing_et integer[];
    t_geom geometry;

    fraction float;
    a float;
    b float;
    segment geometry;
    newgeom geometry;
    
    intersections_on_new float[];
    intersections_on_current float[];
BEGIN

    -- Copy original geometry
    newgeom := NEW.geom;

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
        intersections_on_new := ARRAY[0::float];
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

                IF i = 1 THEN
                    -- First segment : shrink it !
                    -- RAISE NOTICE 'New: Skrink % : geom is %', NEW.id, ST_AsEWKT(segment);
                    UPDATE l_t_troncon SET geom = segment WHERE id = NEW.id;
                ELSE
                    -- RAISE NOTICE 'New: Create geom is %', ST_AsEWKT(segment);
                    -- Next ones : create clones !
                    INSERT INTO l_t_troncon (structure, 
                                          valide,
                                          nom, 
                                          remarques,
                                          sentier,
                                          source,
                                          enjeu,
                                          geom_cadastre,
                                          depart,
                                          arrivee,
                                          confort,
                                          geom) 
                        VALUES (NEW.structure,
                                NEW.valide,
                                NEW.nom,
                                NEW.remarques,
                                NEW.sentier,
                                NEW.source,
                                NEW.enjeu,
                                NEW.geom_cadastre,
                                NEW.depart,
                                NEW.arrivee,
                                NEW.confort,
                                segment)
                        RETURNING id INTO tid_clone;
                END IF;
            END LOOP;
        END IF;


    --------------------------------------------------------------------
    -- 2. Handle paths intersecting with NEW
    --------------------------------------------------------------------

        -- Skip if intersections are 0,1 (means not crossing)
        IF array_length(intersections_on_current, 1) > 2 THEN
            RAISE NOTICE 'Current: % % intersecting on current % % : %', NEW.id, NEW.nom, troncon.id, troncon.nom, intersections_on_current;

            SELECT array_agg(id) INTO existing_et FROM e_r_evenement_troncon et WHERE et.troncon = troncon.id;
            RAISE NOTICE 'Existing: %', existing_et;

            FOR i IN 1..(array_length(intersections_on_current, 1) - 1)
            LOOP
                a := intersections_on_current[i];
                b := intersections_on_current[i+1];

                segment := ST_Line_Substring(troncon.geom, a, b);

                IF i = 1 THEN
                    -- First segment : shrink it !
                    RAISE NOTICE 'Current: Skrink %-% (%) to %', troncon.id, troncon.nom, ST_AsText(troncon.geom), ST_AsText(segment);
                    UPDATE l_t_troncon SET geom = segment WHERE id = troncon.id;
                ELSE
                    -- Next ones : create clones !
                    RAISE NOTICE 'Current: Create clone of %-% (%) with geom %', troncon.id, troncon.nom, ST_AsText(troncon.geom), ST_AsText(segment);
                    INSERT INTO l_t_troncon (structure, 
                                          valide,
                                          nom, 
                                          remarques,
                                          sentier,
                                          source,
                                          enjeu,
                                          geom_cadastre,
                                          depart,
                                          arrivee,
                                          confort,
                                          geom) 
                        VALUES (troncon.structure,
                                troncon.valide,
                                troncon.nom,
                                troncon.remarques,
                                troncon.sentier,
                                troncon.source,
                                troncon.enjeu,
                                troncon.geom_cadastre,
                                troncon.depart,
                                troncon.arrivee,
                                troncon.confort,
                                segment)
                        RETURNING id INTO tid_clone;
                    
                    -- Copy topologies matching start/end
                    INSERT INTO e_r_evenement_troncon (troncon, evenement, pk_debut, pk_fin)
                        SELECT
                            tid_clone,
                            et.evenement,
                            (greatest(a, pk_debut) - a) / (b - a),
                            (least(b, pk_fin) - a) / (b - a)
                        FROM e_r_evenement_troncon et
                        WHERE et.troncon = troncon.id 
                              AND ((pk_debut < b AND pk_fin > a) OR       -- Overlapping
                                   (pk_debut = pk_fin AND pk_debut = a)); -- Point
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
                            WHERE et.troncon = troncon.id AND 
                                  pk_debut = pk_fin AND 
                                  pk_debut = 1;
                        GET DIAGNOSTICS t_count = ROW_COUNT;
                        IF t_count > 0 THEN
                            RAISE NOTICE 'Duplicated % point topologies of %-% (%) on intersection at the end of %-% (%) at [%]', t_count, troncon.id, troncon.nom, ST_AsText(t_geom), tid_clone, troncon.nom, ST_AsText(segment), fraction;
                        END IF;
                    END IF;
                    -- Special case : point topology exactly where NEW path intersects
                    IF a > 0 THEN
                        fraction := ST_Line_Locate_Point(NEW.geom, ST_Line_Substring(troncon.geom, a, a));
                        INSERT INTO e_r_evenement_troncon (troncon, evenement, pk_debut, pk_fin)
                            SELECT NEW.id, et.evenement, fraction, fraction
                            FROM e_r_evenement_troncon et
                            WHERE et.troncon = troncon.id 
                              AND pk_debut = pk_fin AND pk_debut = a;
                        GET DIAGNOSTICS t_count = ROW_COUNT;
                        IF t_count > 0 THEN
                            RAISE NOTICE 'Duplicated % point topologies of %-% (%) on intersection by %-% (%) at [%]', t_count, troncon.id, troncon.nom, ST_AsText(troncon.geom), NEW.id, NEW.nom, ST_AsText(NEW.geom), a;
                        END IF;
                    END IF;
                END IF;
            END LOOP;
            
            -- Now handle first path topologies
            a := intersections_on_current[1];
            b := intersections_on_current[2];
            DELETE FROM e_r_evenement_troncon et WHERE et.troncon = troncon.id
                                                 AND id = ANY(existing_et)
                                                 AND (pk_debut > b OR pk_fin < a);
            GET DIAGNOSTICS t_count = ROW_COUNT;
            IF t_count > 0 THEN
                RAISE NOTICE 'Removed % topologies of %-% on [% ; %]', t_count, troncon.id,  troncon.nom, a, b;
            END IF;

            -- Update topologies overlapping
            UPDATE e_r_evenement_troncon et SET pk_debut = pk_debut / (b - a),
                                                pk_fin = CASE WHEN pk_fin / (b - a) > 1 THEN 1 ELSE pk_fin / (b - a) END
                WHERE et.troncon = troncon.id
                AND pk_debut <= b AND pk_fin >= a; 
            GET DIAGNOSTICS t_count = ROW_COUNT;
            IF t_count > 0 THEN
                RAISE NOTICE 'Updated % topologies of %-% on [% ; %]', t_count, troncon.id,  troncon.nom, a, b;
            END IF;
        END IF;

    END LOOP;

    IF array_length(intersections_on_new, 1) > 0 OR array_length(intersections_on_current, 1) > 0 THEN
        RAISE NOTICE 'Done %-% (%).', NEW.id, NEW.nom, ST_AsText(NEW.geom);
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER l_t_troncon_00_split_geom_iu_tgr
AFTER INSERT OR UPDATE OF geom ON l_t_troncon
FOR EACH ROW EXECUTE PROCEDURE troncons_evenement_intersect_split();
