CREATE OR REPLACE FUNCTION geotrek.ft_path_unify(updated integer, unified integer)
  RETURNS boolean AS $$

DECLARE
    element RECORD;
    rebuild_line geometry;
    updated_geom geometry;
    unified_geom geometry;
    reverse_update boolean;
    reverse_unified boolean;
    
BEGIN
    reverse_update := FALSE;
    reverse_unified := FALSE;

    IF updated = unified
    THEN
        -- can't unified a path itself !
        return FALSE;
	
    END IF;
    
    updated_geom := (SELECT geom FROM l_t_troncon WHERE id = updated);
    unified_geom := (SELECT geom FROM l_t_troncon WHERE id = unified);

    -- DETECT matching point to rebuild path line
    IF ST_EQUALS(ST_STARTPOINT(updated_geom), ST_STARTPOINT(unified_geom))
    THEN
	rebuild_line = ST_MAKELINE(ST_REVERSE(updated_geom), unified_geom);
	reverse_update := TRUE;
	
    ELSIF ST_EQUALS(ST_STARTPOINT(updated_geom), ST_ENDPOINT(unified_geom))
    THEN
	rebuild_line = ST_MAKELINE(ST_REVERSE(updated_geom), ST_REVERSE(unified_geom));
	reverse_update := TRUE;
	
    ELSIF ST_EQUALS(ST_ENDPOINT(updated_geom), ST_ENDPOINT(unified_geom))
    THEN
	rebuild_line = ST_MAKELINE(updated_geom, ST_REVERSE(unified_geom));
	reverse_unified := TRUE;

    ELSIF ST_EQUALS(ST_ENDPOINT(updated_geom), ST_STARTPOINT(unified_geom))
    THEN
	rebuild_line = ST_MAKELINE(updated_geom, unified_geom);

    ELSE
	-- no matching -> try snapping
	RETURN FALSE;
	
    END IF;

    -- update events on updated path
    FOR element IN
        SELECT * FROM e_r_evenement_troncon et JOIN e_t_evenement as evt ON et.evenement=evt.id JOIN l_t_troncon as tr on et.troncon = tr.id WHERE et.troncon = updated
    LOOP
	    IF reverse_update = TRUE
	    THEN
		    UPDATE e_r_evenement_troncon
			   SET pk_debut = (1- pk_debut) * ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom)),
			       pk_fin = (1- pk_fin) * ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom))
			   WHERE id = element.id;
	    ELSE
		    UPDATE e_r_evenement_troncon
			   SET pk_debut = pk_debut * ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom)),
			       pk_fin = pk_fin * ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom))
			   WHERE id = element.id;
	    END IF;
    END LOOP;
    
    -- update events on updated path
    FOR element IN
        SELECT * FROM e_r_evenement_troncon et JOIN e_t_evenement as evt ON et.evenement=evt.id JOIN l_t_troncon as tr on et.troncon = tr.id WHERE et.troncon = unified
    LOOP
	    IF reverse_unified = TRUE
	    THEN
		    UPDATE e_r_evenement_troncon
			   SET pk_debut = ((1- pk_debut) * ST_LENGTH(unified_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom))) + (ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom))),
			       pk_fin = ((1- pk_fin) * ST_LENGTH(unified_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom))) + (ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom)))
			   WHERE id = element.id;
	    ELSE
		    UPDATE e_r_evenement_troncon
			   SET pk_debut = (pk_debut * ST_LENGTH(unified_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom))) + (ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom))),
			       pk_fin = (pk_fin * ST_LENGTH(unified_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom))) + (ST_LENGTH(updated_geom) / (ST_LENGTH(updated_geom) + ST_LENGTH(unified_geom)))
			   WHERE id = element.id;
	    END IF;
    END LOOP;
    -- fix new geom to updated
    UPDATE l_t_troncon
           SET geom = rebuild_line
           WHERE id = updated;
           
    -- Link unified events to updated
    UPDATE e_r_evenement_troncon
           SET troncon = updated
           WHERE troncon = unified;
    
    -- Delete unified Path
    DELETE FROM l_t_troncon WHERE id = unified;

    RETURN TRUE;
    
END;
$$ LANGUAGE plpgsql;
