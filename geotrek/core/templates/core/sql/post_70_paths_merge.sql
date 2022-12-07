CREATE FUNCTION {{ schema_geotrek }}.ft_merge_path(updated integer, merged integer)
  RETURNS integer AS $$

DECLARE
    element RECORD;
    rebuild_line geometry;
    updated_geom geometry;
    merged_geom geometry;
    reverse_update boolean;
    reverse_merged boolean;
    point_snapping geometry;
    max_snap_distance float;
    snap_distance float;
    count_snapping integer;
    
BEGIN
    reverse_update := FALSE;
    reverse_merged := FALSE;
    max_snap_distance := {{ PATH_MERGE_SNAPPING_DISTANCE }};
    snap_distance := {{ PATH_SNAPPING_DISTANCE }};
    rebuild_line := NULL;

    IF updated = merged
    THEN
        -- can't merged a path itself !
        RETURN 0;
	
    END IF;
    
    updated_geom := (SELECT geom FROM core_path WHERE id = updated);
    merged_geom := (SELECT geom FROM core_path WHERE id = merged);

    -- DETECT matching point to rebuild path line
    IF ST_Equals(ST_StartPoint(updated_geom), ST_StartPoint(merged_geom))
    THEN
	rebuild_line := ST_MakeLine(ST_Reverse(updated_geom), merged_geom);
	reverse_update := TRUE;
	point_snapping := ST_StartPoint(updated_geom);
    ELSIF ST_Equals(ST_StartPoint(updated_geom), ST_EndPoint(merged_geom))
    THEN
	rebuild_line := ST_MakeLine(ST_Reverse(updated_geom), ST_Reverse(merged_geom));
	reverse_update := TRUE;
	reverse_merged := TRUE;
	point_snapping := ST_StartPoint(updated_geom);
	
    ELSIF ST_Equals(ST_EndPoint(updated_geom), ST_EndPoint(merged_geom))
    THEN
	rebuild_line := ST_MakeLine(updated_geom, ST_Reverse(merged_geom));
	reverse_merged := TRUE;
	point_snapping := ST_EndPoint(updated_geom);

    ELSIF ST_Equals(ST_EndPoint(updated_geom), ST_StartPoint(merged_geom))
    THEN
	rebuild_line := ST_MakeLine(updated_geom, merged_geom);
	point_snapping := ST_EndPoint(updated_geom);

    ELSIF (ST_Distance(ST_StartPoint(updated_geom), ST_StartPoint(merged_geom))::float <= max_snap_distance)
    THEN 
	rebuild_line := ST_MakeLine(ST_Reverse(updated_geom), merged_geom);
	reverse_update := TRUE;
	point_snapping := ST_StartPoint(updated_geom);
	
    ELSIF (ST_Distance(ST_StartPoint(updated_geom), ST_EndPoint(merged_geom)) <= max_snap_distance)
    THEN
	rebuild_line := ST_MakeLine(ST_Reverse(updated_geom), ST_Reverse(merged_geom));
	reverse_update := TRUE;
	reverse_merged := TRUE;
	point_snapping := ST_StartPoint(updated_geom);
	
    ELSIF (ST_Distance(ST_EndPoint(updated_geom), ST_EndPoint(merged_geom)) <= max_snap_distance)
    THEN
	rebuild_line := ST_MakeLine(updated_geom, ST_Reverse(merged_geom));
	reverse_merged := TRUE;
	point_snapping := ST_EndPoint(updated_geom);

    ELSIF (ST_Distance(ST_EndPoint(updated_geom), ST_StartPoint(merged_geom)) <= max_snap_distance)
    THEN
	rebuild_line := ST_MakeLine(updated_geom, merged_geom);
	point_snapping := ST_EndPoint(updated_geom);
    
    ELSE
    -- no snapping -> END !
        RETURN 0;

    END IF;

    SELECT COUNT(*) INTO count_snapping FROM core_path WHERE (ST_DWITHIN(ST_StartPoint(geom), point_snapping, snap_distance) OR ST_DWITHIN(ST_EndPoint(geom), point_snapping, snap_distance)) AND draft = FALSE AND id != updated AND id != merged;

    IF count_snapping != 0 THEN
        RETURN 2;
    END IF;

    -- update events on updated path
    FOR element IN
        SELECT * FROM core_pathaggregation et
                 JOIN core_topology as evt ON et.topo_object_id=evt.id
                 JOIN core_path as tr on et.path_id = tr.id
        WHERE et.path_id = updated
    LOOP
        IF reverse_update = TRUE
	THEN
	    -- update reverse pk
	    UPDATE core_pathaggregation
		   SET start_position = (1- start_position) * ST_Length(updated_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom)),
		       end_position = (1- end_position) * ST_Length(updated_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom))
		   WHERE id = element.id;
	    -- update reverse offset
            UPDATE core_topology
                   SET "offset" = -"offset"
                   WHERE id = element.topo_object_id;
	ELSE
	    UPDATE core_pathaggregation
		   SET start_position = start_position * ST_Length(updated_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom)),
		       end_position = end_position * ST_Length(updated_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom))
		   WHERE id = element.id;
	END IF;
    END LOOP;
    
    -- update events on merged path
    FOR element IN
        SELECT * FROM core_pathaggregation et
                 JOIN core_topology as evt ON et.topo_object_id=evt.id
                 JOIN core_path as tr on et.path_id = tr.id
        WHERE et.path_id = merged
    LOOP
        IF reverse_merged = TRUE
        THEN
	    UPDATE core_pathaggregation
		   SET start_position = ((1- start_position) * ST_Length(merged_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom))) + (ST_Length(updated_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom))),
		       end_position = ((1- end_position) * ST_Length(merged_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom))) + (ST_Length(updated_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom)))
		   WHERE id = element.id;

            UPDATE core_topology
                   SET "offset" = -"offset"
                   WHERE id = element.topo_object_id;
        ELSE
	    UPDATE core_pathaggregation
		   SET start_position = (start_position * ST_Length(merged_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom))) + (ST_Length(updated_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom))),
		       end_position = (end_position * ST_Length(merged_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom))) + (ST_Length(updated_geom) / (ST_Length(updated_geom) + ST_Length(merged_geom)))
		   WHERE id = element.id;
        END IF;
    END LOOP;
	
    -- fix new geom to updated
    UPDATE core_path
           SET geom = rebuild_line
           WHERE id = updated;
   
    -- Link merged events to updated
    UPDATE core_pathaggregation
           SET path_id = updated
           WHERE path_id = merged;

    -- link element or delete if target unique already present
    FOR element IN SELECT * FROM core_path_networks WHERE path_id = merged
    LOOP
        IF NOT EXISTS (SELECT 1 FROM core_path_networks WHERE network_id=element.network_id AND path_id = updated) THEN
	    UPDATE core_path_networks
		   SET path_id = updated
		   WHERE id = element.id;
        ELSE
            DELETE FROM core_path_networks WHERE path_id = merged;
        END IF;
    END LOOP;

    -- link element or delete if target unique already present
    FOR element IN SELECT * FROM core_path_usages WHERE path_id = merged
    LOOP
        IF NOT EXISTS (SELECT 1 FROM core_path_usages WHERE usage_id=element.usage_id AND path_id = updated) THEN
	    UPDATE core_path_usages
		   SET path_id = updated
		   WHERE id = element.id;
        ELSE
            DELETE FROM core_path_usages WHERE path_id = merged;
        END IF;
    END LOOP;
		   
    
    -- Delete merged Path
    DELETE FROM core_path WHERE id = merged;

    RETURN 1;

END;
$$ LANGUAGE plpgsql;
