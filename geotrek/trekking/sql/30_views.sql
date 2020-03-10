DROP VIEW IF EXISTS rando.o_v_itineraire;

CREATE OR REPLACE VIEW rando.v_treks AS (
	SELECT e.geom, i.*
	FROM trekking_trek AS i, core_topology AS e
	WHERE i.topo_object_id = e.id
	AND e.deleted = FALSE
);

DROP VIEW IF EXISTS rando.v_pois;

CREATE OR REPLACE VIEW rando.v_pois AS (
	SELECT e.geom, i.*
	FROM trekking_poi AS i, core_topology AS e
	WHERE i.topo_object_id = e.id
	AND e.deleted = FALSE
);
