-- Sealing
----------
-- label
-- structure
ALTER TABLE signage_sealing ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE signage_sealing ALTER COLUMN date_update SET DEFAULT now();

-- SignageType
--------------
-- label
-- structure
ALTER TABLE signage_signagetype ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE signage_signagetype ALTER COLUMN date_update SET DEFAULT now();

-- Signage
----------
ALTER TABLE signage_signage ALTER COLUMN code SET DEFAULT '';
-- manager
-- sealing
-- access
-- printed_elevation
--type
-- topo_object
-- name
ALTER TABLE signage_signage ALTER COLUMN description SET DEFAULT '';
-- condition
-- implantation_year
-- eid
ALTER TABLE signage_signage ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date
-- structure
ALTER TABLE signage_signage ALTER COLUMN provider SET DEFAULT '';



-- Direction
------------
-- label
ALTER TABLE signage_direction ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE signage_direction ALTER COLUMN date_update SET DEFAULT now();

-- Color
--------
-- label
ALTER TABLE signage_color ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE signage_color ALTER COLUMN date_update SET DEFAULT now();

-- BladeType
------------
-- label
ALTER TABLE signage_bladetype ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE signage_bladetype ALTER COLUMN date_update SET DEFAULT now();

-- Blade
--------
-- signage
-- number
-- direction
-- type
-- color
-- condition
-- topology
ALTER TABLE signage_blade ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE signage_blade ALTER COLUMN date_update SET DEFAULT now();

-- Line
-------
-- blade
-- number
-- direction
ALTER TABLE signage_line ALTER COLUMN text SET DEFAULT '';
-- distance
-- pictogram_name
-- time
