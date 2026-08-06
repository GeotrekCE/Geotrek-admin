CREATE FUNCTION {{ schema_geotrek }}.point_to_id(
    point geometry,
    tolerance double precision,
    srid integer
) RETURNS bigint AS
$$
DECLARE
    closest_node record;
    pid bigint;

BEGIN
    EXECUTE
        'SELECT
            ST_Distance(
                geom,
                ST_GeomFromText(ST_AsText(' || quote_literal(point::text) || '),' || srid ||')
            ) AS d,
            id,
            geom
        FROM core_pgroutingnode
        WHERE ST_DWithin(
            geom,
            ST_GeomFromText(ST_AsText(' || quote_literal(point::text) ||'),' || srid || '),
            ' || tolerance ||')
        ORDER BY d
        LIMIT 1'
        INTO closest_node;

    IF closest_node.id IS NOT NULL THEN
        pid := closest_node.id;
    ELSE
        execute 'INSERT INTO core_pgroutingnode (geom) VALUES ('||quote_literal(point::text)||')';
        pid := lastval();
    END IF;

    RETURN pid;
END;
$$ LANGUAGE plpgsql;


CREATE FUNCTION {{ schema_geotrek }}.create_pgrouting_topology(
    srid integer,
    tolerance double precision
) RETURNS void AS
$$
DECLARE
    vertex record;
    vertex_id bigint;
BEGIN

    FOR vertex IN SELECT * FROM pgr_extractVertices(
        'SELECT id, geom
        FROM core_path
        WHERE (source IS NULL OR target IS NULL) AND draft = false AND visible = true
        ORDER BY id'
    ) LOOP

        vertex_id := point_to_id(vertex.geom, tolerance, srid);

        UPDATE core_path as cp
        SET source = vertex_id
        WHERE cp.id = ANY(vertex.out_edges);

        UPDATE core_path as cp
        SET "target" = vertex_id
        WHERE cp.id = ANY(vertex.in_edges);

    END LOOP;

    -- Remove orphaned nodes
    DELETE FROM core_pgroutingnode t
    WHERE NOT EXISTS (
        SELECT 1
        FROM core_path p
        WHERE p.source = t.id OR p.target = t.id
    );

END;
$$ LANGUAGE plpgsql;
