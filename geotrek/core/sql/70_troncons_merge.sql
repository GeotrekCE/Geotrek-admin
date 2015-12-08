CREATE OR REPLACE FUNCTION geotrek.ft_merge_path(updated integer, merged integer)
  RETURNS boolean AS $$

DECLARE
    element RECORD;
    rebuild_line geometry;
    updated_geom geometry;
    merged_geom geometry;
    reverse_update boolean;
    reverse_merged boolean;
    max_snap_distance float;
    
BEGIN
    reverse_update := FALSE;
    reverse_merged := FALSE;
    max_snap_distance := {{PATH_MERGE_SNAPPING_DISTANCE}};
    rebuild_line := NULL;

    IF updated = merged
    THEN
        -- can't merged a path itself !
        return FALSE;
	
    END IF;
    
    updated_geom := (SELECT geom FROM l_t_troncon WHERE id = updated);
    merged_geom := (SELECT geom FROM l_t_troncon WHERE id = merged);

    -- DETECT matching point to rebuild path line
    IF ST_EQUALS(ST_STARTPOINT(updated_geom), ST_STARTPOINT(merged_geom))
    THEN
	rebuild_line := ST_MAKELINE(ST_REVERSE(updated_geom), merged_geom);
	reverse_update := TRUE;
	
    ELSIF ST_EQUALS(ST_STARTPOINT(updated_geom), ST_ENDPOINT(merged_geom))
    THEN
	rebuild_line := ST_MAKELINE(ST_REVERSE(updated_geom), ST_REVERSE(merged_geom));
	reverse_update := TRUE;
	reverse_merged := TRUE;
	
    ELSIF ST_EQUALS(ST_ENDPOINT(updated_geom), ST_ENDPOINT(merged_geom))
    THEN
	rebuild_line := ST_MAKELINE(updated_geom, ST_REVERSE(merged_geom));
	reverse_merged := TRUE;

    ELSIF ST_EQUALS(ST_ENDPOINT(updated_geom), ST_STARTPOINT(merged_geom))
    THEN
	rebuild_line := ST_MAKELINE(updated_geom, merged_geom);

    ELSIF (ST_DISTANCE(ST_STARTPOINT(updated_geom), ST_STARTPOINT(merged_geom))::float <= max_snap_distance)
    THEN 
	rebuild_line := ST_MAKELINE(ST_REVERSE(updated_geom), merged_geom);
	reverse_update := TRUE;
	
    ELSIF (ST_DISTANCE(ST_STARTPOINT(updated_geom), ST_ENDPOINT(merged_geom)) <= max_snap_distance)
    THEN
	rebuild_line := ST_MAKELINE(ST_REVERSE(updated_geom), ST_REVERSE(merged_geom));
	reverse_update := TRUE;
	reverse_merged := TRUE;
	
    ELSIF (ST_DISTANCE(ST_ENDPOINT(updated_geom), ST_ENDPOINT(merged_geom)) <= max_snap_distance)
    THEN
	rebuild_line := ST_MAKELINE(updated_geom, ST_REVERSE(merged_geom));
	reverse_merged := TRUE;

    ELSIF (ST_DISTANCE(ST_ENDPOINT(updated_geom), ST_STARTPOINT(merged_geom)) <= max_snap_distance)
    THEN
	rebuild_line := ST_MAKELINE(updated_geom, merged_geom);
    
    ELSE
    -- no snapping -> END !
        RETURN FALSE;

    END IF;

    -- update events on updated path
    FOR element IN
        SELECT * FROM e_r_evenement_troncon et
                 JOIN e_t_evenement as evt ON et.evenement=evt.id
                 JOIN l_t_troncon as tr on et.troncon = tr.id
        WHERE et.troncon = updated
    LOOP
        IF reverse_update = TRUE
	THEN
	    -- update reverse pk
	    UPDATE e_r_evenement_troncon
		   SET pk_debut = (1- pk_debut) * ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom)),
		       pk_fin = (1- pk_fin) * ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom))
		   WHERE id = element.id;
	    -- update reverse offset
            UPDATE e_t_evenement
                   SET decallage = -decallage
                   WHERE id = element.evenement;
	ELSE
	    UPDATE e_r_evenement_troncon
		   SET pk_debut = pk_debut * ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom)),
		       pk_fin = pk_fin * ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom))
		   WHERE id = element.id;
	END IF;
    END LOOP;
    
    -- update events on merged path
    FOR element IN
        SELECT * FROM e_r_evenement_troncon et
                 JOIN e_t_evenement as evt ON et.evenement=evt.id
                 JOIN l_t_troncon as tr on et.troncon = tr.id
        WHERE et.troncon = merged
    LOOP
        IF reverse_merged = TRUE
        THEN
	    UPDATE e_r_evenement_troncon
		   SET pk_debut = ((1- pk_debut) * ST_LENGTH(merged_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom))) + (ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom))),
		       pk_fin = ((1- pk_fin) * ST_LENGTH(merged_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom))) + (ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom)))
		   WHERE id = element.id;

            UPDATE e_t_evenement
                   SET decallage = -decallage
                   WHERE id = element.evenement;
        ELSE
	    UPDATE e_r_evenement_troncon
		   SET pk_debut = (pk_debut * ST_LENGTH(merged_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom))) + (ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom))),
		       pk_fin = (pk_fin * ST_LENGTH(merged_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom))) + (ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(merged_geom)))
		   WHERE id = element.id;
        END IF;
    END LOOP;
	
    -- fix new geom to updated
    UPDATE l_t_troncon
           SET geom = rebuild_line
           WHERE id = updated;
   
    -- Link merged events to updated
    UPDATE e_r_evenement_troncon
           SET troncon = updated
           WHERE troncon = merged;

    -- link element or delete if target unique already present
    FOR element IN SELECT * FROM l_r_troncon_reseau WHERE path_id = merged
    LOOP
        IF NOT EXISTS (SELECT 1 FROM l_r_troncon_reseau WHERE network_id=element.network_id AND path_id = updated) THEN
	    UPDATE l_r_troncon_reseau
		   SET path_id = updated
		   WHERE id = element.id;
        ELSE
            DELETE FROM l_r_troncon_reseau WHERE path_id = merged;
        END IF;
    END LOOP;

    -- link element or delete if target unique already present
    FOR element IN SELECT * FROM l_r_troncon_usage WHERE path_id = merged
    LOOP
        IF NOT EXISTS (SELECT 1 FROM l_r_troncon_usage WHERE usage_id=element.usage_id AND path_id = updated) THEN
	    UPDATE l_r_troncon_usage
		   SET path_id = updated
		   WHERE id = element.id;
        ELSE
            DELETE FROM l_r_troncon_usage WHERE path_id = merged;
        END IF;
    END LOOP;
		   
    
    -- Delete merged Path
    DELETE FROM l_t_troncon WHERE id = merged;

    RETURN TRUE;

END;
$$ LANGUAGE plpgsql;
