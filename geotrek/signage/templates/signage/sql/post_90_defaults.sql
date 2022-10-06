-- Sealing
----------
-- label
-- structure


-- SignageType
--------------
-- label
-- structure


-- Signage
----------
ALTER TABLE signage_signage ALTER COLUMN code SET DEFAULT '';
-- manager
-- sealing
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


-- Color
--------
-- label


-- BladeType
------------
-- label


-- Blade
--------
-- signage
-- number
-- direction
-- type
-- color
-- condition
-- topology


-- Line
-------
-- blade
-- number
-- direction
ALTER TABLE signage_line ALTER COLUMN text SET DEFAULT '';
-- distance
-- pictogram_name
-- time
