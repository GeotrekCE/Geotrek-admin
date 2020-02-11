DROP VIEW IF EXISTS rando.o_v_itineraire;

CREATE OR REPLACE VIEW rando.o_v_itineraire AS (
	SELECT e.geom, i.*
	FROM trekking_trek AS i, core_topology AS e
	WHERE i.topo_object_id = e.id
	AND e.deleted = FALSE
);

DROP VIEW IF EXISTS rando.o_v_poi;

CREATE OR REPLACE VIEW rando.o_v_poi AS (
	SELECT e.geom, i.*
	FROM trekking_poi AS i, core_topology AS e
	WHERE i.topo_object_id = e.id
	AND e.deleted = FALSE
);
