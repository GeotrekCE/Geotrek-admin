CREATE VIEW {# geotrek.zoning #}.v_cities AS (
	SELECT e.*, l.code, l.name
	FROM core_topology AS e, zoning_city AS l
	WHERE deleted = FALSE
);

CREATE VIEW {# geotrek.zoning #}.v_districts AS (
	SELECT e.*, l.name
	FROM core_topology AS e, zoning_district AS l
	WHERE deleted = FALSE
);

CREATE VIEW {# geotrek.zoning #}.v_restrictedareas AS (
	SELECT e.*, l.id AS zonage_id, l.name, b.name AS type
	FROM core_topology AS e, zoning_restrictedareatype AS b, zoning_restrictedarea AS l
	WHERE l.area_type_id = b.id
	AND deleted = FALSE
);
