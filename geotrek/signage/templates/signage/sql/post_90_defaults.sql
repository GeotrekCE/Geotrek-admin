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
ALTER TABLE infrastructure_infrastructure ALTER COLUMN description SET DEFAULT '';
-- condition
-- implantation_year
-- eid
ALTER TABLE infrastructure_infrastructure ALTER COLUMN published SET DEFAULT FALSE;
-- publication_date
-- structure
ALTER TABLE infrastructure_infrastructure ALTER COLUMN provider SET DEFAULT '';



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
ALTER TABLE signage_line ALTER COLUMN text SET DEFAULT '';
-- distance
-- pictogram_name
-- time
