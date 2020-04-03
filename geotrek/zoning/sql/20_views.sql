DROP VIEW IF EXISTS f_v_commune;
DROP VIEW IF EXISTS v_cities;
DROP VIEW IF EXISTS f_v_secteur;
DROP VIEW IF EXISTS v_districts;
DROP VIEW IF EXISTS f_v_zonage;
DROP VIEW IF EXISTS v_restrictedareas;

CREATE OR REPLACE VIEW {# geotrek.zoning #}.v_cities AS (
	SELECT e.*, l.code, l.name
	FROM core_topology AS e, zoning_cityedge AS f, zoning_city AS l
	WHERE f.topo_object_id = e.id AND f.city_id = l.code
	AND deleted = FALSE
);

CREATE OR REPLACE VIEW {# geotrek.zoning #}.v_districts AS (
	SELECT e.*, l.name
	FROM core_topology AS e, zoning_districtedge AS f, zoning_district AS l
	WHERE f.topo_object_id = e.id AND f.district_id = l.id
	AND deleted = FALSE
);

CREATE OR REPLACE VIEW {# geotrek.zoning #}.v_restrictedareas AS (
	SELECT e.*, l.id AS zonage_id, l.name, b.name AS type
	FROM core_topology AS e, zoning_restrictedareaedge AS f, zoning_restrictedareatype AS b, zoning_restrictedarea AS l
	WHERE f.topo_object_id = e.id AND f.restricted_area_id = l.id AND l.area_type_id = b.id
	AND deleted = FALSE
);
