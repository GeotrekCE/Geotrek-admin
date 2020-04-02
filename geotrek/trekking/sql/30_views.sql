DROP VIEW IF EXISTS o_v_itineraire;
DROP VIEW IF EXISTS v_treks;
DROP VIEW IF EXISTS o_v_poi;
DROP VIEW IF EXISTS v_pois;

CREATE OR REPLACE VIEW {# geotrek.trekking #}.v_treks AS (
	SELECT e.geom, i.*
	FROM trekking_trek AS i, core_topology AS e
	WHERE i.topo_object_id = e.id
	AND e.deleted = FALSE
);

CREATE OR REPLACE VIEW {# geotrek.trekking #}.v_pois AS (
	SELECT e.geom, i.*
	FROM trekking_poi AS i, core_topology AS e
	WHERE i.topo_object_id = e.id
	AND e.deleted = FALSE
);
