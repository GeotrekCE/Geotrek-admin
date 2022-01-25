CREATE OR REPLACE VIEW {# geotrek.trekking #}.v_treks AS (
	SELECT e.geom, e.id, e.uuid, i.*
	FROM trekking_trek AS i, core_topology AS e
	WHERE i.topo_object_id = e.id
	AND e.deleted = FALSE
);

CREATE OR REPLACE VIEW {# geotrek.trekking #}.v_pois AS (
	SELECT e.geom, e.id, e.uuid, i.*
	FROM trekking_poi AS i, core_topology AS e
	WHERE i.topo_object_id = e.id
	AND e.deleted = FALSE
);
