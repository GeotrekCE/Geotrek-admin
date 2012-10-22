-------------------------------------------------------------------------------
-- Split paths when crossing each other
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS troncons_split_geom_iu_tgr ON troncons;

CREATE OR REPLACE FUNCTION troncons_evenement_intersect_split() RETURNS trigger AS $$
DECLARE
    troncon record;
    tid integer;
    tid_clone integer;
    
    pk float;  -- "P"oint "K"ilometrique
    a float;
    b float;
    segment geometry;
    
    intersections_on_new float[] := ARRAY[0::float];
    intersections_on_current float[];
BEGIN

    -- 1. Handle paths intersecting with NEW (will handle NEW later)
    
    -- Iterate paths intersecting, excluding those touching by extremities
    FOR tid IN SELECT t.id
               FROM troncons t
               WHERE id != NEW.id 
                     AND ST_Intersects(geom, NEW.geom) 
                     AND NOT ST_Relate(geom, NEW.geom, 'FF*F*****')
    LOOP
        SELECT * FROM troncons WHERE id = tid INTO troncon;
        
        -- Locate intersecting point(s) on NEW, for later use
        FOR pk IN SELECT ST_Line_Locate_Point(NEW.geom, (ST_Dump(ST_Intersection(troncon.geom, NEW.geom))).geom)
        LOOP
            intersections_on_new := array_append(intersections_on_new, pk);
        END LOOP;
        RAISE NOTICE '% intersecting on NEW % : %', tid, NEW.id, intersections_on_new;
        
         -- Locate intersecting point(s) on current path (array of  : {0, 0.32, 0.89, 1})
        intersections_on_current := ARRAY[0::float];
        FOR pk IN SELECT ST_Line_Locate_Point(troncon.geom, (ST_Dump(ST_Intersection(troncon.geom, NEW.geom))).geom)
        LOOP
            intersections_on_current := array_append(intersections_on_current, pk);
        END LOOP;
        intersections_on_current := array_append(intersections_on_current, 1::float);
         -- Sort intersection points and remove duplicates (0 and 1 can appear twice)
        SELECT array_agg(sub.pk) INTO intersections_on_current
        FROM (SELECT unnest(intersections_on_current) AS pk ORDER BY pk) AS sub;
        RAISE NOTICE '% intersecting on current % : %', tid, tid, intersections_on_current;
        
        -- Skip if intersections are 0,1 (means not crossing)
        IF array_length(intersections_on_current, 1) > 2 THEN
            FOR i IN 1..(array_length(intersections_on_current, 1) - 1)
            LOOP
                a := intersections_on_current[i];
                b := intersections_on_current[i+1];

                segment := ST_Line_Substring(troncon.geom, a, b);

                IF i = 1 THEN
                    -- First segment : shrink it !
                    UPDATE troncons SET geom = segment WHERE id = troncon.id;
                ELSE
                    -- Next ones : create clones !
                    INSERT INTO troncons (structure_id, 
                                          troncon_valide,
                                          nom_troncon, 
                                          remarques,
                                          trail_id,
                                          datasource_id,
                                          stake_id,
                                          geom_cadastre,
                                          depart,
                                          arrivee,
                                          comfort_id,
                                          geom) 
                        VALUES (troncon.structure_id,
                                troncon.troncon_valide,
                                troncon.nom_troncon,
                                troncon.remarques,
                                troncon.trail_id,
                                troncon.datasource_id,
                                troncon.stake_id,
                                troncon.geom_cadastre,
                                troncon.depart,
                                troncon.arrivee,
                                troncon.comfort_id,
                                segment)
                        RETURNING id INTO tid_clone;
                END IF;
            END LOOP;
        END IF;

    END LOOP;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER troncons_split_geom_iu_tgr
AFTER INSERT OR UPDATE OF geom ON troncons
FOR EACH ROW EXECUTE PROCEDURE troncons_evenement_intersect_split();
/*
CREATE OR REPLACE FUNCTION T_xxxx() RETURNS Trigger AS $$
DECLARE
    intersections_on_new float[] := ARRAY[0::float];
    intersections_on_current float[];
    segment geometry;
    t_id integer;
    pk float;
    a float;
    b float;
BEGIN
    -- 1. Traiter d'abord les troncons en intersection avec NEW (on traitera NEW dans un second temps)

    -- Tous les troncons en intersection avec NEW sauf ceux qui se touchent seulement par leurs extrêmités
    pour chaque troncon t dans SELECT * FROM troncons WHERE id != NEW.id AND ST_Intersects(geom, NEW.geom) AND NOT ST_Relate(geom, NEW.geom, 'FF*F*****')
    faire
        -- Localiser le(s) point(s) de cassure sur NEW pour les traiter plus tard
        pour chaque pk dans SELECT ST_Line_Locate_Point(NEW.geom, (ST_Dump(ST_Intersection(t.geom, NEW.geom))).geom)
        faire
            intersections_on_new := array_append(intersections_on_new, pk);
        fin pour;

        -- Localiser le(s) point(s) de cassure sur t (résultat sous forme d'un tableau de PK : {0, 0.32, 0.89, 1})
        intersections_on_current := ARRAY[0::float];
        pour chaque pk dans SELECT ST_Line_Locate_Point(t.geom, (ST_Dump(ST_Intersection(t.geom, NEW.geom))).geom)
        faire
            intersections_on_current := array_append(intersections_on_current, pk);
        fin pour;
        intersections_on_current := array_append(intersections_on_current, 1::float);

        -- Ordonner les points de cassures et éliminer les doublons (0 et 1 peuvent apparaître 2 fois)
        SELECT array_agg(pk) INTO intersections_on_current FROM (SELECT DISTINCT pk FROM unnest(intersections_on_current) AS (pk float) ORDER BY pk) AS sub;

        -- Inutile de traiter le cas particulier {0,1}...
        si array_length(intersections_on_current, 1) > 2 alors

            -- Découper le troncon t
            pour i allant de 1 à intersections_on_current[array_length(intersections_on_current, 1) - 1   -- du 1er élément à l'avant-dernier
            faire
                a := intersections_on_current[i];
                b := intersections_on_current[i+1]
                segment := ST_LineSubstring(t.geom, a, b);

                si i == 1 alors
                    -- Cas particulier du 1er segment
                    UPDATE troncons SET geom = segment WHERE id = t.id;
                    -- On a besoin des événements intacts pour les itérations suivantes, on les gérera donc après la boucle dans le cas du 1er segment

                sinon
                    -- Créer un troncon pour chaque segment après le 1er
                    INSERT INTO troncons (<toutes les cols sauf id>) VALUES (<t.* sauf t.id et remplacer t.geom par segment>) RETURNING id INTO t_id;

                    -- Copie les événements qui sont dans la bonne plage de PK
                    INSERT INTO evenements_troncons (troncon, evenement, pk_debut, pk_fin)
                        SELECT
                            t_id,
                            evenement,
                            (greatest(a, pk_debut) - pk_debut) / (b - a),
                            (least(b, pk_fin) - pk_debut) / (b - a)
                        FROM evenements_troncons WHERE troncon = t.id AND ((pk_debut < b AND pk_fin > a) OR (pk_debut = pk_fin AND pk_debut = a));

                    -- Cas particulier : les événements ponctuels sur le point final du troncon original échappent à la condition ci-dessus
                    si b = 1 alors
                        INSERT INTO evenements_troncons (troncon, evenement, pk_debut, pk_fin)
                            SELECT t_id, evenement, 1, 1
                            FROM evenements_troncons WHERE troncon = t.id AND pk_debut = pk_fin AND pk_debut = 1;
                    fin si;
                fin si;
            fin pour;

            -- Gestion déportée des événements du 1er segment
            a := intersections_on_current[1];
            b := intersections_on_current[2];
            -- recadrer les événements du troncon original qui concerne le 1er segment
            UPDATE evenements_troncons
                SET
                    pk_debut = pk_debut / b,
                    pk_fin = least(b, pk_fin) / b
                WHERE troncon = t.id AND pk_debut < b;
            -- supprimer ceux qui sont hors du 1er segment (ils ont été re-créés plus haut)
            DELETE FROM evenements_troncons WHERE troncon = t.id AND pk_debut >= b;
        fin si;
    fin pour;

    -- 2. Traiter le troncon NEW

    -- Mêmes étapes que ci-dessus mais en travaillant avec NEW.geom et intersections_on_new :
    -- * ordonner et dé-doublonner les points de cassures
    -- * les parcourir 2 à 2 pour identifier les segments
    -- * enregistrer les segments avec UPDATE pour le premier et INSERT pour les suivants
    -- * si TG_OP = 'UPDATE' alors mettre à jour les événements

    -- Note : il y a probablement moyen de factoriser le code des étapes 1 & 2.
    -- Peut-être avec une fonction intermédiaire ? Ou peut-être en intégrant
    -- NEW à la boucle de l'étape 1 (je suis sceptique sur la faisabilité) ?

    RETURN NULL;
END;
$$ LANGUAGE plpgsql ;

CREATE TRIGGER t_xxxx
    AFTER INSERT OR UPDATE OF geom ON troncons
    FOR EACH ROW EXECUTE f_xxxx() ;
*/
